# Generated by Django 5.0.4 on 2024-06-20 07:05

import django.contrib.auth.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='institute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.institute'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profile/', verbose_name='Profile Picture'),
        ),
        migrations.AlterField(
            model_name='institute',
            name='instu_id',
            field=models.CharField(error_messages={'unique': 'A institute with this ID already exists.'}, help_text='Required. 150 characters of fewer. Letters, digits only', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator]),
        ),
    ]