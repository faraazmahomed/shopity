"""Utility helpers for email dispatch and vendor group permissions."""

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail

from .models import EmailQueue, Product


def ensure_vendor_group_permissions():
    """Assign Product CRUD permissions to the Vendors group."""
    vendor_group, _ = Group.objects.get_or_create(
        name="Vendors"
    )
    content_type = ContentType.objects.get_for_model(Product)
    codenames = [
        "add_product",
        "change_product",
        "delete_product",
    ]
    permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=codenames,
    )
    vendor_group.permissions.add(*permissions)
    return vendor_group


def send_invoice_email_safely(order):
    """Send an order confirmation invoice email to the buyer.

    Queues a pending EmailQueue entry if sending raises an error.
    """
    customer = (
        getattr(order, "buyer", None)
        or getattr(order, "user", None)
    )

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
