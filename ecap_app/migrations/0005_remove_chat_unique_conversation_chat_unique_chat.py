# Generated by Django 5.0.6 on 2024-06-27 20:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecap_app', '0004_rename_conversation_message_chat_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='chat',
            name='unique_conversation',
        ),
        migrations.AddConstraint(
            model_name='chat',
            constraint=models.UniqueConstraint(condition=models.Q(('user1__lt', models.F('user2'))), fields=('user1', 'user2'), name='unique_chat'),
        ),
    ]