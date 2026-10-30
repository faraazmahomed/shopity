"""
App configuration for the marketplace application.

Defines application metadata and default auto-field settings for Django models.
"""

from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    """Configuration class for the marketplace application."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "marketplace"
