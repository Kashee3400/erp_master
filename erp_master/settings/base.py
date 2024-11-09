from pathlib import Path
from django.conf import settings
import os
from decouple import config
from typing import Any, Dict
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config("SECRET_KEY", None)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")


INSTALLED_APPS = [
    "member",
    "mpms",
    "erp_app",
    "bootstrap5",
    "django_filters",
    "crispy_forms",
    "crispy_bootstrap5",
    "fontawesomefree",
    "import_export",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework",
    "widget_tweaks",
    "django_tables2",
]

SITE_ID = 1
THUMBNAIL_DEBUG = True
THUMBNAIL_FORMAT = "JPEG"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "erp_app.login_middleware.LoginRequiredMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "member.middleware.CurrentRequestMiddleware",
]

DATABASE_ROUTERS = [
    "erp_app.dbrouters.SarthakKasheeRouter",
    "mpms.db_routers.MPMSDBRouter",
]
WSGI_APPLICATION = "erp_master.wsgi.application"

ROOT_URLCONF = "erp_master.urls"

API_URL_PREFIX = ["/api/"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
        },
    },
]

# URL for login
LOGIN_URL = "/admin/login/"

LOGIN_REDIRECT_URL = "/admin/"




LOG_DIR = os.path.join(BASE_DIR, "logs")  # Adjust this path if necessary
os.makedirs(LOG_DIR, exist_ok=True)

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

# LANGUAGE_CODE = 'hi-IN'
LANGUAGE_CODE = "en-us"

USE_L10N = True

LANGUAGES = [
    ("hi", "Hindi"),
    ("en", "English"),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365 * 10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=150),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
}

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# def send_fcm_notification():
#         data_payload = {
#             "data": {
#                 "title": "New Notification",
#                 "body": {
#                     "message":"Hello There",
#                     "date": ""
#                 },
#             },
#             "to": "d5W0JSvrQE6vBrBC_k06GV:APA91bHcVCJ3fr7PXqCAGxl_Pai1_b4_4mHawWVAcqBUKkEsikiJRPF9KV3mKPRKQtxfqLnK9JlxJMgbhCYbhUws33DirIJ8wkxumERN_SdfJo66CkbS0f1Pc98EPVjvnqcFEXBmOgaC"
#         }
#         url = "https://fcm.googleapis.com/fcm/send"
#         headers = {
#                 "Authorization": "key=AAAAI-hZouk:APA91bFOo-4zAELDwxbaZme6pt0wYrN3rp8fy98EGRntKbZoqEqupj8tpsWKSAGRToVEZkB5OK6tH7zmz4gEfMY1joi4weSupGPV9V4PPvAbDwV7ry68jq07c3OThWR8zsHHsk5XVQ3x",
#                 "Content-Type": "application/json"
#         }
#         response = requests.post(url, headers=headers, json=data_payload)
#         print(response)
#         return response

# send_fcm_notification()

from .jazzmin_settings import *

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
