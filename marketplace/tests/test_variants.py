"""
Tests for product base attributes, variants, and baseline catalog properties.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Store, Product

User = get_user_model()


class ProductVariantTests(TestCase):
    """Test cases for baseline product attributes required for catalog support."""

    def setUp(self):
        """Set up test user, store, and base product using base_price."""
        self.user = User.objects.create_user(
            username='cataloguser', password='password')
        self.store = Store.objects.create(
            name='Catalog Store',
            owner=self.user,
            approval_status='approved')
        self.product = Product.objects.create(
            store=self.store,
            name='Configurable Product',
            base_price=120.00,
            stock=8,
            is_active=True
        )

    def test_product_base_attributes(self):
        """Verify baseline product attributes required for store inventory."""
        self.assertEqual(self.product.name, 'Configurable Product')
        self.assertEqual(self.product.base_price, 120.00)
        self.assertTrue(self.product.is_active)
