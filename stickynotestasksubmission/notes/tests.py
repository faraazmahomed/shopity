"""
Unit test suite for models, forms, views, and ordering logic of the sticky notes app.
"""

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from .models import Note
from .forms import NoteForm


class TestUserAuthentication(TestCase):
    """
    Test case class verifying user authentication functionality.
    """
    def setUp(self):
        """Sets up test user credentials."""
        self.username = "testuser"
        self.password = "securepassword123"
        self.user = User.objects.create_user(
            username=self.username, 
            password=self.password
        )

    def test_successful_authentication(self):
        """Verify that a user can successfully authenticate with valid credentials."""
        logged_in = self.client.login(
            username=self.username, 
            password=self.password
        )
        self.assertTrue(logged_in, "The user failed to authenticate with valid credentials.")


class StickyNotesCompleteTestCase(TestCase):
    """
    Test case class verifying CRUD functionality, validation, and layout logic.
    """
    def setUp(self):
        """Sets up test client and sample notes representing different pin states."""
        self.client = Client()
        self.unpinned_1 = Note.objects.create(title="Unpinned One", content="Content A", color="yellow", is_pinned=False)
        self.pinned_1 = Note.objects.create(title="Pinned One", content="Content B", color="blue", is_pinned=True)
        self.pinned_2 = Note.objects.create(title="Pinned Two", content="Content C", color="green", is_pinned=True)
        self.unpinned_2 = Note.objects.create(title="Unpinned Two", content="Content D", color="pink", is_pinned=False)

    def test_pinned_ordering_rule(self):
        """Verify that pinned notes appear before unpinned notes in the list view."""
        response = self.client.get(reverse('notes:note_list'))
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        
        self.assertTrue(notes[0].is_pinned)
        self.assertTrue(notes[1].is_pinned)
        self.assertFalse(notes[2].is_pinned)
        self.assertFalse(notes[3].is_pinned)

    def test_note_detail_view(self):
        """Verify the read-detail view loads successfully and displays note content."""
        response = self.client.get(reverse('notes:note_detail', args=[self.unpinned_1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.unpinned_1.title)
        self.assertContains(response, self.unpinned_1.content)
        self.assertTemplateUsed(response, 'notes/note_detail.html')

    def test_note_update_view(self):
        """Verify the update view correctly modifies an existing note via POST."""
        response = self.client.post(reverse('notes:note_update', args=[self.unpinned_1.pk]), {
            'title': 'Updated Title',
            'content': 'Updated Content',
            'color': 'green',
            'is_pinned': True
        })
        self.assertEqual(response.status_code, 302)
        self.unpinned_1.refresh_from_db()
        self.assertEqual(self.unpinned_1.title, 'Updated Title')
        self.assertTrue(self.unpinned_1.is_pinned)
        self.assertEqual(self.unpinned_1.color, 'green')

    def test_invalid_form_submission(self):
        """Verify that submitting a form with missing required fields fails validation."""
        response = self.client.post(reverse('notes:note_create'), {
            'title': '',
            'content': 'Some content',
            'color': 'yellow'
        })
        self.assertEqual(response.status_code, 200)
        # Pass response.context['form'] instead of the response object itself:
        self.assertFormError(response.context['form'], 'title', 'This field is required.')

    def test_colour_choice_validation(self):
        """Verify that selecting an unsupported color fails form validation."""
        form_data = {
            'title': 'Bad Color Note',
            'content': 'Content',
            'color': 'unsupported_color_hex',
            'is_pinned': False
        }
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('color', form.errors)

    def test_deletion_confirmation_and_action(self):
        """Verify that GET requests show the confirmation page and POST deletes the note."""
        get_response = self.client.get(reverse('notes:note_delete', args=[self.unpinned_1.pk]))
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, 'notes/note_confirm_delete.html')
        
        post_response = self.client.post(reverse('notes:note_delete', args=[self.unpinned_1.pk]))
        self.assertEqual(post_response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.unpinned_1.pk).exists())
