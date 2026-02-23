from django.urls import path
from .views import CurrencyRateListView, UpdateCurrencyRateView

urlpatterns = [
    path('currencies/', CurrencyRateListView.as_view(), name='currency-list'),
    path('update_currencies/', UpdateCurrencyRateView.as_view(), name='currency-update'),
]