from .base import *


# settings.py
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

# cred for connecting sarthak db
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

# cred for connecting mpms db
DB_NAME_MPMS = config("DB_NAME_MPMS", None)

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
        "ENGINE": DB_ENGINE,
        "NAME": DB_NAME_MPMS,
        "USER": DB_USER_SARTHAK,
        "PASSWORD": DB_PASSWORD_SARTHAK,
        "HOST": DB_HOST_SARTHAK,
        "PORT": DB_PORT_SARTHAK,
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
        },
    },
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {
        "level": "DEBUG" if DEBUG else "INFO",
        "handlers": ["console", "file"],
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(message)s",
        },
        "simple": {"format": "[%(asctime)s] %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {  # Added file handler for error logging
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "error.log"),
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
        },
    },
    "loggers": {
        # Django loggers
        "django": {
            "propagate": True,
        },
        "django.db": {"level": "WARNING"},
        "django.request": {
            "handlers": ["mail_admins", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "template_timings_panel": {
            "handlers": ["null"],
        },
    },
}

STATIC_ROOT=STATIC_DIR

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5566",
    "http://1.22.197.176:5566",
]


REST_FRAMEWORK.update({
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
        "anon": "100/day",
    },
})