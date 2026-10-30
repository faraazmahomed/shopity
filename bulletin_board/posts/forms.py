from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    """Form for creating and updating Post objects.

    Fields:
    - title: CharField for the post title.
    - content: TextField for the post content.
    - author: ForeignKey selection for the post author.
    """

    class Meta:
        model = Post
        fields = ["title", "content", "author"]
