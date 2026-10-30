"""
Forms and custom validation logic for the sticky notes application.
"""

from django import forms
from .models import Note, COLOR_CHOICES

class NoteForm(forms.ModelForm):
    """
    Form for creating and updating Note instances with custom color validation.
    """
    class Meta:
        model = Note
        fields = ['title', 'content', 'color', 'is_pinned']

    def clean_color(self):
        """Validates that the selected color exists within allowed choices."""
        color = self.cleaned_data.get('color')
        valid_colors = [choice[0] for choice in COLOR_CHOICES]
        if color not in valid_colors:
            raise forms.ValidationError("Invalid colour choice selected.")
        return color