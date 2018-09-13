from django import template
from django.contrib.auth.models import User

from ..models import Referenceable, Tagable, Followhsip, Action, Notification

register = template.Library()


@register.filter
def absolute_url(value):
    if not hasattr(value, 'get_absolute_url'):
        raise ValueError("Object '{}' does not have a 'get_absolute_url' "
                         "method".format(repr(value)))
    return value.get_absolute_url()


@register.filter
def get_followships(value):
    if isinstance(value, User):
        followship = Followhsip.objects.filter(follower=value)
        return followship
    elif isinstance(value, Tagable):
        followship = Followhsip.objects.filter(tagable=value)
        return followship
    else:
        raise ValueError('Can only get followship for {} and {}'
                         ''.format(User.__name__, Tagable.__name__))


@register.filter
def get_tagable(value):
    # TODO do something faster
    tagable = Tagable.objects.get_subclass(pk=value.pk)
    return tagable


@register.filter
def long_name(value):
    return value.long_name


@register.filter
def short_name(value):
    return value.short_name


@register.filter
def prefere_short(value):
    return value.prefere_short


@register.filter
def slug(value):
    return value.slug


@register.filter
def get_notifications(value):
    if isinstance(value, User):
        return Notification.get_notifications(value)
    else:
        raise ValueError('Can only get notifications for \'\''
                         ''.format(User.__name__))


@register.filter
def has_notifications(value):
    if isinstance(value, User):
        return Notification.has_notifications(value)
    else:
        raise ValueError('Can only get notifications for \'\''
                         ''.format(User.__name__))

@register.filter
def string(value):
    return str(value)
