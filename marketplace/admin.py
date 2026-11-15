"""
Admin configurations for the Marketplace application.
"""

from django.contrib import admin
from .models import (
    Store,
    Product,
    ProductReview,
    Cart,
    CartItem,
    Order,
    OrderItem,
    ResetToken,
)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "owner__username")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "base_price", "stock", "is_active")
    list_filter = ("is_active", "store")
    search_fields = ("name", "description")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_verified", "created_at")
    list_filter = ("rating", "is_verified")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "status", "created_at")
    list_filter = ("status",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "item_status")
    list_filter = ("item_status",)


@admin.register(ResetToken)
class ResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expiry_at", "is_used", "created_at")
    list_filter = ("is_used",)
