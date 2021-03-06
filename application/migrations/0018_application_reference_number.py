# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-12 15:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0017_application_reference_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherPersonPreviousRegistrationDetails',
            fields=[
                ('previous_registration_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('previous_registration', models.BooleanField(default=False)),
                ('individual_id', models.IntegerField(blank=True, default=0, null=True)),
                ('five_years_in_UK', models.BooleanField(default=False)),
                ('person_id', models.ForeignKey(db_column='person_id', on_delete=django.db.models.deletion.CASCADE, to='application.AdultInHome')),
            ],
            options={
                'db_table': 'OTHER_PERSON_PREVIOUS_REGISTRATION_DETAILS',
            },
        ),
    ]
