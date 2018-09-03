from django.urls import path

from . import views


app_name = 'issues'
urlpatterns = [
    path('', views.IssueListView.as_view(), name='index'),
    path('list', views.IssueListView.as_view(), name='list'),

]