from django.db import migrations
from ..models import __STATES__


def add_state(apps, schema_editor):
    IssueState = apps.get_model('issues', 'IssueState')
    for state_name in __STATES__:
        state = IssueState()
        state.name = state_name
        state.save()


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_state),
    ]
