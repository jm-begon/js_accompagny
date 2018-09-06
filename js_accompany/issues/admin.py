from django.contrib import admin
from django.db import transaction
from .models import Issue, StateChanged, MessagePosted


class MessagesForIssues(admin.StackedInline):
    model = MessagePosted
    extra = 1


class IssueAdmin(admin.ModelAdmin):
    inlines = [MessagesForIssues]

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        # https://books.agiliq.com/projects/django-admin-cookbook/en/latest/current_user.html
        # https://docs.djangoproject.com/en/2.1/topics/forms/formsets/#formsets-initial-data ?
        creation = not obj.pk
        super().save_model(request, obj, form, change)
        obj.refresh_from_db()
        if creation:
            StateChanged.on_new_issue(user=request.user, issue=obj)


admin.site.register(Issue, IssueAdmin)
admin.site.register(StateChanged)
admin.site.register(MessagePosted)
