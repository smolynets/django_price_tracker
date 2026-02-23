from rest_framework import generics
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response

from .external_apis.nbu_currency import get_rates
from .external_apis.get_products import get_product_prices
from .models import CurrencyRate, Product
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
            )
        ]
    )
)
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['currency'] = self.request.query_params.get('currency', 'USD')
        return context


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
