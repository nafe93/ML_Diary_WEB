# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2021-02-24 16:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaryCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True, verbose_name='Date')),
                ('Category', models.CharField(max_length=100, unique=True, verbose_name='Category')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diary_category', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
            ],
            options={
                'verbose_name': 'Diary Category',
                'verbose_name_plural': 'Diary Categories',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='DiaryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True, verbose_name='Date')),
                ('text', models.TextField(null=True, verbose_name='Text')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diary_entries', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
            ],
            options={
                'verbose_name': 'Diary entry',
                'verbose_name_plural': 'Diary entries',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='DiaryImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True, verbose_name='Date')),
                ('image_path', models.TextField(verbose_name='image_path')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diary_image', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
            ],
            options={
                'verbose_name': 'Diary Image',
                'verbose_name_plural': 'Diary Images',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='DiaryTasks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True, verbose_name='Date')),
                ('task', models.TextField(verbose_name='task')),
                ('completion_percent', models.IntegerField(blank=True, null=True, verbose_name='completion_percent')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diary_task', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diary_task', to='diary.DiaryCategory', verbose_name='category')),
            ],
            options={
                'verbose_name': 'Diary Task',
                'verbose_name_plural': 'Diary Tasks',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=255, null=True, unique=True, verbose_name='tag')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.AddField(
            model_name='diaryentry',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='diary_entries', to='diary.Tag', verbose_name='Tags'),
        ),
    ]
