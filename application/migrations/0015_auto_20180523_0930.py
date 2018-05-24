# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-23 08:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0014_merge_20180521_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adultinhome',
            name='current_treatment',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='adultinhome',
            name='email',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='adultinhome',
            name='hospital_admission',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='adultinhome',
            name='serious_illness',
            field=models.NullBooleanField(),
        ),
    ]