# Generated by Django 5.0.4 on 2024-08-09 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='mode',
            field=models.CharField(choices=[('cash', 'Cash'), ('online', 'Online')], default='cash', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('hold', 'Hold')], max_length=30),
        ),
    ]