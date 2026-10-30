# apps/notes/tests.py
from django.test import TestCase
from django.urls import reverse
from .forms import NoteForm
from .models import Note


class NoteModelTest(TestCase):

    def setUp(self):
        self.note = Note.objects.create(
            title="First Note",
            content="Content for first note.",
            color="pink",
            is_pinned=True,
        )

    def test_note_creation(self):
        """Test that note attributes are set properly."""
        self.assertEqual(self.note.title, "First Note")
        self.assertEqual(
            self.note.content, "Content for first note."
        )
        self.assertEqual(self.note.color, "pink")
        self.assertTrue(self.note.is_pinned)

    def test_note_str_representation(self):
        """Test model __str__ method returns the title."""
        self.assertEqual(str(self.note), "First Note")

    def test_note_ordering(self):
        """Test pinned notes appear before unpinned notes."""
        unpinned = Note.objects.create(
            title="Unpinned Note",
            content="Some content.",
            is_pinned=False,
        )
        notes = Note.objects.all()
        self.assertEqual(notes[0], self.note)
        self.assertEqual(notes[1], unpinned)


class NoteFormTest(TestCase):

    def test_valid_form(self):
        """Test NoteForm with valid data."""
        data = {
            "title": "Form Note",
            "content": "Valid content.",
            "color": "blue",
            "is_pinned": False,
        }
        form = NoteForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_title(self):
        """Test NoteForm fails without a title."""
        data = {
            "title": "",
            "content": "Content without title.",
            "color": "yellow",
            "is_pinned": False,
        }
        form = NoteForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class NoteViewsTest(TestCase):

    def setUp(self):
        self.note = Note.objects.create(
            title="View Test Note",
            content="Testing views.",
            color="green",
        )

    def test_note_list_view_get(self):
        """Test homepage loads correctly with notes."""
        response = self.client.get(reverse("notes:note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_list.html")
        self.assertContains(response, "View Test Note")
        self.assertContains(response, "Testing views.")

    def test_note_create_post(self):
        """Test creating a note via POST request."""
        data = {
            "title": "New Sticky Note",
            "content": "Created via post.",
            "color": "purple",
            "is_pinned": True,
        }
        response = self.client.post(
            reverse("notes:note_list"), data=data
        )
        # Should redirect back to note_list
        self.assertRedirects(response, reverse("notes:note_list"))
        self.assertTrue(
            Note.objects.filter(title="New Sticky Note").exists()
        )

    def test_note_delete_post(self):
        """Test deleting a note via POST request."""
        delete_url = reverse(
            "notes:note_delete", args=[self.note.pk]
        )
        response = self.client.post(delete_url)
        # Should redirect back to note_list
        self.assertRedirects(response, reverse("notes:note_list"))
        self.assertFalse(
            Note.objects.filter(pk=self.note.pk).exists()
        )
