"""
Tests for marketplace administrative workflows such as store approval.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Store

User = get_user_model()

class AdminWorkflowTests(TestCase):
    """Test cases for administrative workflows and store status updates."""

    def setUp(self):
        """Set up test user for workflow tests."""
        self.user = User.objects.create_user(username='vendor1', password='password')

    def test_store_approval_workflow(self):
        """Verify that store approval status can be toggled or updated."""
        store = Store.objects.create(name='Test Store', owner=self.user, approval_status='pending')
        self.assertEqual(store.approval_status, 'pending')
        store.approval_status = 'approved'
        store.save()
        self.assertEqual(store.approval_status, 'approved')