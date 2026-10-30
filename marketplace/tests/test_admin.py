"""
Tests for the marketplace admin configuration and model registrations.
"""
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from marketplace.models import Store, Product, Order
from marketplace.admin import StoreAdmin, ProductAdmin, OrderAdmin

class MarketplaceAdminTests(TestCase):
    """Test cases for verifying admin class display and search attributes."""

    def setUp(self):
        """Initialize admin site instance for testing."""
        self.site = AdminSite()

    def test_store_admin_configuration(self):
        """Verify StoreAdmin search fields include name and owner username."""
        admin_obj = StoreAdmin(Store, self.site)
        self.assertIn('name', admin_obj.search_fields)
        self.assertIn('owner__username', admin_obj.search_fields)

    def test_product_admin_configuration(self):
        """Verify ProductAdmin search fields include product name."""
        admin_obj = ProductAdmin(Product, self.site)
        self.assertIn('name', admin_obj.search_fields)

    def test_order_admin_configuration(self):
        """Verify OrderAdmin list display fields include order status."""
        admin_obj = OrderAdmin(Order, self.site)
        self.assertIn('status', admin_obj.list_display)
