from .base import *
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


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

def setup_log_directory():
    """Ensure log directory exists"""
    log_dir = getattr(settings, 'LOG_DIR', os.path.join(BASE_DIR, 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


# Call this in your Django app's ready() method or in settings
setup_log_directory()

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'excel_import.log'),
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'your_app': {  # Replace with your app name
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

STATIC_ROOT=STATIC_DIR

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5566",
    "https://1.22.197.176:5566",
]