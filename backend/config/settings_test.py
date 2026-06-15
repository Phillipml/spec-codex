from .settings import *  # noqa: F403

SECRET_KEY = "test-secret-key-for-pytest"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
CRON_SYNC_SECRET = "test-cron-secret"
BNET_CLIENT_ID = "test-client-id"
BNET_CLIENT_SECRET = "test-client-secret"
