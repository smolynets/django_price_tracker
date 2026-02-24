from django.db import models
from django.utils import timezone

class CurrencyRate(models.Model):
    title = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    rate_date = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.rate} ({self.created_at})"


class Product(models.Model):
    external_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def current_price(self):
        latest_record = self.price.first()
        return latest_record.price if latest_record else None

class ProductPriceRecord(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='price'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('product', 'date')
        ordering = ['-date']
