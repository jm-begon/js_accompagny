from django import template

from ..models import Referenceable

register = template.Library()


@register.filter
def absolute_url(value):
    if not hasattr(value, 'get_absolute_url'):
        raise ValueError("Object '{}' does not have a 'get_absolute_url' "
                         "method".format(value))
    return value.get_absolute_url()