from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ErpAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'erp_app'
    label = 'erp_app'
    verbose_name = _('Kashee ERP')

