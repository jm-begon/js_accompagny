from django.contrib import admin
from .models import *


class MessagesForIssues(admin.StackedInline):
    model = IssueMessage
    extra = 1


class IssueAdmin(admin.ModelAdmin):
    inlines = [MessagesForIssues]

admin.site.register(IssueState)
admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueMessage)
