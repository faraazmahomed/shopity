"""
Marketplace Domain Models.

Defines the relational data structures for vendor storefronts, product catalogs,
customer reviews, shopping carts, and order processing workflows.
"""

from django.conf import settings
from django.db import models


class Store(models.Model):
    """
    Represents a merchant storefront managed by a registered user.
    
    Attributes:
        name (CharField): Unique display name of the vendor store.
        description (TextField): Detailed overview or biography of the store.
        owner (ForeignKey): User account that owns and manages the store.
        approval_status (CharField): Admin verification status ('pending', 'approved', 'rejected').
        created_at (DateTimeField): Timestamp when the store was registered.
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
    image = models.ImageField(upload_to='stores/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the store name representation."""
        return self.name


class Product(models.Model):
    """
    Represents an individual item listed within a vendor's store catalog.
    
    Attributes:
        store (ForeignKey): The parent Store offering this product.
        name (CharField): Title of the product.
        description (TextField): Full specification or marketing description.
        base_price (DecimalField): Unit pricing for the product.
        stock (PositiveIntegerField): Available inventory count.
        image (ImageField): Primary promotional or catalog image.
        is_active (BooleanField): Availability toggle for storefront listing.
        created_at (DateTimeField): Timestamp of product creation.
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
        """Return the product name representation."""
        return self.name


class ProductReview(models.Model):
    """
    Stores customer feedback ratings and written comments for specific products.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a descriptive string combining reviewer, product, and rating."""
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


class Cart(models.Model):
    """
    Active shopping session container holding selected items for a user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return user association string for the shopping cart."""
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    """
    Individual line item connecting a shopping cart to a specific product and quantity.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        """Return quantity and product name representation."""
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    """
    Represents a finalized customer checkout transaction and order lifecycle.
    """
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
        """Return order identifier and customer username."""
        return f"Order #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    """
    Historical snapshot of a product purchased within a specific order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        """Return quantity, product name, and parent order reference."""
        return f"{self.quantity} x {self.product.name} (Order #{self.order.pk})"
