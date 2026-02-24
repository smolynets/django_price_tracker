from django.contrib import admin

from .models import CurrencyRate, Product, ProductPriceRecord, Shop

admin.site.register(CurrencyRate)
admin.site.register(Product)
admin.site.register(ProductPriceRecord)
admin.site.register(Shop)
