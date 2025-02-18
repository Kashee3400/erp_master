from .base import *
DB_ENGINE = config("DB_ENGINE", None)

DB_NAME_SARTHAK = config("DB_NAME_SARTHAK", None)
DB_USER_SARTHAK = config("DB_USER_SARTHAK", None)
DB_PASSWORD_SARTHAK = config("DB_PASSWORD_SARTHAK", None)
DB_HOST_SARTHAK = config("DB_HOST_SARTHAK", None)
DB_PORT_SARTHAK = config("DB_PORT_SARTHAK", None)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "sqlite3.db"),
    },
    "sarthak_kashee": {
        "ENGINE": DB_ENGINE,
        "NAME": DB_NAME_SARTHAK,
        "USER": DB_USER_SARTHAK,
        "PASSWORD": DB_PASSWORD_SARTHAK,
        "HOST": DB_HOST_SARTHAK,
        "PORT": DB_PORT_SARTHAK,
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