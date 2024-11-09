from .base import *


DB_ENGINE = os.getenv("DB_ENGINE", None)

# cred for connecting sarthak db
DB_NAME_SARTHAK = os.getenv("DB_NAME_SARTHAK", None)
DB_USER_SARTHAK = os.getenv("DB_USER_SARTHAK", None)
DB_PASSWORD_SARTHAK = os.getenv("DB_PASSWORD_SARTHAK", None)
DB_HOST_SARTHAK = os.getenv("DB_HOST_SARTHAK", None)
DB_PORT_SARTHAK = os.getenv("DB_PORT_SARTHAK", None)


# cred for connecting member db
DB_NAME_MEMBER = os.getenv("DB_NAME_MEMBER", None)
DB_MEMBER_USER = os.getenv("DB_MEMBER_USER", None)
DB_MEMBER_PASS = os.getenv("DB_MEMBER_PASS", None)
DB_HOST_MEMBER = os.getenv("DB_HOST_MEMBER", None)
DB_PORT_MEMBER = os.getenv("DB_PORT_MEMBER", None)

# cred for connecting mpms db
DB_NAME_MPMS = os.getenv("DB_NAME_MPMS", None)
DB_USER_MPMS = os.getenv("DB_USER_MPMS", None)
DB_PASSWORD_MPMS = os.getenv("DB_PASSWORD_MPMS", None)
DB_HOST_MPMS = os.getenv("DB_HOST_MPMS", None)
DB_PORT_MPMS = os.getenv("DB_PORT_MPMS", None)

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
        "USER": DB_USER_MPMS,
        "PASSWORD": DB_PASSWORD_MPMS,
        "HOST": DB_HOST_MPMS,
        "PORT": DB_PORT_MPMS,
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
            "handlers": ["mail_admins", "file"],  # Log errors to file as well
            "level": "ERROR",
            "propagate": False,
        },
        # Suppress output of this debug toolbar panel
        "template_timings_panel": {
            "handlers": ["null"],
        },
    },
}

STATIC_ROOT = STATIC_DIR
