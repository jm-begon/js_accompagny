from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.template.context_processors import csrf
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from tags.models import Notification
from .forms import MyRegistrationForm


class MyLogin(auth_views.LoginView):
    pass


def signup(request):
    if request.user.is_authenticated:
        # return redirect(settings.LOGIN_REDIRECT_URL)
        return redirect('accounts:success_signup')

    context = {}
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:success_signup')

    else:
        form = MyRegistrationForm()

    context['form'] = form
    context.update(csrf(request))
    context['is_signup'] = True

    return render(request, 'accounts/signup.html', context)


def serve_template(template_name, context=None):
    if context is None:
        context = {}

    def handle_request(request):
        return render(request, template_name, context)
    return handle_request


@login_required
def settings(request):
    return render(request, 'accounts/settings.html', {})


def notifications(request):
    Notification.mark_all_as_seen(request.user)
    return HttpResponseRedirect(
        '{}#{}'.format(reverse('accounts:settings'), 'Notifications')
    )
