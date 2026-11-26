"""Unit tests for URL routing and reversal in marketplace."""

from django.test import SimpleTestCase
from django.urls import reverse


class URLRoutingTests(SimpleTestCase):
    """Test suite to ensure named URL routes resolve cleanly."""

    def test_public_and_catalog_urls_resolve(self):
        """Test public catalog, landing, and auth routes."""
        self.assertEqual(reverse("home"), "/")
        self.assertEqual(reverse("product_catalog"), "/catalog/")
        self.assertEqual(reverse("register"), "/register/")
        self.assertEqual(
            reverse("product_detail", kwargs={"pk": 1}),
            "/product/1/",
        )

    def test_cart_and_checkout_urls_resolve(self):
        """Test shopping cart and checkout action routes."""
        self.assertEqual(reverse("cart"), "/cart/")
        self.assertEqual(reverse("cart_detail"), "/cart/")
        self.assertEqual(
            reverse("cart_add", kwargs={"product_id": 1}),
            "/cart/add/1/",
        )
        self.assertEqual(
            reverse("cart_remove", kwargs={"item_id": 1}),
            "/cart/remove/1/",
        )
        self.assertEqual(reverse("checkout"), "/checkout/")

    def test_vendor_dashboard_store_and_product_urls(self):
        """Test consolidated vendor dashboard, store, and product URLs."""
        self.assertEqual(
            reverse("vendor_dashboard"), "/vendor/dashboard/"
        )
        self.assertEqual(
            reverse("store_create"), "/vendor/store/create/"
        )
        self.assertEqual(
            reverse("store_detail", kwargs={"pk": 1}),
            "/vendor/store/1/",
        )
        self.assertEqual(
            reverse("store_edit", kwargs={"pk": 1}),
            "/vendor/store/1/edit/",
        )
        self.assertEqual(
            reverse("store_delete", kwargs={"pk": 1}),
            "/vendor/store/1/delete/",
        )
        self.assertEqual(
            reverse("vendor_product_list"), "/vendor/products/"
        )
        self.assertEqual(
            reverse("vendor_product_add"), "/vendor/products/add/"
        )
        self.assertEqual(
            reverse("vendor_product_edit", kwargs={"pk": 1}),
            "/vendor/products/1/edit/",
        )
        self.assertEqual(
            reverse("vendor_product_delete", kwargs={"pk": 1}),
            "/vendor/products/1/delete/",
        )
        self.assertEqual(
            reverse("product_create"), "/vendor/product/create/"
        )
        self.assertEqual(
            reverse("product_edit", kwargs={"pk": 1}),
            "/vendor/product/1/edit/",
        )
        self.assertEqual(
            reverse("product_delete", kwargs={"pk": 1}),
            "/vendor/product/1/delete/",
        )

    def test_orders_reviews_and_buyer_urls_resolve(self):
        """Test vendor orders, reviews, and buyer routes."""
        self.assertEqual(
            reverse("vendor_order_list"), "/vendor/orders/"
        )
        self.assertEqual(
            reverse("vendor_order_detail", kwargs={"pk": 1}),
            "/vendor/orders/1/",
        )
        self.assertEqual(
            reverse(
                "update_order_item_status",
                kwargs={"item_id": 1},
            ),
            "/vendor/order-item/1/update/",
        )
        self.assertEqual(
            reverse(
                "add_product_review", kwargs={"product_id": 1}
            ),
            "/product/1/review/",
        )
        self.assertEqual(
            reverse("buyer_dashboard"), "/buyer/dashboard/"
        )
        self.assertEqual(
            reverse("buyer_orders"), "/buyer/orders/"
        )
