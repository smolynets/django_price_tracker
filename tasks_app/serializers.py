from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import CurrencyRate, Product

class CurrencyRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CurrencyRate
        fields = ['id', 'title', 'rate', 'rate_date', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    currency_code = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'external_id', 'title', 'description', 'price', 'currency_code', 'created_at']

    def _get_validated_currency(self):
        """
        Internal helper to validate currency from context.
        """
        currency = self.context.get('currency')
        if not currency:
            return 'USD'
        currency = str(currency).upper()
        allowed = ['USD', 'UAH']
        if currency not in allowed:
            raise ValidationError(f"Invalid currency '{currency}'. Supported: {allowed}")
            
        return currency

    def get_price(self, obj):
        target_currency = self._get_validated_currency()
        if target_currency == 'USD':
            return obj.price
        if target_currency == 'UAH':
            rate_obj = CurrencyRate.objects.filter(title="USD").order_by('-created_at').first()
            if rate_obj:
                result = rate_obj.rate * obj.price
                return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return obj.price

    def get_currency_code(self, obj):
        return self._get_validated_currency()
