from django.db import models
from django.contrib.auth.models import User

__STATES__ = ['En cours', 'Close']


class IssueState(models.Model):
    name = models.CharField(max_length=50)

    def get_name(self):
        name = self.name
        if name is None:
            name = __STATES__[0]
        return name

    def __str__(self):
        return '[Etat] {}'.format(self.get_name())


class Issue(models.Model):
    title = models.CharField(max_length=255)
    state = models.ForeignKey(IssueState, on_delete=models.SET_NULL, null=True)
    assignees = models.ManyToManyField(User, related_name='assigned_%(class)s',
                                       blank=True)
    participants = models.ManyToManyField(User,
                                          related_name='%(class)s_participating')

    def __str__(self):
        return '[Rem] {}'.format(self.title)


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
        if len(content <= max_size):
            s = content
        else:
            s = content[:max_size-3] + "..."
        return '[Message] {}...'.format(s)

