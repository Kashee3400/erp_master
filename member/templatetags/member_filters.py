from django import template
from django.apps import apps

register = template.Library()

@register.inclusion_tag('member/filters/filter_layout.html')
def filter_layout(model_name):
    # Get the model class dynamically
    model = apps.get_model('member', model_name)
    
    # Retrieve the fields from the model
    fields = [field.name for field in model._meta.get_fields() if not field.is_relation]
    
    return {'fields': fields}
