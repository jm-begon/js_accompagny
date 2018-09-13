from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from .views import MyLogin, signup, serve_template, settings, notifications


app_name = 'accounts'
# https://docs.djangoproject.com/fr/2.1/topics/auth/default/#using-the-views
urlpatterns = [
    path('login/', MyLogin.as_view(template_name='accounts/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', signup, name='signup'),
    path('success_signup/', serve_template('accounts/success_signup.html'), name='success_signup'),

    re_path(r'^settings/$', settings, name='settings'),
    # re_path(r'^settings/(?P<slug>[\w-]+)/$', settings, name='settings'),
    path('notifications/', notifications, name='notifications')
]

