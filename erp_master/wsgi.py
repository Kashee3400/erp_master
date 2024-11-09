import os
from django.core.wsgi import get_wsgi_application

DEBUG = os.getenv("DEBUG", None)

if DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_master.settings.local')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_master.settings.production')


application = get_wsgi_application()
