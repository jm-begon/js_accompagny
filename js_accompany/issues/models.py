from enum import Enum

from django.db import models
from django.contrib.auth.models import User

from model_utils.managers import InheritanceManager


class StateValue(Enum):
    opened = 'En cours'
    closed = 'Close'


class Issue(models.Model):
    title = models.CharField(max_length=255)

    @classmethod
    def new_issue(cls, title, user, content=None):
        issue = cls.objects.create(title=title)
        StateChanged.on_new_issue(user=user, issue=issue)
        if content is not None:
            MessagePosted.new_message(user=user, issue=issue, content=content)
        return issue

    def __str__(self):
        return '[Prob.] {}'.format(self.title)

    def get_actions(self, refresh=False):
        if refresh or not hasattr(self, '_actions'):
            self._actions = Action.objects.filter(
                issue__pk=self.pk).distinct().order_by('date',
                                                       'pk').select_subclasses()
        return self._actions

    def refresh_from_db(self, using=None, fields=None):
        super().refresh_from_db(using=using, fields=fields)
        self.get_actions(refresh=True)

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


class Action(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              related_name='%(class)s_owner')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    date = models.DateTimeField('Date de publication', auto_now_add=True)

    objects = InheritanceManager()

    def __str__(self):
        return "[Action] de type '{}' effectuée par {} en date du {} à " \
               "propos de {}".format(self.__class__.__name__,
                                     self.owner, self.date, self.issue)

    @property
    def owner_name(self):
        return self.owner.username


class StateChanged(Action):
    state = models.CharField(max_length=50, choices=[(tag.name, tag.value) for
                                                     tag in StateValue])

    @classmethod
    def on_new_issue(cls, user, issue):
        return cls.objects.create(owner=user, issue=issue,
                                  state=StateValue.opened.value)

    def __str__(self):
        return str(self.state)

    def is_closed(self):
        return self.state == StateValue.closed.name


class MessagePosted(Action):
    content = models.TextField(max_length=2048, blank=True)
    last_edited = models.DateTimeField('Dernière édition', null=True)

    @classmethod
    def new_message(cls, user, issue, content):
        return cls.objects.create(owner=user, issue=issue, content=content)

    def __str__(self):
        max_size = 100
        content = self.content
        if len(content) <= max_size:
            s = content
        else:
            s = content[:max_size - 3] + "..."
        return '[Message] {}...'.format(s)
