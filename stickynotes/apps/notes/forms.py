from django import forms
from .models import Note
from django.contrib.auth.forms import UserCreationForm
from .models import User

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content", "color", "is_pinned"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Title...", "class": "form-input"}
            ),
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Write your note here...",
                    "rows": 3,
                    "class": "form-input",
                }
            ),
            "color": forms.Select(attrs={"class": "form-input"}),
            "is_pinned": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].widget.attrs.update({"class": "form-select"})
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})