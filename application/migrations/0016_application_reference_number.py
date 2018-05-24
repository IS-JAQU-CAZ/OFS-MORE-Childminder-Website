# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-23 22:54
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


def seed_application_reference(apps, schema_editor):
    ApplicationReference = apps.get_model('application', 'ApplicationReference')
    ApplicationReference.objects.create(reference=1000000)


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0015_auto_20180523_0930'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.IntegerField(validators=[django.core.validators.MaxValueValidator(9999999)])),
            ],
            options={
                'db_table': 'APPLICATION_REFERENCE',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('payment_reference', models.CharField(max_length=29)),
                ('payment_submitted', models.BooleanField(default=False)),
                ('payment_authorised', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'PAYMENT',
            },
        ),
        migrations.RemoveField(
            model_name='application',
            name='order_code',
        ),
        migrations.AddField(
            model_name='application',
            name='application_reference',
            field=models.CharField(blank=True, max_length=9, null=True, validators=[django.core.validators.RegexValidator('(\\w{2})([0-9]{7})')]),
        ),
        migrations.AlterField(
            model_name='adultinhome',
            name='email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application'),
        ),
        migrations.RunPython(seed_application_reference),
    ]