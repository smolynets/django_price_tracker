import requests
from datetime import datetime

URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

def get_rates():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    rates = {}
    for currency in data:
        if currency["cc"] in ("USD", "EUR"):
            rates[currency["cc"]] = {
                "rate": currency["rate"],
                "date": currency["exchangedate"]
            }
    import pdb;pdb.set_trace()

    return rates

if __name__ == "__main__":
    rates = get_rates()

    print("Офіційний курс НБУ:")
    for code in ("USD", "EUR"):
        if code in rates:
            print(f"{code}: {rates[code]['rate']} грн (дата: {rates[code]['date']})")
        else:
            print(f"{code}: не знайдено")