# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-04 16:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdultInHome',
            fields=[
                ('adult_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('adult', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('middle_names', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('birth_day', models.IntegerField(blank=True)),
                ('birth_month', models.IntegerField(blank=True)),
                ('birth_year', models.IntegerField(blank=True)),
                ('relationship', models.CharField(blank=True, max_length=100)),
                ('dbs_certificate_number', models.CharField(blank=True, max_length=50)),
                ('permission_declare', models.NullBooleanField()),
            ],
            options={
                'db_table': 'ADULT_IN_HOME',
            },
        ),
        migrations.CreateModel(
            name='ApplicantHomeAddress',
            fields=[
                ('home_address_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('street_line1', models.CharField(blank=True, max_length=100)),
                ('street_line2', models.CharField(blank=True, max_length=100)),
                ('town', models.CharField(blank=True, max_length=100)),
                ('county', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postcode', models.CharField(blank=True, max_length=8)),
                ('childcare_address', models.NullBooleanField(default=None)),
                ('current_address', models.NullBooleanField(default=None)),
                ('move_in_month', models.IntegerField(blank=True)),
                ('move_in_year', models.IntegerField(blank=True)),
            ],
            options={
                'db_table': 'APPLICANT_HOME_ADDRESS',
            },
        ),
        migrations.CreateModel(
            name='ApplicantName',
            fields=[
                ('name_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('current_name', models.BooleanField()),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('middle_names', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'db_table': 'APPLICANT_NAME',
            },
        ),
        migrations.CreateModel(
            name='ApplicantPersonalDetails',
            fields=[
                ('personal_detail_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('birth_day', models.IntegerField(blank=True, null=True)),
                ('birth_month', models.IntegerField(blank=True, null=True)),
                ('birth_year', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'APPLICANT_PERSONAL_DETAILS',
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('application_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('application_type', models.CharField(blank=True, choices=[('CHILDMINDER', 'CHILDMINDER'), ('NANNY', 'NANNY'), ('NURSERY', 'NURSERY'), ('SOCIAL_CARE', 'SOCIAL_CARE')], max_length=50)),
                ('application_status', models.CharField(blank=True, choices=[('ARC_REVIEW', 'ARC_REVIEW'), ('CANCELLED', 'CANCELLED'), ('CYGNUM_REVIEW', 'CYGNUM_REVIEW'), ('DRAFTING', 'DRAFTING'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION'), ('NOT_REGISTERED', 'NOT_REGISTERED'), ('REGISTERED', 'REGISTERED'), ('REJECTED', 'REJECTED'), ('SUBMITTED', 'SUBMITTED'), ('WITHDRAWN', 'WITHDRAWN')], max_length=50)),
                ('cygnum_urn', models.CharField(blank=True, max_length=50)),
                ('login_details_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('personal_details_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('childcare_type_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('first_aid_training_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('eyfs_training_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('criminal_record_check_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('health_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('references_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('people_in_home_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('adults_in_home', models.NullBooleanField(default=None)),
                ('children_in_home', models.NullBooleanField(default=None)),
                ('children_turning_16', models.NullBooleanField(default=None)),
                ('declarations_status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('FURTHER_INFORMATION', 'FURTHER_INFORMATION')], max_length=50)),
                ('background_check_declare', models.NullBooleanField(default=None)),
                ('inspect_home_declare', models.NullBooleanField(default=None)),
                ('interview_declare', models.NullBooleanField(default=None)),
                ('share_info_declare', models.NullBooleanField(default=None)),
                ('information_correct_declare', models.NullBooleanField(default=None)),
                ('change_declare', models.NullBooleanField(default=None)),
                ('date_created', models.DateTimeField(blank=True, null=True)),
                ('date_updated', models.DateTimeField(blank=True, null=True)),
                ('date_accepted', models.DateTimeField(blank=True, null=True)),
                ('order_code', models.UUIDField(blank=True, null=True)),
                ('date_submitted', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'APPLICATION',
            },
        ),
        migrations.CreateModel(
            name='Arc',
            fields=[
                ('application_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('user_id', models.CharField(blank=True, max_length=50)),
                ('last_accessed', models.CharField(max_length=50)),
                ('app_type', models.CharField(max_length=50)),
                ('comments', models.CharField(blank=True, max_length=400)),
                ('login_details_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
                ('childcare_type_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
                ('personal_details_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
                ('first_aid_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
                ('dbs_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
                ('health_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
                ('references_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
                ('people_in_home_review', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], max_length=50)),
            ],
            options={
                'db_table': 'ARC',
            },
        ),
        migrations.CreateModel(
            name='ArcComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_pk', models.UUIDField(blank=True)),
                ('table_name', models.CharField(blank=True, max_length=30)),
                ('field_name', models.CharField(blank=True, max_length=40)),
                ('comment', models.CharField(blank=True, max_length=100)),
                ('flagged', models.BooleanField()),
            ],
            options={
                'db_table': 'ARC_COMMENTS',
            },
        ),
        migrations.CreateModel(
            name='ChildcareType',
            fields=[
                ('childcare_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('zero_to_five', models.BooleanField()),
                ('five_to_eight', models.BooleanField()),
                ('eight_plus', models.BooleanField()),
                ('overnight_care', models.NullBooleanField()),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'CHILDCARE_TYPE',
            },
        ),
        migrations.CreateModel(
            name='ChildInHome',
            fields=[
                ('child_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('child', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('middle_names', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('birth_day', models.IntegerField(blank=True)),
                ('birth_month', models.IntegerField(blank=True)),
                ('birth_year', models.IntegerField(blank=True)),
                ('relationship', models.CharField(blank=True, max_length=100)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'CHILD_IN_HOME',
            },
        ),
        migrations.CreateModel(
            name='CriminalRecordCheck',
            fields=[
                ('criminal_record_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('dbs_certificate_number', models.CharField(blank=True, max_length=50)),
                ('cautions_convictions', models.BooleanField()),
                ('send_certificate_declare', models.NullBooleanField()),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'CRIMINAL_RECORD_CHECK',
            },
        ),
        migrations.CreateModel(
            name='EYFS',
            fields=[
                ('eyfs_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('eyfs_understand', models.NullBooleanField(default=None)),
                ('eyfs_training_declare', models.NullBooleanField(default=None)),
                ('share_info_declare', models.NullBooleanField(default=None)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'EYFS',
            },
        ),
        migrations.CreateModel(
            name='FirstAidTraining',
            fields=[
                ('first_aid_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('training_organisation', models.CharField(max_length=100)),
                ('course_title', models.CharField(max_length=100)),
                ('course_day', models.IntegerField()),
                ('course_month', models.IntegerField()),
                ('course_year', models.IntegerField()),
                ('show_certificate', models.NullBooleanField(default=None)),
                ('renew_certificate', models.NullBooleanField(default=None)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'FIRST_AID_TRAINING',
            },
        ),
        migrations.CreateModel(
            name='HealthDeclarationBooklet',
            fields=[
                ('hdb_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('send_hdb_declare', models.NullBooleanField()),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'HDB',
            },
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('reference_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('reference', models.IntegerField(blank=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('relationship', models.CharField(blank=True, max_length=100)),
                ('years_known', models.IntegerField(blank=True)),
                ('months_known', models.IntegerField(blank=True)),
                ('street_line1', models.CharField(blank=True, max_length=100)),
                ('street_line2', models.CharField(blank=True, max_length=100)),
                ('town', models.CharField(blank=True, max_length=100)),
                ('county', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postcode', models.CharField(blank=True, max_length=8)),
                ('phone_number', models.CharField(blank=True, max_length=50)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'REFERENCE',
            },
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('login_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('mobile_number', models.CharField(blank=True, max_length=20)),
                ('add_phone_number', models.CharField(blank=True, max_length=20)),
                ('email_expiry_date', models.IntegerField(blank=True, null=True)),
                ('sms_expiry_date', models.IntegerField(blank=True, null=True)),
                ('magic_link_email', models.CharField(blank=True, max_length=100, null=True)),
                ('magic_link_sms', models.CharField(blank=True, max_length=100, null=True)),
                ('security_question', models.CharField(blank=True, max_length=100, null=True)),
                ('security_answer', models.CharField(blank=True, max_length=100, null=True)),
                ('application_id', models.ForeignKey(db_column='application_id', default=uuid.uuid4, on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'USER_DETAILS',
            },
        ),
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application'),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application'),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='personal_detail_id',
            field=models.ForeignKey(db_column='personal_detail_id', on_delete=django.db.models.deletion.CASCADE, to='application.ApplicantPersonalDetails'),
        ),
        migrations.AddField(
            model_name='applicanthomeaddress',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application'),
        ),
        migrations.AddField(
            model_name='applicanthomeaddress',
            name='personal_detail_id',
            field=models.ForeignKey(db_column='personal_detail_id', on_delete=django.db.models.deletion.CASCADE, to='application.ApplicantPersonalDetails'),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='application_id',
            field=models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application'),
        ),
    ]
