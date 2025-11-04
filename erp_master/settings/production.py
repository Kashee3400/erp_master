from .base import *
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
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


def setup_log_directory():
    """Ensure log directory exists"""
    log_dir = getattr(settings, "LOG_DIR", os.path.join(BASE_DIR, "logs"))
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


# Call this in your Django app's ready() method or in settings
setup_log_directory()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        # Handlers for each app
        "notifications_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "notifications.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "member_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "member.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "facilitator_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "facilitator.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "feedback_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "feedback.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "veterinary_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "veterinary.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mpms_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "mpms.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        # Optional console logging
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "notifications": {
            "handlers": ["notifications_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "member": {
            "handlers": ["member_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "facilitator": {
            "handlers": ["facilitator_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "feedback": {
            "handlers": ["feedback_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "veterinary": {
            "handlers": ["veterinary_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "mpms": {
            "handlers": ["mpms_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

STATIC_ROOT = STATIC_DIR

from corsheaders.defaults import default_headers

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="")
if CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",")
    ]
else:
    CORS_ALLOWED_ORIGINS = []

CORS_ALLOW_HEADERS = list(default_headers) + [
    "X-API-KEY",
]

# import crontab

# CELERY_BEAT_SCHEDULE = {
#     "daily_admin_test_notification": {
#         "task": "notifications.tasks.test_notification",
#         "schedule": crontab(hour=10, minute=0),
#         "kwargs": {"user": "9565901765", "template": "member_sync_completed"},
#     },
#     "syc_member_data": {
#         "task": "veterinary.tasks.process_member_sync_notifications",
#         "schedule": crontab(hour=1, minute=0),
#     },
# }
