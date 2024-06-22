# Generated by Django 5.0.4 on 2024-06-20 08:54

import django.db.models.deletion
import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_institute_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='institute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.institute', validators=[users.models.validate_institute_for_user_type]),
        ),
    ]
