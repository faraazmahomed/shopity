"""
Service layer modules for handling asynchronous tasks, email delivery,
and business logic operations for the marketplace application.
"""

from django.core.mail import send_mail
from django.conf import settings
from .models import EmailQueue


def send_invoice_email_safely(order):
    """
    Send an order confirmation invoice email to the customer securely.
    
    Extracts the customer email and username from the order object,
    attempts to send the email via Django's mail backend, and logs 
    the payload into the EmailQueue if delivery encounters an exception.
    """
    # Support both 'buyer' and 'user' fields defensively
    customer = getattr(order, "buyer", None) or getattr(order, "user", None)
    
    if not customer or not customer.email:
        return  # Skip if no valid recipient email is found

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
