from django.urls import path
from django.contrib.auth import views as auth_views

from .views import MyLogin, signup, serve_template


app_name = 'accounts'
# https://docs.djangoproject.com/fr/2.1/topics/auth/default/#using-the-views
urlpatterns = [
    path('login/', MyLogin.as_view(template_name='accounts/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', signup, name='signup'),
    path('success_signup/', serve_template('accounts/success_signup.html'), name='success_signup'),
]

