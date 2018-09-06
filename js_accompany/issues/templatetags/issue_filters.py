from django import template
from ..models import Issue, IssueMessage, IssueState, StateValue

register = template.Library()


@register.filter
def author_name(value):
    if isinstance(value, Issue):
        return value.get_author().username
    elif isinstance(value, IssueMessage):
        return value.author.username
    else:
        raise ValueError('Can only extract author from {} or {}'
                         ''.format(Issue.__class__.__name__,
                                   IssueMessage.__class__.__name__))


@register.filter
def pub_date(value):
    if isinstance(value, Issue):
        return value.get_publication_date()
    elif isinstance(value, IssueMessage):
        return value.pub_date
    else:
        raise ValueError('Can only extract publication date from {} or {}'
                         ''.format(Issue.__class__.__name__,
                                   IssueMessage.__class__.__name__))


@register.filter
def state(value):
    if isinstance(value, IssueState):
        return value.get_name()
    elif isinstance(value, Issue):
        return value.get_state_name()
    else:
        raise ValueError('Can only extract state from {} or {}'
                         ''.format(Issue.__class__.__name__,
                                   IssueState.__class__.__name__))


@register.filter
def is_closed(value):
    if isinstance(value, IssueState):
        return value.is_closed()
    elif isinstance(value, Issue):
        return value.state.is_closed()
    else:
        raise ValueError('Can only extract state from {} or {}'
                         ''.format(Issue.__class__.__name__,
                                   IssueState.__class__.__name__))


@register.filter
def messages(value, update=False):
    return value.get_messages(update)
