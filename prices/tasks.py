from celery import shared_task
import logging

from .external_apis.nbu_currency import get_rates
from .external_apis.get_products import get_product_prices
from .utils import process_price_alerts


logger = logging.getLogger(__name__)

@shared_task
def run_daily_logic():
    get_rates()
    logger.info("Currency rates retrieved")
    get_product_prices()
    logger.info("Products rates retrieved")
    process_price_alerts()
    logger.info("Alerts checked")
