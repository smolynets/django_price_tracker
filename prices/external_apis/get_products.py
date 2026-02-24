import requests
from decimal import Decimal
from django.utils import timezone

def get_product_prices():
    """
    English comment:
    Iterates through the shops dictionary, fetches data from each API,
    and syncs products and prices linked to the specific shop.
    """
    from prices.models import Shop, Product, ProductPriceRecord

    shops = {
        "dummyjson": "https://dummyjson.com/products",
        "fakestoreapi": "https://fakestoreapi.com/products"
    }
    for shop_title, url in shops.items():
        try:
            shop_obj, _ = Shop.objects.get_or_create(
                title=shop_title,
                defaults={'url': url}
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            products_data = data.get("products", data) if isinstance(data, dict) else data
            for item in products_data:
                current_price = Decimal(str(item.get('price', 0)))
                product_obj, created = Product.objects.update_or_create(
                    external_id=item['id'],
                    shop=shop_obj,
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
            print(f"Successfully synced {len(products_data)} products from {shop_title}.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {shop_title}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while syncing {shop_title}: {e}")
