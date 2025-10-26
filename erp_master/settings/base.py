from pathlib import Path
import os
from decouple import config
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DEBUG = config("DEBUG", default=False, cast=bool)
SECRET_KEY = config("SECRET_KEY", None)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

GEOIP_PATH = os.path.join(BASE_DIR, "geoip")

LOCAL_APPS = [
    "member",
    "mpms",
    "erp_app",
    "facilitator",
    "veterinary",
    "feedback",
    "notifications",
    "django_cleanup.apps.CleanupConfig",
    "taggit",
]

THIRD_PARTY_APPS = [
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework",
    "widget_tweaks",
    "django_tables2",
    "bootstrap5",
    "django_filters",
    "django_celery_beat",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_ckeditor_5",
    "fontawesomefree",
    "import_export",
    "corsheaders",
]

ADMIN_APPS = [
    "daphne",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = ADMIN_APPS + LOCAL_APPS + THIRD_PARTY_APPS

SITE_ID = 1
THUMBNAIL_DEBUG = True
THUMBNAIL_FORMAT = "JPEG"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
ASGI_APPLICATION = "erp_master.asgi.application"

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

LANGUAGE_CODE = "en-us"

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("hi", _("Hindi")),
    # ("as", _("Assamese")),  # <-- custom
    # ("bn", _("Bengali")),
    # ("gu", _("Gujarati")),
    # ("kn", _("Kannada")),
    # ("kok", _("Konkani")),
    # ("ml", _("Malayalam")),
    # ("mr", _("Marathi")),
    # ("or", _("Odia")),
    # ("pa", _("Punjabi")),
    # ("ta", _("Tamil")),
    # ("te", _("Telugu")),
    ("ur", _("Urdu")),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

TIME_ZONE = "Asia/Kolkata"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

API_KEY_EXPIRATION_ALLOWED = False
# DATA_UPLOAD_MAX_NUMBER_FIELDS =5000
REST_FRAMEWORK = {
    # Global authentication classes
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # Default permission
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",  # JSON responses
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",  # JSON request parsing
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
        "anon": "50000/day",
        "otp": "2/minute",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ERP API",
    "DESCRIPTION": "API documentation for your ERP platform",
    "VERSION": "1.0.0",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=180),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365),
    "BLACKLIST_AFTER_ROTATION": True,
    "ROTATE_REFRESH_TOKENS": True,
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

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MONTHS = [
    _("January"),
    _("February"),
    _("March"),
    _("April"),
    _("May"),
    _("June"),
    _("July"),
    _("August"),
    _("September"),
    _("October"),
    _("November"),
    _("December"),
]
MONTH_FILTER = [
    ("January", "January"),
    ("February", "February"),
    ("March", "March"),
    ("April", "April"),
    ("May", "May"),
    ("June", "June"),
    ("July", "July"),
    ("August", "August"),
    ("September", "September"),
    ("October", "October"),
    ("November", "November"),
    ("December", "December"),
]
OPEN = "open"
CLOSED = "closed"
RE_OPENED = "re opened"

FEEDBACK_STATUS = [
    (OPEN, "Open"),
    (CLOSED, "Closed"),
    (RE_OPENED, "Re-opened"),
]

from .jazzmin_settings import *

customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "insertImage",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageUpload",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "any"

CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")
CELERY_RESULT_EXTENDED = True

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_TASK_DEFAULT_QUEUE = "erp_master_queue"

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_RESULT_EXPIRES = 3600

CELERY_TASK_QUEUES = {
    "erp_master_queue": {
        "exchange": "erp_exchange",
        "routing_key": "erp_task",
    }
}

CELERY_TASK_ROUTES = {
    "feedback.tasks.*": {"queue": "erp_master_queue", "routing_key": "erp_task"},
    "notifications.tasks.*": {"queue": "erp_master_queue", "routing_key": "erp_task"},
    "veterinary.tasks.*": {"queue": "erp_master_queue", "routing_key": "erp_task"},
}

# Email Configuration

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "HRMS <hrms@kasheemilk.com>"
HRMS_DEFAULT_FROM_EMAIL = "HRMS <hrms@kasheemilk.com>"

SUPPORT_TEAM_EMAIL = config("SUPPORT_TEAM_EMAIL")


EXCEL_IMPORT_SETTINGS = {
    "MAX_FILE_SIZE": 50 * 1024 * 1024,
    "ALLOWED_EXTENSIONS": [".xlsx", ".xls"],
    "MAX_PREVIEW_ROWS": 100,
    "TEMP_FILE_TIMEOUT": 3600,
    "DEFAULT_DATE_FORMAT": "%Y-%m-%d",
    "DEFAULT_DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}
