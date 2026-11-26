"""Tests for product variants and attributes."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from marketplace.models import Product, Store

User = get_user_model()


class ProductVariantTests(TestCase):
    """Test cases for product attributes and variant data."""

    def setUp(self):
        """Initialize test client and seed product data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testvendor", password="password"
        )
        self.store = Store.objects.create(
            name="Variant Store", owner=self.user
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Base Product",
            base_price=Decimal("19.99"),
            stock=15,
            is_active=True,
        )

    def test_product_creation(self):
        """Verify base product properties are saved properly."""
        self.assertEqual(self.product.base_price, Decimal("19.99"))
        self.assertEqual(self.product.stock, 15)
        self.assertTrue(self.product.is_active)
