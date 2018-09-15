from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views import View

from .models import Followship, Tagable


def refuse(msg):
    return JsonResponse({'message': msg}, status=403)


def accept(msg):
    return JsonResponse({'message': msg})


class JsonReturn(JsonResponse):

    def __init__(self, message, http_code=None, data=None, **kwargs):
        if data is None:
            data = {}
        data['message'] = message
        if http_code is not None:
            kwargs['status'] = http_code
        super().__init__(data, **kwargs)


class NotAllowedJson(JsonReturn):

    def __init__(self, message, data, **kwargs):
        super().__init__(message, 403, data, **kwargs)


@login_required
def remove_followship(request, followship_pk):
    followship = Followship.objects.get(pk=followship_pk)
    if followship.follower != request.user:
        return NotAllowedJson('Un utilisateur ne peut désabonner que lui-même')
    followship.notify = False
    followship.save()
    return JsonReturn('Abonnement supprimé')


@login_required
def add_followship(request, tagable_pk):
    if not request.user.has_perm('tags.add_followship'):
        return NotAllowedJson('Vous ne pouvez pas ajouter d\'abonnement')
    tag = Tagable.objects.filter(pk=tagable_pk).select_subclasses()[0]
    print('add_followship', tagable_pk, tag)
    Followship.add_or_renew(request.user, tagable_pk)
    return JsonReturn('Abonnement ajouté')
