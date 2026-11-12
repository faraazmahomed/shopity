"""
Tests for customer product reviews, ratings, and verification logic.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Store, Product, ProductReview, Order, OrderItem

User = get_user_model()


class ProductReviewTests(TestCase):
    """Test cases for verifying product review creation, ratings, and verification constraints."""

    def setUp(self):
        """Set up test user, approved store, and product using base_price."""
        self.user = User.objects.create_user(username='reviewer', password='password')
        self.store = Store.objects.create(
            name='Review Store',
            owner=self.user,
            approval_status='approved')
        self.product = Product.objects.create(
            store=self.store,
            name='Reviewed Item',
            base_price=29.99,
            stock=15,
            is_active=True
        )

    def test_valid_review_creation(self):
        """Verify creating a review with a valid rating (1-5)."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment='Good quality item.',
            is_verified=False
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertFalse(review.is_verified)

    def test_verified_review_status(self):
        """Verify that a review linked to an existing order item is marked as verified."""
        order = Order.objects.create(user=self.user, status='completed')
        order_item = OrderItem.objects.create(
            order=order, product=self.product, quantity=1, price=29.99)

        # Simulate view-level logic checking for an existing OrderItem
        has_purchased = OrderItem.objects.filter(
            order__user=self.user, product=self.product).exists()

        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Bought and tested, works wonderfully!',
            is_verified=has_purchased
        )

        self.assertTrue(review.is_verified)
