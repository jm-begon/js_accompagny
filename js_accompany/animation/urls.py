from django.urls import path, re_path

from . import views
from . import models

app_name = 'animation'
urlpatterns = [
    path('', views.fields, name='index'),

    re_path(r'^axes/$', views.fields, name=models.Field.view_name),
    re_path(r'^axes/(?P<slug>[\w-]+)/$', views.fields, name=models.Field.view_name),

    re_path(r'^formations/$', views.trainings, name=models.Training.view_name),
    re_path(r'^formations/(?P<slug>[\w-]+)/$', views.trainings, name=models.Training.view_name),

    re_path(r'^competences/$', views.skills, name=models.Skill.view_name),
    re_path(r'^competences/(?P<slug>[\w-]+)/$', views.skills, name=models.Skill.view_name),

    re_path(r'^modules/$', views.modules, name=models.Module.view_name),
    re_path(r'^modules/(?P<slug>[\w-]+)/$', views.modules, name=models.Module.view_name),

    re_path(r'^criteres/$', views.criteria, name=models.Criterion.view_name),
    re_path(r'^criteres/(?P<slug>[\w-]+)/$', views.criteria, name=models.Criterion.view_name),

    path('todo', views.unassigned, name='todo'),
]