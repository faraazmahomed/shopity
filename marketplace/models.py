"""Marketplace Domain Models.

Defines relational models for storefronts, products, reviews,
shopping carts, orders, email queue entries, and reset tokens.
"""

from datetime import timedelta
import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone


class Store(models.Model):
    """Merchant storefront managed by a registered user."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stores",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the store name."""
        return self.name


class Product(models.Model):
    """Item listed within a vendor store catalog."""

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to="products/", blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def available_stock(self):
        """Return stock minus quantities in active/pending orders."""
        reserved = (
            self.orderitem_set.exclude(
                order__status__iexact="cancelled"
            )
            .exclude(item_status__iexact="cancelled")
            .exclude(order__status__iexact="completed")
            .exclude(item_status__iexact="delivered")
            .aggregate(total=Coalesce(Sum("quantity"), 0))
            .get("total", 0)
        )
        return max(self.stock - reserved, 0)

    def __str__(self):
        """Return the product name."""
        return self.name


class ProductReview(models.Model):
    """Customer feedback ratings and written comments."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5,
    )
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return summary string with reviewer and rating."""
        return (
            f"{self.user.username} - "
            f"{self.product.name} ({self.rating}★)"
        )


class Cart(models.Model):
    """Active shopping session container for a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return cart label for the owning user."""
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    """Individual line item in a shopping cart."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        """Return quantity and product name."""
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    """Customer checkout transaction and order lifecycle."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return order ID and buyer username."""
        return f"Order #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    """Historical snapshot of a purchased product."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    item_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("SHIPPED", "Shipped"),
            ("DELIVERED", "Delivered"),
            ("CANCELLED", "Cancelled"),
            ("DISPUTED", "Disputed"),
        ],
        default="PROCESSING",
    )
    carrier_name = models.CharField(
        max_length=50, blank=True, null=True
    )
    tracking_number = models.CharField(
        max_length=100, blank=True, null=True
    )

    def __str__(self):
        """Return item quantity, product, and order ID."""
        return (
            f"{self.quantity} x {self.product.name} "
            f"(Order #{self.order.pk})"
        )


class EmailQueue(models.Model):
    """Queue for sending asynchronous email notifications."""

    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return recipient and email subject."""
        return (
            f"Email to {self.to_email}: {self.subject}"
        )


class ResetToken(models.Model):
    """Time-limited tokens for password recovery."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reset_tokens",
    )
    token_hash = models.CharField(max_length=64)
    expiry_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_token(cls, user):
        """Invalidate prior tokens and create a new token."""
        cls.objects.filter(
            user=user, is_used=False
        ).update(is_used=True)

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()
        expiry_at = timezone.now() + timedelta(hours=1)

        cls.objects.create(
            user=user,
            token_hash=token_hash,
            expiry_at=expiry_at,
        )
        return raw_token

    def __str__(self):
        """Return token label for the target user."""
        return f"Reset Token for {self.user.username}"
