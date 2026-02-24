from django.db.models import Min, Max, OuterRef, Subquery, Avg, F
from rest_framework import generics
from decimal import Decimal, ROUND_HALF_UP
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response

from .external_apis.nbu_currency import get_rates
from .external_apis.get_products import get_product_prices
from .models import CurrencyRate, Product, ProductPriceRecord
from .serializers import CurrencyRateSerializer, ProductSerializer


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
                enum=['price', '-price'],
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
        latest_price = ProductPriceRecord.objects.filter(
            product=OuterRef('pk')
        ).order_by('-date').values('price')[:1]
        queryset = Product.objects.annotate(
            latest_price=Subquery(latest_price)
        ).prefetch_related('price')
        ordering = self.request.query_params.get('ordering')
        if ordering in ('price', '-price'):
            direction = '-' if ordering.startswith('-') else ''
            queryset = queryset.order_by(f'{direction}latest_price')
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
