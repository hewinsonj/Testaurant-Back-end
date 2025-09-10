"""
Django settings for testaurant_app_crud project.

Hardened for production deploys (Fly.io/Heroku/etc.) and clean local dev.
"""

import os
from pathlib import Path
import dj_database_url

# --- Base paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Debug/Secrets ---
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("SECRET", "change-me"))  # support old SECRET name

# --- Hosts ---
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".fly.dev",             # Fly default app hostname
]
_custom_host = os.getenv("ALLOWED_HOST")
if _custom_host:
    ALLOWED_HOSTS.append(_custom_host)

# --- Applications ---
INSTALLED_APPS = [
    # Project apps
    "api",

    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "whitenoise.runserver_nostatic",  # before django.contrib.staticfiles

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# --- Middleware (order matters) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # add right after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",       # CORS early
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "testaurant_app_crud.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "testaurant_app_crud.wsgi.application"

# --- Django Rest Framework defaults ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# --- Database ---
# Reads DATABASE_URL; falls back to local sqlite for convenience.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///" + str(BASE_DIR / "db.sqlite3"),
        conn_max_age=600,
        ssl_require=False,  # Fly internal Postgres typically doesn't require SSL
    )
}

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- Static files for admin & browsable API ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- CORS/CSRF ---

# --- TEMP: open up CORS for debugging, revert after verifying ---
CORS_ALLOW_ALL_ORIGINS = True
# keep these so preflights are clean
from corsheaders.defaults import default_headers, default_methods
CORS_ALLOW_HEADERS = list(default_headers) + ["authorization", "content-type"]
CORS_ALLOW_METHODS = list(default_methods) + ["OPTIONS"]
CORS_URLS_REGEX = r"^/.*$"


CLIENT_ORIGIN = os.getenv("CLIENT_ORIGIN", "https://testaurantapp.netlify.app")  # default to Netlify app if not provided
CLIENT_ORIGIN_DEV = os.getenv("CLIENT_ORIGIN_DEV", "http://localhost:3000")

CORS_ALLOWED_ORIGINS = [o for o in [CLIENT_ORIGIN, CLIENT_ORIGIN_DEV] if o]
CSRF_TRUSTED_ORIGINS = [
    "https://*.fly.dev",
] + [o for o in [CLIENT_ORIGIN, CLIENT_ORIGIN_DEV] if o]

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]

CORS_ALLOW_METHODS = list(default_methods) + [
    "OPTIONS",
]

# Ensure CORS applies to all URL patterns
CORS_URLS_REGEX = r"^/.*$"

# --- Security/Proxy ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Auth model ---
AUTH_USER_MODEL = "api.User"

# --- Auto field (silences BigAutoField warning on newer Django) ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
