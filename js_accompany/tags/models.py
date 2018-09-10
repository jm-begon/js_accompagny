from datetime import datetime

from django.db import models, transaction
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


from model_utils.managers import InheritanceManager


class Referenceable(models.Model):
    objects = InheritanceManager()

    @property
    def long_name(self):
        return ""

    @property
    def short_name(self):
        return self.slug

    @property
    def prefere_short(self):
        return False

    @property
    def slug(self):
        """Return a slug used for anchoring"""
        return slugify('{}_{}'.format(self.__class__.__name__, self.pk))

    def get_absolute_url(self):
        pass


class Tagable(Referenceable):

    def register_follower(self, follower):
        """"re-entrant friendly"""
        Followhsip.objects.get_or_create(follower=follower, tagable=self)

    def get_actions(self, refresh=False):
        if refresh or not hasattr(self, '_actions') or self._actions is None:
            self._actions = Action.objects.filter(
                tag__pk=self.pk).distinct().order_by('date',
                                                     'pk').select_subclasses()
        return self._actions

    def refresh_from_db(self, using=None, fields=None):
        super().refresh_from_db(using=using, fields=fields)
        self.get_actions(refresh=True)

    def __iter__(self):
        return iter(self.get_actions())

    def trigger_action(self, owner, action_factory, **kwargs):
        action = action_factory(owner=owner, tag=self, **kwargs)
        action.save()
        return action

    def create_tag(self, owner, referenceable=None):
        a1 = self.trigger_action(owner, TagCreation)
        a2 = None
        if referenceable is not None \
                and isinstance(referenceable, Referenceable):
            a2 = self.trigger_action(owner, Tagged, tagged_by=referenceable)
        return a1, a2


class Followhsip(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    tagable = models.ForeignKey(Tagable, on_delete=models.CASCADE)
    notify = models.BooleanField(default=True)

    def __str__(self):
        return '[Follow] {} {} {}'.format(self.follower.username,
                                          'suit' if self.notify else
                                          'ne suit pas',
                                          self.tagable.short_name)


class Action(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              related_name='%(class)s_owner')
    tag = models.ForeignKey(Tagable, on_delete=models.CASCADE)
    date = models.DateTimeField('Date de publication', auto_now_add=True)

    objects = InheritanceManager()

    def __str__(self):
        return "[Action] de type '{}' effectuée par {} en date du {} à " \
               "propos de {}".format(self.__class__.__name__,
                                     self.owner, self.date, self.tag)

    @property
    def owner_name(self):
        return self.owner.username

    @property
    def notif_message(self):
        return '???'

    @property
    def goto(self):
        return self.tag.get_absolute_url()

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
        for follow_rel in Followhsip.objects.filter(tagable=self.tag,
                                                    notify=True):
            follower = follow_rel.follower
            if follower.pk != self.owner.pk:
                # Do not notify owner of the action
                Notification.objects.create(action=self, recipient=follower)


class TagCreation(Action):
    """This represents the creation of tag referencing a given tageable from
    the outisde"""
    @property
    def notif_message(self):
        return "Creation d'un nouveau tag"


class Tagged(Action):
    """This represents a tageable being tagged"""
    tagged_by = models.ForeignKey(Referenceable, on_delete=models.CASCADE)

    @property
    def notif_message(self):
        return "Taggué"


class Notification(models.Model):
    """
    seen_on is null until it is seen by the user
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    seen_on = models.DateTimeField('Vu', null=True)

    def mark_as_seen(self):
        self.seen_on = datetime.now()

    def __str__(self):
        return '[Notif.] pour {}{} concernant {}' \
               ''.format(self.recipient,
                         '' if self.seen_on is None \
                             else ' (vu le {})'.format(self.seen_on),
                         self.action)





