# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-20 10:00
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arc',
            fields=[
                ('application_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('user_id', models.CharField(blank=True, max_length=50)),
                ('last_accessed', models.CharField(max_length=50)),
                ('app_type', models.CharField(max_length=50)),
                ('comments', models.CharField(blank=True, max_length=400)),
                ('login_details_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('childcare_type_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('personal_details_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('first_aid_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('dbs_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('health_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('references_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('people_in_home_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
            ],
            options={
                'managed': False,
                'db_table': 'ARC',
            },
        ),
        migrations.CreateModel(
            name='ArcComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_pk', models.UUIDField(blank=True)),
                ('table_name', models.CharField(blank=True, max_length=30)),
                ('field_name', models.CharField(blank=True, max_length=30)),
                ('comment', models.CharField(blank=True, max_length=100)),
                ('flagged', models.BooleanField()),
            ],
            options={
                'managed': False,
                'db_table': 'ARC_COMMENTS',
            },
        ),
    ]
