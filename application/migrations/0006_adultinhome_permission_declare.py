# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-29 12:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_auto_20180126_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='adultinhome',
            name='permission_declare',
            field=models.NullBooleanField(),
        ),
    ]