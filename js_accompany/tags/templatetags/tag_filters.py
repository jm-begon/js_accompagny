from django import template
from django.contrib.auth.models import User

from ..models import Referenceable, Tagable, Followship, Action, Notification

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
        followships = Followship.objects.filter(follower=value)
        return followships
    elif isinstance(value, Tagable):
        followships = Followship.objects.filter(tagable=value)
        return followships
    else:
        raise ValueError('Can only get followship for {} and {} (got {})'
                         ''.format(User.__name__, Tagable.__name__,
                                   value.__class__.__name__))


@register.filter
def get_tagable(value):
    if isinstance(value, Tagable):
        # TODO do something faster
        tagable = Tagable.objects.get_subclass(pk=value.pk)
    elif isinstance(value, Followship):
        tagable = Tagable.objects.get_subclass(pk=value.tagable.pk)
    elif isinstance(value, Action):
        tagable = Tagable.objects.get_subclass(pk=value.tag.pk)
    else:
        raise ValueError('Can only get tagable for {}, {} and {} (got {})'
                         ''.format(Tagable.__name__, Followship.__name__,
                                   Action.__name__, value.__class__.__name__))
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
def prefered_name(value):
    return value.short_name if value.prefere_short else value.long_name


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
