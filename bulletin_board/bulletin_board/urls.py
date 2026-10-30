# bulletin_board/urls.py
from django.contrib import admin
from django.urls import include, path
# Define URL patterns for the entire project
urlpatterns = [
    # Admin URL pattern, mapping to the Django admin interface
    path("admin/", admin.site.urls),
    # Include URL patterns from the 'posts' app
    # All URLs from 'posts.urls' will be prefixed with '/'
    path("", include("posts.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
]
