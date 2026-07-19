from .base import *  # noqa: F401,F403

DEBUG = True

SECRET_KEY = "django-insecure-dev-only-change-me-for-anything-shared"

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Prefer simple static storage in local/dev so collectstatic is optional.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
