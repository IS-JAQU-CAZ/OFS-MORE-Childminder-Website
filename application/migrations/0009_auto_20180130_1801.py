# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-30 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0008_remove_adultinhome_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='background_check_declare',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='application',
            name='eyfs_questions_declare',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='application',
            name='inspect_home_declare',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='application',
            name='interview_declare',
            field=models.NullBooleanField(),
        ),
    ]
