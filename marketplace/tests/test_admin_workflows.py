"""Tests for marketplace administrative and vendor workflows."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from marketplace.models import Store

User = get_user_model()


class AdminWorkflowTests(TestCase):
    """Test cases for administrative workflows and store creation."""

    def setUp(self):
        """Set up test user for workflow tests."""
        self.user = User.objects.create_user(
            username="vendor1", password="password"
        )

    def test_store_creation_workflow(self):
        """Verify that a vendor can create multiple stores."""
        first = Store.objects.create(
            name="Test Store", owner=self.user
        )
        second = Store.objects.create(
            name="Second Store", owner=self.user
        )
        self.assertEqual(first.name, "Test Store")
        self.assertEqual(second.owner, self.user)
        self.assertEqual(
            Store.objects.filter(owner=self.user).count(), 2
        )
