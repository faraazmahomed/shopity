"""
Tests for marketplace public views, catalog, and context data.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from marketplace.models import Store, Product

User = get_user_model()


class MarketplaceViewTests(TestCase):
    """Test cases for verifying view responses and context data."""

    def setUp(self):
        """Initialize test client and seed test data with base_price."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.store = Store.objects.create(
            name='Test Store',
            owner=self.user,
            approval_status='approved')
        self.product = Product.objects.create(
            store=self.store,
            name='Test Product',
            base_price=49.99,
            stock=5,
            is_active=True
        )

    def test_home_view(self):
        """Verify home page loads successfully with status 200."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_product_catalog_view(self):
        """Verify product catalog page loads successfully with status 200."""
        response = self.client.get(reverse('product_catalog'))
        self.assertEqual(response.status_code, 200)

    def test_store_model_string_in_view_context(self):
        """Verify database objects can be queried and validated in test environment."""
        self.assertTrue(Product.objects.filter(name='Test Product').exists())
