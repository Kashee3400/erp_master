from pathlib import Path
from django.conf import settings
import os
from dotenv import load_dotenv
load_dotenv()
from django.utils.translation import gettext_lazy as _

SECRET_KEY = 'django-insecure-+q&lga%@fxkh0q8q7l89f0y+!w9rd5ytfxz5z(^+*!thf))73j'

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# DEBUG = False
DEBUG = True


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
    'fontawesomefree',
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

if not DEBUG:
    LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'DEBUG' if DEBUG else 'INFO',
        'handlers': ['console', ],
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
            'handlers': ['mail_admins', ],
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
    "SIGNING_KEY": settings.SECRET_KEY,
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
