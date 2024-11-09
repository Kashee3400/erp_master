from .base import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "sqlite3.db"),
    },
    "sarthak_kashee": {
        "ENGINE": "mssql",
        "NAME": "sarthak_kashee",
        "USER": "sarthak",
        "PASSWORD": "123",
        "HOST": "10.10.11.2",
        "PORT": 1433,
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
        },
    },
    "mpms_db": {
        "ENGINE": "mssql",
        "NAME": "kanha_Procurement",
        "USER": "sarthak",
        "PASSWORD": "123",
        "HOST": "10.10.11.2",
        "PORT": 1433,
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
        },
    },
}

STATICFILES_DIRS = [STATIC_DIR]