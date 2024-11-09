from pathlib import Path
from django.conf import settings
import os
from dotenv import load_dotenv
from typing import Any, Dict

load_dotenv()
from django.utils.translation import gettext_lazy as _

SECRET_KEY = 'django-insecure-+q&lga%@fxkh0q8q7l89f0y+!w9rd5ytfxz5z(^+*!thf))73j'

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

DEBUG = False
# DEBUG = True


# URL for login
LOGIN_URL = '/admin/login/'

LOGIN_REDIRECT_URL = '/admin/'


if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["1.22.197.176"]


INSTALLED_APPS = [
    'member',
    'mpms',
    'erp_app',
    "bootstrap5",
    'django_filters',
    'crispy_forms',
    "crispy_bootstrap5",
    'fontawesomefree',
    'import_export',
    'jazzmin',
    "django.contrib.admin",
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework',
    'widget_tweaks',
    'django_tables2',
]

SITE_ID = 1
THUMBNAIL_DEBUG = True
THUMBNAIL_FORMAT = 'JPEG'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'erp_app.login_middleware.LoginRequiredMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    "member.middleware.CurrentRequestMiddleware",
]

DATABASE_ROUTERS = ['erp_app.dbrouters.SarthakKasheeRouter','mpms.db_routers.MPMSDBRouter']


ROOT_URLCONF = 'erp_master.urls'

API_URL_PREFIX = ['/api/']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
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

WSGI_APPLICATION = 'erp_master.wsgi.application'


DB_ENGINE = os.getenv('DB_ENGINE', None)

# cred for connecting sarthak db
DB_NAME_SARTHAK = os.getenv('DB_NAME_SARTHAK', None)
DB_USER_SARTHAK = os.getenv('DB_USER_SARTHAK', None)
DB_PASSWORD_SARTHAK = os.getenv('DB_PASSWORD_SARTHAK', None)
DB_HOST_SARTHAK = os.getenv('DB_HOST_SARTHAK', None)
DB_PORT_SARTHAK = os.getenv('DB_PORT_SARTHAK', None)


#cred for connecting member db
DB_NAME_MEMBER = os.getenv('DB_NAME_MEMBER', None)
DB_MEMBER_USER = os.getenv('DB_MEMBER_USER', None)
DB_MEMBER_PASS = os.getenv('DB_MEMBER_PASS', None)
DB_HOST_MEMBER = os.getenv('DB_HOST_MEMBER', None)
DB_PORT_MEMBER = os.getenv('DB_PORT_MEMBER', None)

#cred for connecting mpms db
DB_NAME_MPMS = os.getenv('DB_NAME_MPMS', None)
DB_USER_MPMS = os.getenv('DB_USER_MPMS', None)
DB_PASSWORD_MPMS = os.getenv('DB_PASSWORD_MPMS', None)
DB_HOST_MPMS = os.getenv('DB_HOST_MPMS', None)
DB_PORT_MPMS = os.getenv('DB_PORT_MPMS', None)

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME_MEMBER,
            'USER': DB_MEMBER_USER,
            'PASSWORD': DB_MEMBER_PASS,
            'HOST': DB_HOST_MEMBER,
            'PORT': DB_PORT_MEMBER,
        },
        'sarthak_kashee': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME_SARTHAK,
            'USER': DB_USER_SARTHAK,
            'PASSWORD': DB_PASSWORD_SARTHAK,
            'HOST': DB_HOST_SARTHAK,
            'PORT': DB_PORT_SARTHAK,
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        },
        'mpms_db': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME_MPMS,
            'USER': DB_USER_MPMS,
            'PASSWORD': DB_PASSWORD_MPMS,
            'HOST': DB_HOST_MPMS,
            'PORT': DB_PORT_MPMS,
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'sqlite3.db'),
        },
        'sarthak_kashee': {
            'ENGINE': 'mssql',
            'NAME': 'sarthak_kashee',
            'USER': 'sarthak',
            'PASSWORD': '123',
            'HOST': '10.10.11.2',
            'PORT': 1433,
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        },
        'mpms_db': {
            'ENGINE': 'mssql',
            'NAME': 'kanha_Procurement',
            'USER': 'sarthak',
            'PASSWORD': '123',
            'HOST': '10.10.11.2',
            'PORT': 1433,
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        },
    }

