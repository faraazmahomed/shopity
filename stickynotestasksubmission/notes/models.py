"""
Database models for the sticky notes application.
"""

from django.db import models

COLOR_CHOICES = [
    ('yellow', 'Yellow'),
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('pink', 'Pink'),
]

from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    color = models.CharField(max_length=50, default='yellow')
    is_pinned = models.BooleanField(default=False)
    
    # Ensure auto_now and auto_now_add are set correctly:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns the string representation of the note (its title)."""
        return self.title
