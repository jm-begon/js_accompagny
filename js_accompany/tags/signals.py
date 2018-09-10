from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from js_accompany.tags.models import Tagable

# https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html
# https://docs.djangoproject.com/en/2.1/topics/signals/
# https://docs.djangoproject.com/en/2.1/ref/signals/#m2m-changed


def subclasses(cls):
    classes = set()
    nodes = [cls]
    while len(nodes) > 0:
        cls = nodes.pop()
        for subcls in cls.__subclasses__():
            if subcls not in classes:
                classes.add(subcls)
                nodes.append(subcls)
    return classes


def receiver_subclasses(signal, sender, dispatch_uid_prefix, **kwargs):
    # https://web.archive.org/web/20120715042306/http://codeblogging.net/blogs/1/14
    """
    A decorator for connecting receivers and all receiver's subclasses to signals. Used by passing in the
    signal and keyword arguments to connect::

        @receiver_subclasses(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...
    """
    def _decorator(func):
        for sender_ in subclasses(sender):
            signal.connect(func, sender=sender_,
                           dispatch_uid='{}_{}'.format(dispatch_uid_prefix,
                                                       sender.__name__),
                           **kwargs)
        return func
    return _decorator

# @receiver_subclasses(m2m_changed, sender=Tageable,
#                      dispatch_uid_prefix="handling_tageable_m2m")
# def tag_signal_handler(sender, action, instance, reverse, model, pk_set,
#                        **kwargs):
#     if action == "post_add":
#         # Since it is NOT the Tageable model which holds the m2m rel.:
#         #  - reverse==True: it is accessed from the Tageable --> instance is
#         #      the Tageable
#         #  - reverse==False: it is NOT accessed from the Tageable --> get
#         #      Tageable instance from the pk_set. Also, model is the Tageable
#         #      subclass
#         if reverse:
#             tageable = instance
#         else:
#             model.get