# Generated by Django 5.0.4 on 2024-06-29 06:29

import base.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0004_alter_customuser_institute'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Klass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('group', models.CharField(blank=True, max_length=50, null=True)),
                ('branch', models.CharField(blank=True, max_length=50, null=True)),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.institute')),
                ('teachers', models.ManyToManyField(blank=True, null=True, related_name='teacher', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=120)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=120)),
                ('last_name', models.CharField(blank=True, max_length=120, null=True)),
                ('mobile', models.CharField(max_length=50)),
                ('mothers_name', models.CharField(max_length=120)),
                ('fathers_name', models.CharField(max_length=120)),
                ('address', models.CharField(max_length=220)),
                ('birth_date', models.DateField()),
                ('birth_certificate_no', models.CharField(max_length=220)),
                ('nid_no', models.CharField(blank=True, max_length=220, null=True)),
                ('image', models.ImageField(upload_to=base.models.Student.folder_convention)),
                ('institute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.institute')),
                ('klass', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.klass', verbose_name='Class')),
            ],
        ),
        migrations.CreateModel(
            name='StudentDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_title', models.CharField(max_length=120)),
                ('image', models.ImageField(upload_to=base.models.StudentDocument.folder_convention)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.student')),
            ],
        ),
    ]