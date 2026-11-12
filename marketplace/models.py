"""
Marketplace Domain Models.

Defines the relational data structures for vendor storefronts, product catalogs,
customer reviews, shopping carts, and order processing workflows.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta
import hashlib
import secrets


class Store(models.Model):
    """
    Represents a merchant storefront managed by a registered user.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stores'
    )
    approval_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Represents an individual item listed within a vendor's store catalog.
    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    """Stores customer feedback ratings and written comments for specific products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


class Cart(models.Model):
    """Active shopping session container holding selected items for a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    """Individual line item connecting a shopping cart to a specific product and quantity."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    """Represents a finalized customer checkout transaction and order lifecycle."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    """Historical snapshot of a product purchased within a specific order, including tracking fields."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Tracking Subsystem Fields
    item_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('SHIPPED', 'Shipped'),
            ('DELIVERED', 'Delivered'),
            ('CANCELLED', 'Cancelled'),
            ('DISPUTED', 'Disputed')
        ],
        default='PROCESSING'
    )
    carrier_name = models.CharField(max_length=50, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.pk})"


class ResetToken(models.Model):
    """Stores secure time-limited tokens for forgotten password recovery."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reset_tokens'
    )
    token_hash = models.CharField(max_length=64)
    expiry_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_token(cls, user):
        # Invalidate any existing unused tokens for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        expiry_at = timezone.now() + timedelta(hours=1) # Valid for 1 hour
        
        cls.objects.create(
            user=user,
            token_hash=token_hash,
            expiry_at=expiry_at
        )
        return raw_token

    def __str__(self):
        return f"Reset Token for {self.user.username}"
