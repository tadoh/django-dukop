# Using development settings, replace in production!
from .base import BASE_DIR  # noqa
from .base import INSTALLED_APPS  # noqa
from .production import *  # noqa

SECRET_KEY = "test"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR.parent / "test.sqlite3"),
    },
    "detsker": {
        "NAME": "detsker",
        "ENGINE": "django.db.backends.postgresql",
        "USER": "",
        "PASSWORD": "",
    },
}

INSTALLED_APPS.append("dukop.apps.sync_old")

DATABASE_ROUTERS = ["dukop.apps.sync_old.router.SyncRouter"]

EMAIL_CONFIRM_SALT = "test"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# DUKOP_BACKWARDS_DAYS = 100

THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.dbm_kvstore.KVStore"
