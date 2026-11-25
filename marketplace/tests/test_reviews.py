"""Tests for marketplace product reviews and verification."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from marketplace.models import (
    Order,
    OrderItem,
    Product,
    ProductReview,
    Store,
)

User = get_user_model()


class ProductReviewTests(TestCase):
    """Test cases for creating and verifying product reviews."""

    def setUp(self):
        """Initialize client, users, store, product, and order."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="buyeruser", password="password"
        )
        self.vendor = User.objects.create_user(
            username="vendoruser", password="password"
        )
        self.store = Store.objects.create(
            name="Review Store", owner=self.vendor
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Review Product",
            base_price=29.99,
            stock=10,
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user, status="COMPLETED"
        )
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=29.99,
            item_status="DELIVERED",
        )
        self.assertIsNotNone(order_item.pk)

    def test_verified_purchase_review(self):
        """Verify review sets is_verified True for buyers."""
        self.client.login(
            username="buyeruser", password="password"
        )
        response = self.client.post(
            reverse(
                "add_product_review", args=[self.product.pk]
            ),
            {
                "rating": 5,
                "comment": "Fantastic product and fast delivery!",
            },
        )
        self.assertEqual(response.status_code, 302)
        review = ProductReview.objects.get(
            product=self.product
        )
        self.assertTrue(review.is_verified)
