import requests

from tasks_app.models import Product

url = "https://dummyjson.com/products"

def get_product_prices():
    """
    Fetches products from the API and prints titles and prices.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        for product in products:
            Product.objects.update_or_create(
                external_id=product['id'],
                defaults={
                    'title': product['title'],
                    'description': product['description'],
                    'price': product['price'],
                }
            )
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
