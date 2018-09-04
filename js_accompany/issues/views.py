from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import permission_required


from .models import Issue, IssueState, __STATES__


class IssueListView(ListView):
    # https://docs.djangoproject.com/fr/2.1/ref/class-based-views/generic-display/

    model = Issue
    paginate_by = None  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['object_list'] = context['object_list'].orderby()
        context['now'] = timezone.now()
        return context


class IssueDetailView(DetailView):

    model = Issue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@permission_required('issues.add_issue')
def create_issue(request):
    return render(request, 'issues/new_issue.html')


@permission_required('issues.add_issue')
def save_issue(request):
    # https://docs.djangoproject.com/fr/2.1/intro/tutorial04/
    try:
        print("Method", request.method)
        print("Get", request.GET)
        print("Post:", request.POST)
        title = request.POST['title']
    except KeyError:
        return render(request, "issues/new_issue.html",
                      {'title_error': True})

    print("Title:", title)

    state = IssueState.objects.get(name=__STATES__[0])
    Issue.objects.create(title=title, state=state)
    return HttpResponseRedirect(reverse('issues:issue-list'))

