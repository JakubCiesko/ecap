# Generated by Django 5.0.6 on 2024-07-12 18:50

import ecap_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecap_app', '0013_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(default='profile_pictures/default_user.jpg', upload_to=ecap_app.models.get_profile_picture_filepath),
        ),
    ]
