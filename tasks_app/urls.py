from django.urls import path
from .views import (
    CurrencyRateListView, UpdateCurrencyRateView, UpdateProductsView, ProductListView, ProductDetailView
)

urlpatterns = [
    path('currencies/', CurrencyRateListView.as_view(), name='currency-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    # for test only!
    path('update_currencies/', UpdateCurrencyRateView.as_view(), name='currency-update'),
    path('update_products/', UpdateProductsView.as_view(), name='products-update'),
]
