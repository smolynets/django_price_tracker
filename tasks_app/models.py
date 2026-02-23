from django.db import models

class CurrencyRate(models.Model):
    title = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    rate_date = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.rate} ({self.created_at})"
