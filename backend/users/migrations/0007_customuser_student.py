# Generated by Django 5.0.4 on 2025-01-30 17:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_student_email'),
        ('users', '0006_delete_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.student'),
        ),
    ]
