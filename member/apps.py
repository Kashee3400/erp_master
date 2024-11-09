from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MemberConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'member'
    label = 'member'
    verbose_name = _('Kashee Member')
