# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-30 11:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_adultinhome_permission_declare'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='children_turning_16',
            field=models.NullBooleanField(),
        ),
    ]
