import requests
from decimal import Decimal
from django.utils import timezone

URL = "https://dummyjson.com/products"

def get_product_prices():
    """
    Fetches products from the API and updates both Product and its Price history.
    """
    from prices.models import Product, ProductPriceRecord
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
        products_data = data.get("products", [])
        for item in products_data:
            current_price = Decimal(str(item.get('price', 0)))
            product_obj, created = Product.objects.update_or_create(
                external_id=item['id'],
                defaults={
                    'title': item.get('title'),
                    'description': item.get('description'),
                }
            )
            ProductPriceRecord.objects.update_or_create(
                product=product_obj,
                date=timezone.now().date(),
                defaults={'price': current_price}
            )
        print(f"Successfully synced {len(products_data)} products and prices.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
