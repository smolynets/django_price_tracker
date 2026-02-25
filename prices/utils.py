import logging

from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import ProductPriceAlert


logger = logging.getLogger(__name__)

def process_price_alerts():
    """
    Identifies products where the current price has dropped below the threshold_price
    and sends email notifications to subscribed users.
    """
    today = timezone.now().date()
    # We take ALL alerts from the database, 
    # but exclude those that have already sent a notification today.
    alerts = ProductPriceAlert.objects.exclude(
        last_notification_date=today
    ).select_related('product', 'product__shop')
    for alert in alerts:
        current_price = alert.product.current_price
        # Check if the price is low enough and exists
        print(current_price)
        print(alert.threshold_price)
        print(alert.product)
        if current_price is not None and current_price <= alert.threshold_price:
            subject = f"Price Drop Alert: {alert.product.title}"
            message = (
                f"Good news! The price for '{alert.product.title}' has dropped to {current_price}.\n"
                f"Your threshold price was: {alert.threshold_price}.\n\n"
                f"Shop: {alert.product.shop.title}\n"
                f"Link: {alert.product.shop.url}"
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[alert.email],
                    fail_silently=False,
                )
                alert.last_notification_date = today
                alert.save()
                logger.info("Email sended")
            except Exception as e:
                print(f"Error sending email to {alert.email}: {e}")
