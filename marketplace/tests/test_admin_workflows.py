"""
Tests for marketplace administrative workflows.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Store

User = get_user_model()


class AdminWorkflowTests(TestCase):
    """Test cases for administrative workflows and store creation."""

    def setUp(self):
        """Set up test user for workflow tests."""
        self.user = User.objects.create_user(username="vendor1", password="password")

    def test_store_creation_workflow(self):
        """Verify that a store can be successfully created by a vendor."""
        store = Store.objects.create(name="Test Store", owner=self.user)
        self.assertEqual(store.name, "Test Store")
        self.assertEqual(store.owner, self.user)
