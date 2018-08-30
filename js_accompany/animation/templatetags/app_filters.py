from django import template

register = template.Library()


@register.filter
def id_str(value):
    return '{}_{}'.format(value.__class__.linkable_name, value.id)
