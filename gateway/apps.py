from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GatewayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gateway'
    label = 'gateway'
    verbose_name = _('Payment Gateway')

