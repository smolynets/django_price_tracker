from django.contrib import admin

from .models import CurrencyRate, Product, ProductPriceRecord, Shop, ProductPriceAlert

admin.site.register(CurrencyRate)
admin.site.register(Product)
admin.site.register(ProductPriceRecord)
admin.site.register(Shop)

@admin.register(ProductPriceAlert)
class ProductPriceAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'threshold_price', 'email', 'last_notification_date')
    list_filter = ('last_notification_date', 'product__shop')
    search_fields = ('email', 'product__title')
    exclude = ('last_notification_date', 'created_at')
