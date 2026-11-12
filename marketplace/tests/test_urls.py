"""
Unit tests for URL routing and reversal in the marketplace application.
"""
from django.test import SimpleTestCase
from django.urls import reverse


class URLRoutingTests(SimpleTestCase):
    """Test suite to ensure all named URL routes resolve successfully."""

    def test_public_and_catalog_urls_resolve(self):
        """Test public catalog, landing, and authentication routes."""
        self.assertEqual(reverse('home'), '/')
        self.assertEqual(reverse('product_catalog'), '/catalog/')
        self.assertEqual(reverse('register'), '/register/')
        self.assertEqual(reverse('product_detail', kwargs={'pk': 1}), '/product/1/')

    def test_cart_and_checkout_urls_resolve(self):
        """Test shopping cart and checkout action routes."""
        self.assertEqual(reverse('cart'), '/cart/')
        self.assertEqual(reverse('cart_add', kwargs={'product_id': 1}), '/cart/add/1/')
        self.assertEqual(
            reverse(
                'cart_remove',
                kwargs={
                    'item_id': 1}),
            '/cart/remove/1/')
        self.assertEqual(reverse('checkout'), '/checkout/')

    def test_vendor_dashboard_and_crud_urls_resolve(self):
        """Test vendor management and CRUD routes."""
        self.assertEqual(reverse('vendor_dashboard'), '/vendor/dashboard/')
        self.assertEqual(reverse('store_create'), '/vendor/store/create/')
        self.assertEqual(reverse('store_detail', kwargs={'pk': 1}), '/vendor/store/1/')
        self.assertEqual(
            reverse(
                'store_edit',
                kwargs={
                    'pk': 1}),
            '/vendor/store/1/edit/')
        self.assertEqual(
            reverse(
                'store_delete',
                kwargs={
                    'pk': 1}),
            '/vendor/store/1/delete/')

        self.assertEqual(reverse('product_create'), '/vendor/product/create/')
        self.assertEqual(
            reverse(
                'product_edit',
                kwargs={
                    'pk': 1}),
            '/vendor/product/1/edit/')
        self.assertEqual(
            reverse(
                'product_delete',
                kwargs={
                    'pk': 1}),
            '/vendor/product/1/delete/')

    def test_reviews_and_fulfillment_urls_resolve(self):
        """Test customer reviews, fulfillment, and buyer dashboard routes."""
        self.assertEqual(
            reverse(
                'add_product_review',
                kwargs={
                    'product_id': 1}),
            '/product/1/review/')
        self.assertEqual(
            reverse(
                'update_order_item_status',
                kwargs={
                    'item_id': 1}),
            '/vendor/order-item/1/update/')
        self.assertEqual(reverse('buyer_dashboard'), '/buyer/dashboard/')
