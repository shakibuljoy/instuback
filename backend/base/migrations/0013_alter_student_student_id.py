# Generated by Django 5.0.4 on 2024-11-02 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_student_active_student_admitted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.CharField(blank=True, default='', editable=False, max_length=8, unique=True),
        ),
    ]
