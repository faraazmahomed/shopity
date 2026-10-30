"""
URL Configuration for the Shopity Project.

This module maps top-level URL patterns to their respective views and app-level
URL routers, including Django admin, built-in authentication, the Reddit feed
integration, and the primary marketplace application.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views

# ==========================================
# MAIN URL PATTERNS
# ==========================================

urlpatterns = [
    # Django Administrative Portal
    path('admin/', admin.site.urls),

    # Django Built-in Authentication Views (login, logout, password resets)
    path('accounts/', include('django.contrib.auth.urls')),

    # Dedicated Reddit Feed Endpoint
    path('reddit/', views.reddit_feed, name='reddit_feed'),

    # Primary Marketplace Application Routes
    path('', include('marketplace.urls')),
]

# ==========================================
# MEDIA FILES CONFIGURATION (DEVELOPMENT)
# ==========================================

# Serve user-uploaded media files during development when DEBUG is enabled
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
