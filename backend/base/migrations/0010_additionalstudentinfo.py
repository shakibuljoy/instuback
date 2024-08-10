# Generated by Django 5.0.4 on 2024-08-09 12:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_additionalstudentfield_delete_additionalstudentinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalStudentInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=512)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.additionalstudentfield')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.student')),
            ],
            options={
                'unique_together': {('student', 'field')},
            },
        ),
    ]