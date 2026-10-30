"""
URL configuration for stickynotes project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Root URL routes directly to your notes app homepage
    path("", include("apps.notes.urls")),
]
