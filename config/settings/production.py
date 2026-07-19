import os

from .base import *  # noqa: F401,F403

DEBUG = os.environ.get("DEBUG", "false").lower() in {"1", "true", "yes"}

SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-production-fallback-change-me")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
