from django.contrib import admin
from .models import Tagable, Followhsip, Notification, TagSomething

admin.site.register(Tagable)
admin.site.register(Followhsip)
admin.site.register(Notification)
admin.site.register(TagSomething)
