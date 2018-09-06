from enum import Enum

from django.db import models
from django.contrib.auth.models import User


class StateValue(Enum):
    opened = 'En cours'
    closed = 'Close'


class IssueState(models.Model):
    name = models.CharField(max_length=50, choices=[(tag, tag.value) for
                                                    tag in StateValue])

    def get_name(self):
        name = self.name
        if name is None:
            name = StateValue.opened
        return name

    def is_closed(self):
        return self.name == StateValue.closed.value

    def __str__(self):
        return '[Etat] {}'.format(self.get_name())


class Issue(models.Model):
    title = models.CharField(max_length=255)
    state = models.ForeignKey(IssueState, on_delete=models.SET_NULL, null=True)
    assignees = models.ManyToManyField(User, related_name='assigned_%(class)s',
                                       blank=True)

    def __str__(self):
        return '[Prob.] {}'.format(self.title)

    @property
    def first_message(self):
        if not hasattr(self, '_first_message'):
            messages = self.get_messages()
            self._first_message = messages[0]
        return self._first_message

    def get_messages(self, update=False):
        if update or not hasattr(self, '_messages'):
            self._messages = IssueMessage.objects.filter(issue=self).order_by('pub_date')
        self._first_message = self._messages[0]
        return self._messages

    def get_author(self):
        return self.first_message.author

    def get_publication_date(self):
        return self.first_message.pub_date

    def get_participants(self):
        messages = self.get_messages()
        return messages.values('author').distinct('author')

    def get_state_name(self):
        return self.state.get_name()


class IssueMessage(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                               related_name='%(class)s_creator')
    pub_date = models.DateTimeField('Date de publication', auto_now_add=True)
    unread_by = models.ManyToManyField(User, related_name='unread_by_%(class)s',
                                       blank=True)
    content = models.TextField(max_length=2048, blank=True)

    def __str__(self):
        max_size = 100
        content = self.content
        if len(content) <= max_size:
            s = content
        else:
            s = content[:max_size-3] + "..."
        return '[Message] {}...'.format(s)
