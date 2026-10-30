"""
Tests for customer product reviews, ratings, and validation logic.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Store, Product, ProductReview

User = get_user_model()

class ProductReviewTests(TestCase):
    """Test cases for verifying product review creation and constraints."""

    def setUp(self):
        """Set up test user, approved store, and product using base_price."""
        self.user = User.objects.create_user(username='reviewer', password='password')
        self.store = Store.objects.create(name='Review Store', owner=self.user, approval_status='approved')
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
            comment='Good quality item.'
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
