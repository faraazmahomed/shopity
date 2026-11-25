"""Tests for marketplace admin configuration and registrations."""

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from marketplace.admin import OrderAdmin, ProductAdmin, StoreAdmin
from marketplace.models import Order, Product, Store


class MarketplaceAdminTests(TestCase):
    """Test cases for verifying admin display and search fields."""

    def setUp(self):
        """Initialize admin site instance for testing."""
        self.site = AdminSite()

    def test_store_admin_configuration(self):
        """Verify StoreAdmin search fields include name and owner."""
        admin_obj = StoreAdmin(Store, self.site)
        self.assertIn("name", admin_obj.search_fields)
        self.assertIn(
            "owner__username", admin_obj.search_fields
        )

    def test_product_admin_configuration(self):
        """Verify ProductAdmin search fields include product name."""
        admin_obj = ProductAdmin(Product, self.site)
        self.assertIn("name", admin_obj.search_fields)

    def test_order_admin_configuration(self):
        """Verify OrderAdmin list display includes order status."""
        admin_obj = OrderAdmin(Order, self.site)
        self.assertIn("status", admin_obj.list_display)
