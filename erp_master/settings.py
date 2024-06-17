from pathlib import Path
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()


# SECURITY WARNING: keep the secret key used in production secret!
# KEY = os.getenv('SECRET_KEY', None)
# if KEY:
#     SECRET_KEY = KEY
# else:
#     SECRET_KEY = 'django-insecure-+q&lga%@fxkh0q8q7l89f0y+!w9rd5ytfxz5z(^+*!thf))73j'

SECRET_KEY = 'django-insecure-+q&lga%@fxkh0q8q7l89f0y+!w9rd5ytfxz5z(^+*!thf))73j'

BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = True
# DEBUG = False
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["1.22.197.176"]
    
INSTALLED_APPS = [
    'erp_app',
    'member',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'erp_app.login_middleware.LoginRequiredMiddleware',
    
]

DATABASE_ROUTERS = ['erp_app.dbrouters.SarthakKasheeRouter']

ROOT_URLCONF = 'erp_master.urls'

API_URL_PREFIX = ['/api/']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'erp_master.wsgi.application'


DB_ENGINE = os.getenv('DB_ENGINE', None)

# cred for connecting sarthak db
DB_USER_SARTHAK = os.getenv('DB_USER_SARTHAK', None)
DB_PASSWORD_SARTHAK = os.getenv('DB_PASSWORD_SARTHAK', None)
DB_NAME_SARTHAK = os.getenv('DB_NAME_SARTHAK', None)

#cred for connecting member db

DB_NAME_MEMBER = os.getenv('DB_NAME_MEMBER', None)
DB_MEMBER_USER = os.getenv('DB_MEMBER_USER', None)
DB_MEMBER_PASS = os.getenv('DB_MEMBER_PASS', None)

DB_HOST = os.getenv('DB_HOST', None)
DB_PORT = os.getenv('DB_PORT', None)

if not DEBUG:    
    if DB_ENGINE:
        DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'member',
            'USER': 'root',
            'PASSWORD': '12345@Kashee',
            'HOST': 'localhost',
            'PORT': '3306',
        },
        'sarthak_kashee': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME_SARTHAK,
            'USER': DB_USER_SARTHAK,
            'PASSWORD': DB_PASSWORD_SARTHAK,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
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
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME_SARTHAK,
        'USER': DB_USER_SARTHAK,
        'PASSWORD': DB_PASSWORD_SARTHAK,
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
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'error.log'),  # Path to your error log file
                'maxBytes': 1024 * 1024 * 10,  # 10 MB
                'backupCount': 5,  # Keep up to 5 previous log files
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
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
# STATIC_URL="staticfiles/"
STATIC_ROOT="static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100

}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
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

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}