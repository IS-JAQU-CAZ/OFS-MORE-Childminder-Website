# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-23 08:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0024_merge_20180816_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthcheckcurrent',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='healthcheckhospital',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='healthcheckserious',
            name='description',
            field=models.TextField(),
        ),
    ]
