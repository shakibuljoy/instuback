# Generated by Django 5.0.4 on 2025-02-08 06:06

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_customuser_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institute',
            name='instititute_photo',
            field=models.ImageField(blank=True, null=True, upload_to=users.models.institute_photo_upload_path),
        ),
    ]
