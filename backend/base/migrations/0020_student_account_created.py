# Generated by Django 5.0.4 on 2025-01-30 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_student_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='account_created',
            field=models.BooleanField(default=False),
        ),
    ]
