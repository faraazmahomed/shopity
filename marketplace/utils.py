"""
Utility functions and helper tasks for the marketplace application,
including safe email dispatch and error queueing.
"""

from django.core.mail import send_mail
from django.conf import settings
from .models import EmailQueue


def send_invoice_email_safely(order):
    """
    Send an order confirmation invoice email to the buyer.

    If the email delivery fails due to an exception, catches the error
    and creates a pending record in the EmailQueue for later retry.
    """
    customer = getattr(order, "buyer", None) or getattr(order, "user", None)

    if not customer or not customer.email:
        return

    recipient = customer.email
    username = customer.username

    subject = f"Order Invoice #{order.id} Confirmation"
    body = (
        f"Hello {username},\n\n"
        f"Thank you for your purchase!\n"
        f"Order ID: #{order.id}\n"
        f"Total Amount: ${order.total_amount}\n\n"
        f"We will notify you once your items are shipped."
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception as exc:
        EmailQueue.objects.create(
            recipient_email=recipient,
            subject=subject,
            body_text=body,
            status=EmailQueue.Status.PENDING,
            error_log=str(exc),
        )
