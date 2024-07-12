# Generated by Django 5.0.6 on 2024-07-12 18:41

import ecap_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecap_app', '0011_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='default_user.jpg', null=True, upload_to=ecap_app.models.get_profile_picture_filepath),
        ),
    ]
