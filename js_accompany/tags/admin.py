from django.contrib import admin
from .models import Tagable, Followship, Notification, TagSomething

admin.site.register(Tagable)
admin.site.register(Followship)
admin.site.register(Notification)
admin.site.register(TagSomething)
