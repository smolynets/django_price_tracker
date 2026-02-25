from django.db.models import Min, Max, OuterRef, Subquery, Avg, F
from rest_framework import generics
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response

from .external_apis.nbu_currency import get_rates
from .external_apis.get_products import get_product_prices
from .models import CurrencyRate, Product, ProductPriceRecord, Shop, ProductPriceAlert
from .serializers import (
    CurrencyRateSerializer, ProductSerializer, ShopAveragePriceSerializer, ProductPriceAlertSerializer
)


@extend_schema_view(
    get=extend_schema(tags=['Currencies'])
)
class CurrencyRateListView(generics.ListAPIView):
    """
    API endpoint that allows currency rates to be viewed.
    """
    queryset = CurrencyRate.objects.all().order_by('-created_at')
    serializer_class = CurrencyRateSerializer


@extend_schema_view(
    get=extend_schema(
        tags=['Products'],
        summary="Get a list of products with currency conversion",
        parameters=[
            OpenApiParameter(
                name='currency',
                description='Currency code (UAH, USD)',
                required=False,
                type=str,
                enum=['USD', 'UAH'],
                default='USD'
            ),
            OpenApiParameter(
                name='ordering',
                description='Sort by price',
                required=False,
                type=str,
                enum=['price', '-price', 'trend', '-trend'],
            )
        ]
    )
)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency'] = self.request.query_params.get('currency', 'USD')
        return context

    def get_queryset(self):
        """
        Prepares a queryset of products with annotated current price and 30-day trend.
        
        This method performs the following:
        1. Subqueries the latest price from ProductPriceRecord for each product.
        2. Calculates the average price over the last 30 days using a subquery.
        3. Annotates each product with 'latest_price' and 'price_trend' (current - average).
        4. Handles dynamic sorting based on 'ordering' parameter:
        - 'price'/'-price': Sorts by the current actual price.
        - 'trend'/'-trend': Sorts by price volatility (growth or drop magnitude).
        5. Defaults to sorting by creation date.
        """
        # Subquery to fetch the single most recent price
        latest_price = ProductPriceRecord.objects.filter(
            product=OuterRef('pk')
        ).order_by('-date').values('price')[:1]
        # Subquery to calculate average price for the last 30 days
        last_month = timezone.now().date() - timedelta(days=30)
        avg_price = ProductPriceRecord.objects.filter(
            product=OuterRef('pk'),
            date__gte=last_month
        ).values('product').annotate(avg=Avg('price')).values('avg')
        # Combine subqueries and calculate the trend as a virtual field
        queryset = Product.objects.annotate(
            latest_price=Subquery(latest_price),
            avg_price_30d=Subquery(avg_price)
        ).annotate(
            price_trend=F('latest_price') - F('avg_price_30d')
        ).prefetch_related('price')
        ordering = self.request.query_params.get('ordering')
        # Unified sorting logic for price and trend fields
        if ordering in ('price', '-price', 'trend', '-trend'):
            direction = '-' if ordering.startswith('-') else ''
            field_map = {
                'price': 'latest_price',
                'trend': 'price_trend'
            }
            clean_name = ordering.lstrip('-')
            target_field = field_map[clean_name]
            queryset = queryset.order_by(f'{direction}{target_field}')
        else:
            queryset = queryset.order_by('-created_at')
        return queryset


class ProductPriceRangeView(APIView):
    @extend_schema(
        tags=['Products'],
        summary="Get min and max product prices",
        parameters=[
            OpenApiParameter(name='currency', type=str, enum=['USD', 'UAH'], default='USD')
        ],
        responses={200: {
            "type": "object",
            "properties": {
                "min_price": {"type": "number", "format": "decimal", "example": 10.50},
                "max_price": {"type": "number", "format": "decimal", "example": 500.00},
                "currency": {"type": "string", "example": "UAH"}
            }
        }}
    )
    def get(self, request):
        currency = request.query_params.get('currency', 'USD').upper()
        latest_price_subquery = ProductPriceRecord.objects.filter(
            product=OuterRef('pk')
        ).order_by('-date').values('price')[:1]
        stats = Product.objects.annotate(
            ann_current_price=Subquery(latest_price_subquery)
        ).aggregate(
            min_val=Min('ann_current_price'),
            max_val=Max('ann_current_price')
        )
        min_p = Decimal(str(stats['min_val'] or 0))
        max_p = Decimal(str(stats['max_val'] or 0))
        if currency == 'UAH':
            rate_obj = CurrencyRate.objects.filter(title="USD").order_by('-created_at').first()
            if rate_obj:
                rate = rate_obj.rate
                min_p = (min_p * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                max_p = (max_p * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            min_p = min_p.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            max_p = max_p.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Response({
            "min_price": min_p,
            "max_price": max_p,
            "currency": currency
        })


@extend_schema_view(
    get=extend_schema(
        tags=['Products'], 
        summary="Get a single product by ID",
        parameters=[
            OpenApiParameter(
                name='currency',
                description='Currency code (UAH, USD)',
                required=False,
                type=str,
                enum=['USD', 'UAH'],
                default='USD'
            )
        ]
    )
)
class ProductDetailView(generics.RetrieveAPIView):
    """
    API endpoint that returns a single product identified by its ID.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency'] = self.request.query_params.get('currency', 'USD')
        return context


class ShopTodayAveragePriceView(APIView):
    def get(self, request):
        today = timezone.now().date()
        shops_data = Shop.objects.filter(
            product__price__date=today
        ).annotate(
            average_price=Avg('product__price__price')
        ).values('title', 'average_price')
        serializer = ShopAveragePriceSerializer(shops_data, many=True)
        return Response(serializer.data)


class TodayPriceChartView(APIView):
    @extend_schema(
        summary="Get today's price statistics",
        description="Returns the average price per shop and the overall market average for the current day."
    )
    def get(self, request):
        """
        Retrieves today's price statistics by calculating the average price 
        per shop and the overall market average across all shops.
        """
        today = timezone.now().date()
        today_records = ProductPriceRecord.objects.filter(date=today)
        shop_history = []
        shops = Shop.objects.all()
        for shop in shops:
            # Calculate average for this shop for today
            history = (
                today_records.filter(product__shop=shop)
                .values('date')
                .annotate(avg_price=Avg('price'))
            )
            avg_val = history[0]['avg_price'] if history.exists() else None
            shop_history.append({
                "title": shop.title,
                "data": [{"date": today, "price": avg_val}]
            })
        # Overall average price across ALL shops for today
        overall_history = (
            today_records.values('date')
            .annotate(avg_price=Avg('price'))
        )
        overall_avg_val = overall_history[0]['avg_price'] if overall_history.exists() else None
        overall_data = [
            {"date": today, "price": overall_avg_val}
        ]
        return Response({
            "date": today,
            "shops": shop_history,
            "overall_average": overall_data
        })


class ProductPriceAlertCreateView(generics.CreateAPIView):
    queryset = ProductPriceAlert.objects.all()
    serializer_class = ProductPriceAlertSerializer

    @extend_schema(
        summary="Add new price alert",
        description="Creates a notification trigger for a specific product and email.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# for test only!
@extend_schema_view(
    get=extend_schema(tags=['Test'])
)
class UpdateCurrencyRateView(APIView):
    def get(self, request):
        get_rates() # for test
        return Response({"message": "Hello! The task API is working."})


@extend_schema_view(
    get=extend_schema(tags=['Test'])
)
class UpdateProductsView(APIView):
    def get(self, request):
        get_product_prices() # for test
        return Response({"message": "Hello! The task API is working."})
