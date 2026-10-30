"""
Tests for core marketplace models including stores, products, reviews, and carts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Store, Product, Cart, CartItem, Order, OrderItem, ProductReview

User = get_user_model()

class MarketplaceModelTests(TestCase):
    """Test cases for core model creation, fields, and relationships."""

    def setUp(self):
        """Create baseline user, store, and product instances using base_price."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.store = Store.objects.create(name='Test Store', owner=self.user, approval_status='approved')
        self.product = Product.objects.create(
            store=self.store,
            name='Test Product',
            base_price=99.99,
            stock=10,
            is_active=True
        )

    def test_store_creation(self):
        """Verify store string representation and owner attribution."""
        self.assertEqual(str(self.store), 'Test Store')
        self.assertEqual(self.store.owner, self.user)

    def test_product_creation(self):
        """Verify product attributes, base_price, and store foreign key relationship."""
        self.assertEqual(str(self.product), 'Test Product')
        self.assertEqual(self.product.base_price, 99.99)
        self.assertEqual(self.product.store, self.store)

    def test_product_review_creation(self):
        """Verify customer product reviews and ratings."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Great product!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user, self.user)

    def test_cart_and_order_creation(self):
        """Verify cart, cart items, and order lifecycle models."""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.assertEqual(cart_item.quantity, 2)

        order = Order.objects.create(user=self.user, status='pending')
        order_item = OrderItem.objects.create(order=order, product=self.product, quantity=2, price=99.99)
        self.assertEqual(order_item.price, 99.99)
