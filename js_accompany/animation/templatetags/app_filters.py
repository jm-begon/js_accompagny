from django import template

register = template.Library()


@register.filter
def id_str(value):
    return '{}_{}'.format(value.__class__.view_name, value.id)

@register.filter
def url(value):
    # TODO something more robust
    return value.get_list_url()
