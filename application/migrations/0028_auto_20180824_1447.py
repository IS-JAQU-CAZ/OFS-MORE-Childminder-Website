# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-24 13:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0027_remove_arc_childcare_training_review'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arc',
            old_name='eyfs_review',
            new_name='childcare_training_review',
        ),
    ]