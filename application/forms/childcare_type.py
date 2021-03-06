from django import forms
from govuk_forms.widgets import CheckboxSelectMultiple, InlineRadioSelect

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ChildcareType)


class TypeOfChildcareGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Type of childcare: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class TypeOfChildcareAgeGroupsForm(ChildminderForms):
    """
    GOV.UK form for the Type of childcare task
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    CHILDCARE_AGE_CHOICES = (
        ('0-5', '0 to 5 year olds'),
        ('5-8', '5 to 7 year olds'),
        ('8over', '8 years or older'),
    )
    type_of_childcare = forms.MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple,
        choices=CHILDCARE_AGE_CHOICES,
        label='What age groups could you be caring for?',
        help_text='Tick all that apply'
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of childcare form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(TypeOfChildcareAgeGroupsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ChildcareType.objects.filter(application_id=self.application_id_local).count() > 0:
            childcare_record = ChildcareType.objects.get(application_id=self.application_id_local)
            zero_to_five_status = childcare_record.zero_to_five
            five_to_eight_status = childcare_record.five_to_eight
            eight_plus_status = childcare_record.eight_plus
            if (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['0-5', '5-8', '8over']
            elif (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['0-5', '5-8']
            elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['0-5', '8over']
            elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['5-8', '8over']
            elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['0-5']
            elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['5-8']
            elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['8over']
            elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = []
        self.fields['type_of_childcare'].error_messages = {
            'required': 'Please select at least one age group'}


class TypeOfChildcareRegisterForm(ChildminderForms):
    """
    GOV.UK form for the Type of childcare: register page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class TypeOfChildcareOvernightCareForm(ChildminderForms):
    """
    GOV.UK form for the Type of Childcare: Overnight care page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem on this page'

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )

    overnight_care = forms.ChoiceField(label='Will you be looking after children overnight?', choices=options,
                                       widget=InlineRadioSelect, required=True,
                                       error_messages={'required':
                                                       "Please say if you'll be looking after children overnight"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of Childcare: Overnight form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(TypeOfChildcareOvernightCareForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

        # If information was previously entered, display it on the form
        if ChildcareType.objects.filter(application_id=self.application_id_local).count() > 0:
            childcare_record = ChildcareType.objects.get(application_id=self.application_id_local)
            self.fields['overnight_care'].initial = childcare_record.overnight_care
            self.field_list = ['overnight_care']
