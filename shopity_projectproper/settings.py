"""Django settings for the shopity_projectproper project."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env_bool(name, default=False):
    """Parse a boolean environment variable safely."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _env_list(name, default):
    """Parse a comma-separated list from environment."""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return list(default)
    return [
        item.strip()
        for item in raw.split(",")
        if item.strip()
    ]


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-me-in-env",
)

DEBUG = _env_bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = _env_list(
    "DJANGO_ALLOWED_HOSTS",
    ["127.0.0.1", "localhost"],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "marketplace",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    (
        "django.contrib.sessions.middleware"
        ".SessionMiddleware"
    ),
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    (
        "django.contrib.auth.middleware"
        ".AuthenticationMiddleware"
    ),
    (
        "django.contrib.messages.middleware"
        ".MessageMiddleware"
    ),
    (
        "django.middleware.clickjacking"
        ".XFrameOptionsMiddleware"
    ),
]

ROOT_URLCONF = "shopity_projectproper.urls"

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django"
            ".DjangoTemplates"
        ),
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors"
                    ".debug"
                ),
                (
                    "django.template.context_processors"
                    ".request"
                ),
                (
                    "django.contrib.auth.context_processors"
                    ".auth"
                ),
                (
                    "django.contrib.messages"
                    ".context_processors.messages"
                ),
                (
                    "marketplace.context_processors"
                    ".store_context"
                ),
                (
                    "marketplace.context_processors"
                    ".cart_context"
                ),
            ],
        },
    },
]

WSGI_APPLICATION = "shopity_projectproper.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "DB_ENGINE", "django.db.backends.mysql"
        ),
        "NAME": os.environ.get("DB_NAME", "shopity_db"),
        "USER": os.environ.get("DB_USER", "shopity_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation"
            ".UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation"
            ".MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation"
            ".CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation"
            ".NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = os.environ.get(
    "DJANGO_TIME_ZONE", "Africa/Johannesburg"
)

USE_I18N = True

USE_TZ = True

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = _env_bool(
    "EMAIL_USE_TLS", default=True
)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD", ""
)
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "noreply@shopity.com"
)

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "home"

LOGOUT_REDIRECT_URL = "home"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

CSRF_COOKIE_SECURE = _env_bool(
    "CSRF_COOKIE_SECURE", default=False
)

SESSION_COOKIE_SECURE = _env_bool(
    "SESSION_COOKIE_SECURE", default=False
)
