"""Local development: SQLite, console email, DEBUG on."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, SECRET_KEY as _KEY

DEBUG = True
SECRET_KEY = _KEY or "dev-only-insecure-key-do-not-use-in-production"
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
