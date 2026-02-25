from django.urls import path
from .views import (
    CurrencyRateListView,
    UpdateCurrencyRateView,
    UpdateProductsView,
    ProductListView,
    ProductDetailView,
    ProductPriceRangeView,
    ShopTodayAveragePriceView,
    PriceHistoryChartView,
    ProductPriceAlertCreateView
)

urlpatterns = [
    path('currencies/', CurrencyRateListView.as_view(), name='currency-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/price-range/', ProductPriceRangeView.as_view(), name='product-price-range'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('shops/average-today-prices/', ShopTodayAveragePriceView.as_view(), name='average-today-prices'),
    path('shops/price-chart/', PriceHistoryChartView.as_view(), name='price-chart'),
    path('alerts/', ProductPriceAlertCreateView.as_view(), name='create-alert'),
    # for test only!
    path('update_currencies/', UpdateCurrencyRateView.as_view(), name='currency-update'),
    path('update_products/', UpdateProductsView.as_view(), name='products-update'),
]
