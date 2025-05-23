# Generated by Django 3.1.5 on 2021-01-13 08:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lobby', '0007_passwordreset'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reset hesla',
                'verbose_name_plural': 'Reset hesla',
            },
        ),
        migrations.DeleteModel(
            name='PasswordReset',
        ),
    ]