import os

LOG_DIR = os.path.join(BASE_DIR, 'logs')  # Adjust this path if necessary
os.makedirs(LOG_DIR, exist_ok=True)

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'handlers': ['console', 'file'],  # Added 'file' handler
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
            },
            'simple': {
                'format': '[%(asctime)s] %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'file': {  # Added file handler for error logging
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': os.path.join(LOG_DIR, 'error.log'),
                'formatter': 'verbose',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'filters': ['require_debug_false'],
            },
        },
        'loggers': {
            # Django loggers
            'django': {
                'propagate': True,
            },
            'django.db': {
                'level': 'WARNING'
            },
            'django.request': {
                'handlers': ['mail_admins', 'file'],  # Log errors to file as well
                'level': 'ERROR',
                'propagate': False
            },
            'sorl.thumbnail': {
                'level': 'ERROR',
            },
            # Suppress output of this debug toolbar panel
            'template_timings_panel': {
                'handlers': ['null'],
            }
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

# LANGUAGE_CODE = 'hi-IN'
LANGUAGE_CODE = 'en-us'

USE_L10N = True

LANGUAGES = [
    ('hi', 'Hindi'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

if DEBUG:
    STATICFILES_DIRS = [STATIC_DIR] 
else:
    STATIC_ROOT="staticfiles/"

MEDIA_URL="/media/"
MEDIA_ROOT=os.path.join(BASE_DIR,"media/")
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365 * 10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=150),
    "ROTATE_REFRESH_TOKENS": False,
    'BLACKLIST_AFTER_ROTATION': True,
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


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
import requests
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


JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Kashee ERP Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Kashee ERP",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Kashee ERP",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "member/assets/img/kashee_logo.png",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "member/assets/img/kashee_login_logo.png",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": "member/assets/img/kashee_login_logo.png",

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": "member/assets/img/small-logos/icon-sun-cloud.png",

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the kashee ERP",

    # Copyright on the footer
    "copyright": "Kashee Milk Producer Company LTD",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string 
    "search_model": ["auth.User", "auth.Group","member.OTP"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # Url that gets reversed (Permissions can be added)
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

        # external url that opens in a new window (Permissions can be added)
        {"name": "View Site", "url": "/", "new_window": True},

        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "member"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],

    # Custom links to append to app groups, keyed on app name
    # "custom_links": {
    #     "books": [{
    #         "name": "Make Messages", 
    #         "url": "make_messages", 
    #         "icon": "fas fa-comments",
    #         "permissions": ["books.view_book"]
    #     }]
    # },

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "carousel", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": True,
}


JAZZMIN_UI_TWEAKS = {
#     # "navbar_small_text": True,
#     # "footer_small_text": True,
#     # "body_small_text": True,
#     # "brand_small_text": True,
#     # "brand_colour": "navbar-lights",
#     # "accent": "accent-primary",
#     # "navbar": "navbar-navy navbar-dark",
#     # "no_navbar_border": True,
#     # "navbar_fixed": True,
#     # "layout_boxed": False,
#     # "footer_fixed": True,
#     # The above code snippet appears to be a comment in a Python file. It mentions a key-value pair
#     # "footer_fixed" with a boolean value of True. This could potentially be a configuration setting
#     # for a website or application, indicating that the footer should be fixed in its position on the
#     # page. However, without more context or surrounding code, it is difficult to determine the exact
#     # purpose or functionality of this specific code snippet.
    "sidebar_fixed": True,
#     # "sidebar": "sidebar-light-navy ",
#     # "sidebar_nav_small_text": False,
#     # "sidebar_disable_expand": False,
#     # "sidebar_nav_child_indent": False,
#     # "sidebar_nav_compact_style": False,
#     # "sidebar_nav_legacy_style": False,
#     # "sidebar_nav_flat_style": True,
#     "theme": "slate",
#     # "dark_mode_theme": None,
#     # "button_classes": {
#     #     "primary": "btn-primary",
#     #     "secondary": "btn-secondary",
#     #     "info": "btn-info",
#     #     "warning": "btn-warning",
#     #     "danger": "btn-danger",
#     #     "success": "btn-success"
#     # }
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MONTHS = [
            "January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"
        ]