# app/migrations/0003_auto_add_roles.py
from django.db import migrations

def add_roles(apps, schema_editor):
    Role = apps.get_model('app', 'Role')
    Role.objects.create(name='admin')
    Role.objects.create(name='user')
    Role.objects.create(name='employee')

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_appuser_is_active_employee_is_active'),
    ]

    operations = [
        migrations.RunPython(add_roles),
    ]
