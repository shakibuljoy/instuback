# Generated by Django 5.0.4 on 2025-01-17 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
