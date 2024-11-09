import os
from django.core.asgi import get_asgi_application
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_master.settings.local')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_master.settings.production')


application = get_asgi_application()
