from django.urls import path

from . import views


app_name = 'issues'
urlpatterns = [
    path('', views.IssueListView.as_view(), name='issue-list'),
    path('<int:pk>/', views.IssueDetailView.as_view(), name='issue-detail'),


]