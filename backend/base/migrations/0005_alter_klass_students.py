# Generated by Django 5.0.4 on 2024-06-20 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_klass_students'),
    ]

    operations = [
        migrations.AlterField(
            model_name='klass',
            name='students',
            field=models.ManyToManyField(related_name='student', to='base.student'),
        ),
    ]
