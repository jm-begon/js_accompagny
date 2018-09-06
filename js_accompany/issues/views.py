from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import permission_required
from django.db import transaction

from .models import Issue, IssueState, StateValue, IssueMessage


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


@permission_required('issues.add_issue', raise_exception=True)
def create_issue(request):
    return render(request, 'issues/new_issue.html')


@transaction.atomic
@permission_required('issues.add_issue', raise_exception=True)
def save_issue(request):
    # https://docs.djangoproject.com/fr/2.1/intro/tutorial04/
    try:
        title = request.POST['title']
    except KeyError:
        return render(request, "issues/new_issue.html",
                      {'title_error': True})

    state = IssueState.objects.get(name=StateValue.opened)

    issue = Issue.objects.create(title=title, state=state)
    IssueMessage.objects.create(issue=issue, author=request.user,
                                content=request.POST['message_content'])
    return HttpResponseRedirect(reverse('issues:issue-list'))


@transaction.atomic
@permission_required('issues.add_issuemessage', raise_exception=True)
def add_message(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    try:
        content = request.POST['message_content']
        if content is None or len(content) == 0:
            raise ValueError('Le message ne peut pas être vide')
    except (KeyError, ValueError) as err:
        return render(request, "issues/issue_detail.html",
                      {'object': issue, 'error_message': str(err)})

    IssueMessage.objects.create(issue=issue, author=request.user,
                                content=content)
    return HttpResponseRedirect(reverse('issues:issue-detail', args=(issue.id,)))




