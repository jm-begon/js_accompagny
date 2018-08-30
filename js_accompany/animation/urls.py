from django.urls import path

from . import views
from . import models


app_name = 'animation'
urlpatterns = [
    path('', views.fields, name='index'),
    path(models.Field.linkable_name, views.fields, name=models.Field.linkable_name),
    path(models.Training.linkable_name, views.trainings, name=models.Training.linkable_name),
    path(models.Module.linkable_name, views.modules, name=models.Training.linkable_name),
    path(models.Skill.linkable_name, views.skills, name=models.Skill.linkable_name),
    path(models.Criterion.linkable_name, views.criteria, name=models.Criterion.linkable_name),
    path('todo', views.unassigned, name='todo')

]