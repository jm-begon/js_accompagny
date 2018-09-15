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
        Followship.objects.get_or_create(follower=follower, tagable=self)

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

    def create_tag(self, owner, tagable=None):
        a1 = self.trigger_action(owner, TagCreation)
        a2 = None
        if tagable is not None \
                and isinstance(tagable, Tagable):
            a2 = tagable.trigger_action(owner, TagSomething, tag_about=self)
        return a1, a2


class Followship(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    tagable = models.ForeignKey(Tagable, on_delete=models.CASCADE)
    notify = models.BooleanField(default=True)

    @classmethod
    @transaction.atomic
    def add_or_renew(cls, user, tagable):
        if isinstance(tagable, Tagable):
            followship, created = Followship.objects.get_or_create(
                follower=user,
                tagable=tagable)
        else:
            # tagable is actually the key
            tagable_pk = tagable
            followship, created = Followship.objects.get_or_create(
                follower=user,
                tagable_id=tagable_pk)
        if not created:
            followship.notify = True  # Notify is true by default
            followship.save()

    def __str__(self):
        return '[Follow {}] {} {} {}'.format(self.pk, self.follower.username,
                                             'suit' if self.notify else
                                             'ne suit pas',
                                             self.tagable.short_name)

    def __repr__(self):
        return "{cls}(follower={follower}, tagable={tagable}, notify={notify})" \
               "".format(cls=self.__class__.__name__,
                         follower=repr(self.follower),
                         tagable=repr(self.tagable),
                         notify=repr(self.notify))


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
    def true_tag(self):
        if not hasattr(self, '_true_tag'):
            self._true_tag = Tagable.objects.filter(
                pk=self.tag.pk
            ).select_subclasses()[0]
        return self._true_tag

    @property
    def owner_name(self):
        return self.owner.username

    @property
    def notif_message(self):
        return '???'

    @property
    def goto(self):
        return self.true_tag.get_absolute_url()

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
        for follow_rel in Followship.objects.filter(tagable=self.tag,
                                                    notify=True):
            follower = follow_rel.follower
            if follower.pk != self.owner.pk:
                # Do not notify owner of the action
                Notification.objects.create(action=self, recipient=follower)


class TagCreation(Action):
    """This represents the creation of tag referencing a given tageable from
    the outisde. The tag field must reference the target Tageable"""
    @property
    def notif_message(self):
        return "Creation d'un nouveau tag"


class TagSomething(Action):
    """This represents a tageable being tagged"""
    tag_about = models.ForeignKey(Tagable, on_delete=models.CASCADE)

    @property
    def get_tag_about(self):
        return Tagable.objects.select_subclasses().get(pk=self.tag_about.pk)

    @property
    def notif_message(self):
        tag = self.get_tag_about
        msg = tag.short_name if tag.prefere_short else tag.long_name
        return "Creation d'un tag: {}".format(msg)

    def __str__(self):
        return super().__str__() + " --> {}".format(self.tag_about)


class Notification(models.Model):
    """
    seen_on is null until it is seen by the user
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    seen_on = models.DateTimeField('Vu', null=True)

    @classmethod
    def get_notifications(cls, user, only_unseen=False):
        # TODO do better
        if only_unseen:
            notifs = Notification.objects.filter(recipient=user, seen_on=None)
        else:
            notifs = Notification.objects.filter(recipient=user)
        notifs = notifs.order_by('-pk')
        return notifs

    @classmethod
    def get_actions(cls, user, only_unseen=False):
        # TODO do better
        if only_unseen:
            action_ids = Notification.objects.filter(recipient=user, seen_on=None).values('action')
        else:
            action_ids = Notification.objects.filter(recipient=user).values('action')
        actions = Action.objects.filter(pk__in=action_ids).select_subclasses()
        return actions

    @classmethod
    def has_notifications(cls, user):
        return len(Notification.objects.filter(recipient=user,
                                               seen_on=None)) > 0

    @classmethod
    def mark_all_as_seen(cls, user):
        Notification.objects.filter(recipient=user, seen_on=None).update(seen_on=datetime.now())

    def mark_as_seen(self):
        self.seen_on = datetime.now()

    @property
    def true_action(self):
        if not hasattr(self, '_true_action'):
            self._true_action = Action.objects.filter(
                pk=self.action.pk
            ).select_subclasses()[0]
        return self._true_action

    @property
    def has_been_seen(self):
        return self.seen_on is not None

    def __str__(self):
        return '[Notif.] pour {}{} concernant {}' \
               ''.format(self.recipient,
                         '' if self.seen_on is None \
                             else ' (vu le {})'.format(self.seen_on),
                         self.action)
