"""Tests for core marketplace models and relationships."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from marketplace.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Product,
    ProductReview,
    Store,
)

User = get_user_model()


class MarketplaceModelTests(TestCase):
    """Test cases for core model creation and relationships."""

    def setUp(self):
        """Create baseline user, store, and product instances."""
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.store = Store.objects.create(
            name="Test Store", owner=self.user
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Test Product",
            base_price=99.99,
            stock=10,
            is_active=True,
        )

    def test_store_creation(self):
        """Verify store string representation and ownership."""
        self.assertEqual(str(self.store), "Test Store")
        self.assertEqual(self.store.owner, self.user)

    def test_product_creation(self):
        """Verify product attributes and store relationship."""
        self.assertEqual(str(self.product), "Test Product")
        self.assertEqual(float(self.product.base_price), 99.99)
        self.assertEqual(self.product.store, self.store)

    def test_product_review_creation(self):
        """Verify customer product reviews and ratings."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great product!",
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user, self.user)

    def test_cart_and_order_creation(self):
        """Verify cart, cart items, and order lifecycle models."""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart, product=self.product, quantity=2
        )
        self.assertEqual(cart_item.quantity, 2)

        order = Order.objects.create(
            user=self.user, status="pending"
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=99.99,
        )
        self.assertEqual(float(order_item.price), 99.99)
