# Generated by Django 5.0.4 on 2024-11-02 17:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_alter_student_student_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='klass',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.klass', verbose_name='Class'),
        ),
    ]
