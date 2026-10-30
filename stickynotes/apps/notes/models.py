# apps/notes/models.py
from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    # Color choices for styling the sticky notes in UI
    COLOR_CHOICES = [
        ('yellow', 'Yellow'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
    ]

    # Required Fields
    title = models.CharField(max_length=200, help_text="Short title for the note")
    content = models.TextField(help_text="Detailed note content")

    # Optional Utility Fields
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='yellow')
    is_pinned = models.BooleanField(default=False, help_text="Pin note to top")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: Associate note with a user (if multi-user)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', null=True, blank=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']  # Pinned notes first, then latest updated

    def __str__(self):
        return self.title
