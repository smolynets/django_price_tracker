import requests
from datetime import datetime

from tasks_app.models import CurrencyRate

URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

def get_rates():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    rates = {}
    for currency in data:
        if currency["cc"] in ("USD", "EUR"):
            CurrencyRate.objects.update_or_create(
                title=currency["cc"],
                rate_date=currency['exchangedate'],
                defaults={'rate': currency["rate"]}
            )

    return rates
