# Generated by Django 5.0.4 on 2025-01-23 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_rename_result_publish_klass_result_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(default='shakibulislamj@gmail.com', max_length=254),
            preserve_default=False,
        ),
    ]
