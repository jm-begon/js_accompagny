from django.contrib import admin
from .models import *

admin.site.register(IssueState)
admin.site.register(Issue)
admin.site.register(IssueMessage)
