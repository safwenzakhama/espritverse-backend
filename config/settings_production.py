"""
Production settings for EspritVerse
"""
import os
from pathlib import Path
from decouple import config
from .settings import *

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')

# 1) Hosts & CSRF (Railway uses *.railway.app / *.up.railway.app)
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    ".railway.app,.up.railway.app,localhost,127.0.0.1"
).split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://"+h.lstrip(".") for h in ALLOWED_HOSTS if h not in ("localhost","127.0.0.1")
]

# 2) Reverse proxy / HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# 3) Database (use DATABASE_URL, persistent connections)
import dj_database_url

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "CONN_MAX_AGE": int(os.getenv("PG_CONN_MAX_AGE", "60")),
        "OPTIONS": {"sslmode": os.getenv("PGSSLMODE", "prefer")},
    }
}

DATABASES["default"].update(
    dj_database_url.config(default=os.getenv("DATABASE_URL"), conn_max_age=60)
)

# 4) Static files (WhiteNoise)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS settings for production
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in config('CORS_ALLOWED_ORIGINS', default='').split(',') if origin.strip()]
CORS_ALLOW_CREDENTIALS = True

# HTTPS settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)

# Session security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# Email settings (configure for your email provider)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# 5) WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 6) Logging
LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
