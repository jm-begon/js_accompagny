from django.contrib import admin
from django.db import models as django_models
from django.forms import TextInput, Textarea

from .models import Field, Skill, Module, Criterion, Training


class LongTextAdmin(admin.ModelAdmin):
    formfield_overrides = {
        django_models.CharField: {'widget': TextInput(attrs={'size': '150'})},
        django_models.TextField: {'widget': Textarea(attrs={'rows': 5,
                                                            'cols': 150})},
    }

admin.site.register(Field, LongTextAdmin)
admin.site.register(Skill, LongTextAdmin)
admin.site.register(Module, LongTextAdmin)
admin.site.register(Criterion, LongTextAdmin)
admin.site.register(Training, LongTextAdmin)


