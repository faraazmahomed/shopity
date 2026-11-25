"""Django settings for the shopity_projectproper project."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = (
    "django-insecure-your-secret-key-change-this-in-production"
)

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

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
        "ENGINE": "django.db.backends.mysql",
        "NAME": "shopity_db",
        "USER": "shopity_user",
        "PASSWORD": "secure_password123",
        "HOST": "127.0.0.1",
        "PORT": "3306",
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

TIME_ZONE = "Africa/Johannesburg"

USE_I18N = True

USE_TZ = True

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
)

DEFAULT_FROM_EMAIL = "noreply@shopity.com"

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "home"

LOGOUT_REDIRECT_URL = "home"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

CSRF_COOKIE_SECURE = False

SESSION_COOKIE_SECURE = False
