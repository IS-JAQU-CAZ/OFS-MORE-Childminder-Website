from django import forms
from govuk_forms.widgets import InlineRadioSelect, NumberInput

from ..forms.childminder import ChildminderForms
from ..forms_helper import full_stop_stripper
from ..models import CriminalRecordCheck, Application
from ..business_logic import childminder_dbs_number_duplication_check, childminder_dbs_duplicates_household_member_check


class DBSRadioForm(ChildminderForms):
    """
    TODO -mop
    GOV.UK form for the Criminal record check: generic radio button form
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choice_field_name = 'generic_choice_field_name'
    dbs_field_name = None

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id = kwargs.pop('id')
        super().__init__(*args, **kwargs)

        self.fields[self.choice_field_name] = self.get_choice_field_data()

        # If information was previously entered, display it on the form
        self.fields = self.populate_initial_values()

    def get_options(self):
        options = (
            ('True', 'Yes'),
            ('False', 'No')
        )
        return options

    def populate_initial_values(self):
        if self.dbs_field_name is not None:
            fields = self.fields

            if CriminalRecordCheck.objects.filter(application_id=self.application_id).exists():
                dbs_record = CriminalRecordCheck.objects.get(application_id=self.application_id)
                fields[self.choice_field_name].initial = getattr(dbs_record, self.dbs_field_name)
                #self.pk = dbs_record.criminal_record_id

            return fields
        else:
            raise NotImplementedError("dbs_field_name must not be None.")

    def get_choice_field_data(self):
        raise NotImplementedError("No choice field was inherited.")


class DBSLivedAbroadForm(DBSRadioForm):
    """
    GOV.UK form for the Criminal record check: lived abroad page
    """
    choice_field_name = 'lived_abroad'
    dbs_field_name = 'lived_abroad'

    def get_choice_field_data(self):
        return forms.ChoiceField(label='Have you lived outside of the UK in the last 5 years?',
                                 choices=self.get_options(),
                                 widget=InlineRadioSelect,
                                 required=True,
                                 error_messages={'required': 'Please say if you have lived outside of the UK in the last 5 years'})


class DBSMilitaryForm(DBSRadioForm):
    """
    GOV.UK form for the Criminal record check: lived abroad page
    """
    choice_field_name = 'military'
    dbs_field_name = 'military_base'

    def get_choice_field_data(self):
        return forms.ChoiceField(label='Have you lived or worked on a military base overseas in the last five years?',
                                 choices=self.get_options(),
                                 widget=InlineRadioSelect,
                                 required=True,
                                 error_messages={'required': 'Please say if you have lived in a military base outside of the UK in the last 5 years'})

class DBSCheckUploadDBSForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: upload DBS page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class DBSCheckDBSDetailsForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    # Overrides standard NumberInput widget to give wider field
    widget_instance = NumberInput()
    widget_instance.input_classes = 'form-control form-control-1-4'

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    dbs_certificate_number = forms.IntegerField(label='DBS certificate number',
                                                help_text='12-digit number on your certificate',
                                                required=True,
                                                error_messages={'required': 'Please enter the DBS certificate number'},
                                                widget=widget_instance)

    cautions_convictions = forms.ChoiceField(label='Do you have any criminal cautions or convictions?',
                                             help_text='Include any information recorded on your certificate',
                                             choices=options, widget=InlineRadioSelect,
                                             required=True,
                                             error_messages={'required': 'Please say if you have any cautions or convictions'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DBSCheckDBSDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if CriminalRecordCheck.objects.filter(application_id=self.application_id_local).count() > 0:
            dbs_record = CriminalRecordCheck.objects.get(application_id=self.application_id_local)
            self.fields['dbs_certificate_number'].initial = dbs_record.dbs_certificate_number
            self.fields['cautions_convictions'].initial = dbs_record.cautions_convictions
            self.pk = dbs_record.criminal_record_id
            self.field_list = ['dbs_certificate_number', 'cautions_convictions']

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        # is_valid() call strips leading 0 required by DBS number. Use raw str input from user instead of cleaned_data.
        dbs_certificate_number = self.data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('The certificate number should be 12 digits long')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('The certificate number should be 12 digits long')

        application_id = self.data['id']
        application = Application.objects.get(pk=application_id)

        if childminder_dbs_duplicates_household_member_check(application, dbs_certificate_number):
            raise forms.ValidationError('Please enter a different DBS number. '
                                        'You entered this number for someone in your childcare location')

        return dbs_certificate_number


class DBSCheckSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'generic-error-summary.html'
    auto_replace_widgets = True

    arc_errors = forms.CharField()
