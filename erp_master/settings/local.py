from .base import *


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


DB_ENGINE = config("DB_ENGINE", None)

DB_NAME_SARTHAK = config("DB_NAME_SARTHAK", None)
DB_USER_SARTHAK = config("DB_USER_SARTHAK", None)
DB_PASSWORD_SARTHAK = config("DB_PASSWORD_SARTHAK", None)
DB_HOST_SARTHAK = config("DB_HOST_SARTHAK", None)
DB_PORT_SARTHAK = config("DB_PORT_SARTHAK", None)


# cred for connecting member db
DB_NAME_MEMBER = config("DB_NAME_MEMBER", None)
DB_MEMBER_USER = config("DB_MEMBER_USER", None)
DB_MEMBER_PASS = config("DB_MEMBER_PASS", None)
DB_HOST_MEMBER = config("DB_HOST_MEMBER", None)
DB_PORT_MEMBER = config("DB_PORT_MEMBER", None)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME_MEMBER,
        "USER": DB_MEMBER_USER,
        "PASSWORD": DB_MEMBER_PASS,
        "HOST": DB_HOST_MEMBER,
        "PORT": DB_PORT_MEMBER,
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

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']

REST_FRAMEWORK.update({
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
})