# Generated by Django 5.0.4 on 2025-01-17 05:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_klass_result_publish_subject_mark'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subject',
            unique_together={('name', 'klass')},
        ),
        migrations.RemoveField(
            model_name='subject',
            name='institute',
        ),
    ]
