from django.urls import path, re_path

from .views import remove_followship, add_followship


app_name = 'tags'
urlpatterns = [
    path('api/remove_followship/<int:followship_pk>', remove_followship,
         name='api-remove-followship'),
    path('api/add_followship/<int:tagable_pk>', add_followship,
         name='api-add-followship'),
]


