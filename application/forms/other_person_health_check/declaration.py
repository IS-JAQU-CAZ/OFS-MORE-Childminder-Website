from django import forms

from application.forms import ChildminderForms, Application


class OtherPeopleDeclarationForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    declaration_confirmation = forms.BooleanField(label='I confirm',
                                                  required=True,
                                                  error_messages={
                                                      'required': 'You must confirm everything on this page to continue'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        # self.application_id_local = kwargs.pop('id')
        super().__init__(*args, **kwargs)
        # # If information was previously entered, display it on the form
        # if Application.objects.filter(application_id=self.application_id_local).count() > 0:
        #     declaration_confirmation = Application.objects.get(
        #         application_id=self.application_id_local).declaration_confirmation
        #     if declaration_confirmation is True:
        #         self.fields['declaration_confirmation'].initial = '1'
        #     elif declaration_confirmation is False:
        #         self.fields['declaration_confirmation'].initial = '0'