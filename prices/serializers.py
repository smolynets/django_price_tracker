from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from django.utils import timezone
from datetime import timedelta

from .models import CurrencyRate, Product, ProductPriceAlert

class CurrencyRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CurrencyRate
        fields = ['id', 'title', 'rate', 'rate_date', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    shop = serializers.ReadOnlyField(source='shop.title')
    price = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'external_id', 'title', 'description', 'price', 'trend', 'shop']

    def _get_validated_currency(self):
        return self.context.get('currency', 'USD').upper()

    def get_price(self, obj):
        target_currency = self._get_validated_currency()
        base_price = obj.current_price
        
        if base_price is None:
            return None

        if target_currency == 'UAH':
            rate_obj = CurrencyRate.objects.filter(title="USD").order_by('-created_at').first()
            if rate_obj:
                result = rate_obj.rate * base_price
                return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return base_price

    def get_trend(self, obj):
        last_month = timezone.now().date() - timedelta(days=30)
        avg_price_data = obj.price.filter(
            date__gte=last_month
        ).aggregate(avg=Avg('price'))
        avg_price = avg_price_data['avg']
        current_price = obj.current_price
        avg_price = Decimal(str(avg_price))
        threshold = avg_price * Decimal('0.01')
        if current_price > (avg_price + threshold):
            return "up"
        elif current_price < (avg_price - threshold):
            return "down"
        return "no"

    def get_currency_code(self, obj):
        return self._get_validated_currency()


class ShopAveragePriceSerializer(serializers.Serializer):
    title = serializers.CharField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class ProductPriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceAlert
        fields = ['product', 'threshold_price', 'email']

        validators = [
            UniqueTogetherValidator(
                queryset=ProductPriceAlert.objects.all(),
                fields=['product', 'email'],
                message="You already have an active alert for this product."
            )
        ]
        
    def validate_threshold_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
