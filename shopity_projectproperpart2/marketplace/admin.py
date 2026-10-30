"""
Marketplace Admin Registry.

Configures Django administration panels and custom list filters for marketplace entities.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Cart, CartItem, Order, OrderItem, Product, ProductReview, Store

User = get_user_model()


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """Admin configuration for managing vendor stores and approval workflows."""
    list_display = ('name', 'owner', 'approval_status', 'created_at')
    list_filter = ('approval_status', 'created_at')
    search_fields = ('name', 'owner__username', 'approval_status')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for product catalogs and inventory oversight."""
    list_display = ('name', 'store', 'base_price', 'stock', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'store__name')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin configuration for inspecting customer product reviews."""
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for user shopping sessions."""
    list_display = ('user', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for individual cart items."""
    list_display = ('cart', 'product', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for tracking customer order statuses."""
    list_display = ('pk', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for viewing specific line items within orders."""
    list_display = ('order', 'product', 'quantity', 'price')
