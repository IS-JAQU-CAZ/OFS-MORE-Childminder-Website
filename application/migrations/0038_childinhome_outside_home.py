# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-09-13 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0037_auto_20180911_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='childinhome',
            name='outside_home',
            field=models.BooleanField(default=False),
        ),
    ]
