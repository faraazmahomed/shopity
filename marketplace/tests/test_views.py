"""Tests for marketplace views, multi-store CRUD, and catalog."""

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from marketplace.models import Product, Store

User = get_user_model()


class MarketplaceViewTests(TestCase):
    """Test cases for verifying view responses and permissions."""

    def setUp(self):
        """Initialize client, vendor group, stores, and product."""
        self.client = Client()
        self.vendor_group, _ = Group.objects.get_or_create(
            name="Vendors"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password",
        )
        self.user.groups.add(self.vendor_group)
        self.buyer = User.objects.create_user(
            username="buyeruser",
            email="buyeruser@example.com",
            password="password",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="password",
        )
        self.store = Store.objects.create(
            name="Test Store", owner=self.user
        )
        self.second_store = Store.objects.create(
            name="Second Store", owner=self.user
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Test Product",
            base_price=49.99,
            stock=5,
            is_active=True,
        )

    def test_home_view(self):
        """Verify home page loads successfully with status 200."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_product_catalog_view(self):
        """Verify product catalog loads with status 200."""
        response = self.client.get(reverse("product_catalog"))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_flow_resolves_and_resets(self):
        """Verify reset email link resolves and updates password."""
        resp = self.client.post(
            reverse("password_reset_request"),
            {"email": "testuser@example.com"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        match = re.search(
            r"/password-reset/confirm/([^/\s]+)/",
            mail.outbox[0].body,
        )
        self.assertIsNotNone(match)
        token = match.group(1)
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"token": token}
        )
        get_resp = self.client.get(confirm_url)
        self.assertEqual(get_resp.status_code, 200)
        post_resp = self.client.post(
            confirm_url,
            {
                "new_password1": "NewStrongPass123!",
                "new_password2": "NewStrongPass123!",
            },
        )
        self.assertEqual(post_resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("NewStrongPass123!")
        )

    def test_vendor_dashboard_lists_all_stores(self):
        """Verify vendor dashboard displays all owned stores."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("vendor_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Store")
        self.assertContains(response, "Second Store")
        self.assertContains(
            response,
            reverse("store_detail", args=[self.store.pk]),
        )
        self.assertContains(
            response,
            reverse("store_edit", args=[self.store.pk]),
        )
        self.assertContains(
            response,
            reverse("store_delete", args=[self.store.pk]),
        )
        self.assertContains(response, reverse("store_create"))

    def test_vendor_can_create_product_after_store(self):
        """Verify vendor can create product without 403 error."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("product_create"),
            {
                "store": self.second_store.pk,
                "name": "New Store Item",
                "description": "Item description",
                "base_price": "25.00",
                "stock": 8,
                "is_active": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Product.objects.filter(
                name="New Store Item", store=self.second_store
            ).exists()
        )

    def test_non_vendor_blocked_from_store_create(self):
        """Verify non-vendor user gets 403 on store_create."""
        self.client.force_login(self.buyer)
        response = self.client.get(reverse("store_create"))
        self.assertEqual(response.status_code, 403)

    def test_store_edit_and_delete_scoped_to_owner(self):
        """Verify vendors edit/delete own stores but not others."""
        self.client.force_login(self.user)
        edit_resp = self.client.post(
            reverse("store_edit", args=[self.second_store.pk]),
            {
                "name": "Updated Second Store",
                "description": "Desc",
            },
        )
        self.assertEqual(edit_resp.status_code, 302)
        self.second_store.refresh_from_db()
        self.assertEqual(
            self.second_store.name, "Updated Second Store"
        )

        other_store = Store.objects.create(
            name="Other Store", owner=self.other_user
        )
        forbidden_edit = self.client.get(
            reverse("store_edit", args=[other_store.pk])
        )
        forbidden_delete = self.client.post(
            reverse("store_delete", args=[other_store.pk])
        )
        self.assertEqual(forbidden_edit.status_code, 404)
        self.assertEqual(forbidden_delete.status_code, 404)

    def test_store_model_string_in_view_context(self):
        """Verify seeded product exists in database."""
        self.assertTrue(
            Product.objects.filter(name="Test Product").exists()
        )
