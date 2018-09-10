from enum import Enum

from django.db import models

from tags.models import Action, Tagable


def clip(s, max_size=100):
    if len(s) > max_size:
        s = s[:max_size - 3] + "..."
    return s


class StateValue(Enum):
    opened = 'En cours'
    closed = 'Close'


class Issue(Tagable):
    title = models.CharField(max_length=255)

    @classmethod
    def new_issue(cls, title, user, content=None):
        issue = cls.objects.create(title=title)
        issue.trigger_action(user, StateChanged.on_new_issue)
        if content is not None:
            issue.trigger_action(user, MessagePosted.new_message,
                                 content=content)
        return issue

    def trigger_action(self, owner, action_factory, **kwargs):
        self.register_follower(owner)
        super().trigger_action(owner, action_factory, **kwargs)

    @property
    def long_name(self):
        return self.title

    @property
    def short_name(self):
        return clip(self.title, 50)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('issues.views.IssueDetailView',
                       args=[str(self.pk)])

    def __str__(self):
        return '[Prob.] {}'.format(self.title)

    @property
    def owner(self):
        return self.get_actions()[0].owner

    @property
    def owner_name(self):
        return self.owner.username

    @property
    def date(self):
        return self.get_actions()[0].date

    @property
    def state(self):
        for action in self.get_actions()[::-1]:
            if isinstance(action, StateChanged):
                return action
        raise ValueError('There is no state for this issue')

    def get_messages(self, refresh=False):
        return [a for a in self.get_actions(refresh)
                if isinstance(a, MessagePosted)]


class StateChanged(Action):
    state = models.CharField(max_length=50, choices=[(tag.name, tag.value) for
                                                     tag in StateValue])

    @classmethod
    def on_new_issue(cls, user, issue):
        return cls.objects.create(owner=user, issue=issue,
                                  state=StateValue.opened.value)

    @property
    def notif_message(self):
        return "Changement d'état: {}".format(self.state)

    def __str__(self):
        return str(self.state)

    def is_closed(self):
        return self.state == StateValue.closed.name


class MessagePosted(Action):
    content = models.TextField(max_length=2048, blank=True)
    last_edited = models.DateTimeField('Dernière édition', null=True)

    @classmethod
    def new_message(cls, owner, tag, content):
        return cls.objects.create(owner=owner, tag=tag, content=content)

    def get_content_or_trim(self, max_size=100):
        content = self.content
        if len(content) > max_size:
            content = content[:max_size - 3] + "..."
        return content

    def __str__(self):
        return '[Message] {}'.format(clip(self.content))

    @property
    def notif_message(self):
        return "Nouveau message: {}".format(clip(self.content))

