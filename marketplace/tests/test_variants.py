"""
Tests for product variants and attributes.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from marketplace.models import Store, Product

User = get_user_model()


class ProductVariantTests(TestCase):
    """Test cases for managing and validating product
    variants and attributes.
    """

    def setUp(self):
        """Initialize test client and seed data."""
        self.client = Client()
        self.user = User.objects.create_user(username="testvendor", password="password")
        self.store = Store.objects.create(name="Variant Store", owner=self.user)
        self.product = Product.objects.create(
            store=self.store,
            name="Base Product",
            base_price=19.99,
            stock=15,
            is_active=True,
        )

    def test_product_creation(self):
        """Verify base product properties are saved correctly."""
        self.assertEqual(self.product.base_price, 19.99)
        self.assertTrue(self.product.is_active)
