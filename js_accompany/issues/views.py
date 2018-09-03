from django.shortcuts import render
from django.utils import timezone
from django.views.generic.list import ListView

from .models import Issue


class IssueListView(ListView):
    # https://docs.djangoproject.com/fr/2.1/ref/class-based-views/generic-display/

    model = Issue
    paginate_by = None  # if pagination is desired

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super().get_context_data(**kwargs)
        print(context)
        context['now'] = timezone.now()
        return context
