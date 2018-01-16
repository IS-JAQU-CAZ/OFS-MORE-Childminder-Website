"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- views.py --

@author: Informed Solutions
"""

import datetime
import json
import re
import time

from datetime import date

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .middleware import CustomAuthenticationHandler
from . import magic_link, payment, status
from .business_logic import (childcare_type_logic,
                             dbs_check_logic,
                             first_aid_logic,
                             health_check_logic,
                             login_contact_logic,
                             login_contact_logic_phone,
                             multiple_childcare_address_logic,
                             personal_childcare_address_logic,
                             personal_dob_logic,
                             personal_home_address_logic,
                             personal_location_of_care_logic,
                             personal_name_logic,
                             references_first_reference_logic,
                             references_second_reference_logic)
from .forms import (AccountForm,
                    ApplicationSavedForm,
                    ConfirmForm,
                    ContactEmailForm,
                    ContactPhoneForm,
                    ContactSummaryForm,
                    DBSCheckDBSDetailsForm,
                    DBSCheckGuidanceForm,
                    DBSCheckSummaryForm,
                    DBSCheckUploadDBSForm,
                    DeclarationForm,
                    EYFSForm,
                    FirstAidTrainingDeclarationForm,
                    FirstAidTrainingDetailsForm,
                    FirstAidTrainingGuidanceForm,
                    FirstAidTrainingRenewForm,
                    FirstAidTrainingSummaryForm,
                    FirstAidTrainingTrainingForm,
                    HealthBookletForm,
                    HealthIntroForm,
                    OtherPeopleForm,
                    PaymentDetailsForm,
                    PaymentForm,
                    PersonalDetailsChildcareAddressForm,
                    PersonalDetailsChildcareAddressManualForm,
                    PersonalDetailsDOBForm,
                    PersonalDetailsGuidanceForm,
                    PersonalDetailsHomeAddressForm,
                    PersonalDetailsHomeAddressManualForm,
                    PersonalDetailsLocationOfCareForm,
                    PersonalDetailsNameForm,
                    PersonalDetailsSummaryForm,
                    QuestionForm,
                    FirstReferenceForm,
                    ReferenceIntroForm,
                    ReferenceFirstReferenceAddressForm,
                    ReferenceFirstReferenceAddressManualForm,
                    ReferenceFirstReferenceContactForm,
                    ReferenceSecondReferenceAddressForm,
                    ReferenceSecondReferenceAddressManualForm,
                    ReferenceSecondReferenceContactForm,
                    ReferenceSummaryForm,
                    SecondReferenceForm,
                    TypeOfChildcareForm)
from .models import (Application,
                     ApplicantHomeAddress,
                     ApplicantName,
                     ApplicantPersonalDetails,
                     CriminalRecordCheck,
                     FirstAidTraining,
                     HealthDeclarationBooklet,
                     Reference,
                     UserDetails)


def start_page(request):
    """
    Method returning the template for the start page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered start page template
    """
    return render(request, 'start-page.html')


def account_selection(request):
    """
    Method returning the template for the account selection page and navigating to the account: email page when
    clicking on the Create an account button, which triggers the creation of a new application
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered account selection template
    """
    if request.method == 'GET':
        form = AccountForm()
        variables = {
            'form': form,
        }
        return render(request, 'account-account.html', variables)
    if request.method == 'POST':
        user = UserDetails.objects.create()
        application = Application.objects.create(
            application_type='CHILDMINDER',
            login_id=user,
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
            personal_details_status='NOT_STARTED',
            childcare_type_status='NOT_STARTED',
            first_aid_training_status='NOT_STARTED',
            eyfs_training_status='NOT_STARTED',
            criminal_record_check_status='NOT_STARTED',
            health_status='NOT_STARTED',
            references_status='NOT_STARTED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None
        )
        application_id_local = str(application.application_id)
        return HttpResponseRedirect(settings.URL_PREFIX + '/account/email?id=' + application_id_local)
    else:
        form = AccountForm()
        variables = {
            'form': form
        }
        return render(request, 'account-account.html', variables)


def contact_email(request):
    """
    Method returning the template for the Your login and contact details: email page (for a given application)
    and navigating to the Your login and contact details: phone number page when successfully completed;
    business logic is applied to either create or update the associated User_Details record; the page redirects
    the applicant to the login page if they have previously applied
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: email template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ContactEmailForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'login_details_status': application.login_details_status
        }
        return render(request, 'contact-email.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ContactEmailForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Send login e-mail link if applicant has previously applied
            email = form.cleaned_data['email_address']
            if UserDetails.objects.filter(email=email).exists():
                acc = UserDetails.objects.get(email=email)
                domain = request.META.get('HTTP_REFERER', "")
                domain = domain[:-54]
                link = magic_link.generate_random(12, "link")
                expiry = int(time.time())
                acc.email_expiry_date = expiry
                acc.magic_link_email = link
                acc.save()
                magic_link.magic_link_email(email, domain + 'validate/' + link)
                return HttpResponseRedirect(settings.URL_PREFIX + '/email-sent?id=' + application_id_local)
            else:
                # Create or update User_Details record
                user_details_record = login_contact_logic(application_id_local, form)
                user_details_record.save()
                application.date_updated = current_date
                application.save()
                response = HttpResponseRedirect(settings.URL_PREFIX + '/account/phone?id=' + application_id_local)
                # Create session and issue cookie to user
                CustomAuthenticationHandler.create_session(response, application.login_id.email)
                return response
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'login_details_status': application.login_details_status
            }
            return render(request, 'contact-email.html', variables)


def contact_phone(request):
    """
    Method returning the template for the Your login and contact details: phone number page (for a given application)
    and navigating to the Your login and contact details: question page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: phone template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ContactPhoneForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'login_details_status': application.login_details_status
        }
        return render(request, 'contact-phone.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ContactPhoneForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Update User_Details record
            user_details_record = login_contact_logic_phone(application_id_local, form)
            user_details_record.save()
            application.date_updated = current_date
            application.save()
            return HttpResponseRedirect(settings.URL_PREFIX + '/account/question?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'login_details_status': application.login_details_status
            }
            return render(request, 'contact-phone.html', variables)


def contact_question(request):
    """
    Method returning the template for the Your login and contact details: question page (for a given application)
    and navigating to the Your login and contact details: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: question template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = QuestionForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'login_details_status': application.login_details_status
        }
        return render(request, 'contact-question.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = QuestionForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Do not update User_Details record (awaiting confirmation from Ofsted)
            return HttpResponseRedirect(settings.URL_PREFIX + '/account/summary?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'login_details_status': application.login_details_status
            }
            return render(request, 'contact-question.html', variables)


def contact_summary(request):
    """
    Method returning the template for the Your login and contact details: summary page (for a given application)
    displaying entered data for this task and navigating to the Type of childcare page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        login_id = application.login_id.login_id
        user_details = UserDetails.objects.get(login_id=login_id)
        email = user_details.email
        mobile_number = user_details.mobile_number
        add_phone_number = user_details.add_phone_number
        if application.login_details_status != 'COMPLETED':
            status.update(application_id_local, 'login_details_status', 'COMPLETED')
        form = ContactSummaryForm()
        variables = {
            'form': form,
            'application_id': application_id_local,
            'email': email,
            'mobile_number': mobile_number,
            'add_phone_number': add_phone_number,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'contact-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ContactSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            status.update(application_id_local, 'login_details_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/childcare?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'login_details_status': application.login_details_status
            }
            return render(request, 'contact-summary.html', variables)


def type_of_childcare(request):
    """
    Method returning the template for the Type of childcare page (for a given application) and navigating to
    the task list when successfully completed; business logic is applied to either create or update the
    associated Childcare_Type record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = TypeOfChildcareForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'childcare.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = TypeOfChildcareForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update Childcare_Type record
            childcare_type_record = childcare_type_logic(application_id_local, form)
            childcare_type_record.save()
            application.date_updated = current_date
            application.save()
            status.update(application_id_local, 'childcare_type_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'childcare_type_status': application.childcare_type_status
            }
            return render(request, 'childcare.html', variables)


def task_list(request):
    """
    Method returning the template for the task-list (with current task status) for an applicant's application;
    logic is built in to enable the Declarations and Confirm your details tasks when all other tasks are complete
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered task list template
    """
    if request.method == 'GET':
        application_id = request.GET["id"]
        application = Application.objects.get(pk=application_id)
        application_status_context = dict({
            'application_id': application_id,
            'login_details_status': application.login_details_status,
            'personal_details_status': application.personal_details_status,
            'childcare_type_status': application.childcare_type_status,
            'first_aid_training_status': application.first_aid_training_status,
            'eyfs_training_status': application.eyfs_training_status,
            'criminal_record_check_status': application.criminal_record_check_status,
            'health_status': application.health_status,
            'reference_status': application.references_status,
            'people_in_home_status': application.people_in_home_status,
            'declaration_status': application.declarations_status,
            'all_complete': False,
            'confirm_details': False
        })
        temp_context = application_status_context
        del temp_context['declaration_status']
        # Enable/disable Declarations and Confirm your details tasks depending on task completion
        if ('NOT_STARTED' in temp_context.values()) or ('IN_PROGRESS' in temp_context.values()):
            application_status_context['all_complete'] = False
        else:
            application_status_context['all_complete'] = True
            application_status_context['declaration_status'] = application.declarations_status
            if application_status_context['declaration_status'] == 'COMPLETED':
                application_status_context['confirm_details'] = True
            else:
                application_status_context['confirm_details'] = False
    return render(request, 'task-list.html', application_status_context)


def personal_details_guidance(request):
    """
    Method returning the template for the Your personal details: guidance page (for a given application)
    and navigating to the Your login and contact details: name page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = PersonalDetailsGuidanceForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = PersonalDetailsGuidanceForm(request.POST)
        if form.is_valid():
            if Application.objects.get(pk=application_id_local).personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/name?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'personal-details-guidance.html', variables)


def personal_details_name(request):
    """
    Method returning the template for the Your personal details: name page (for a given application)
    and navigating to the Your personal details: date of birth page when successfully completed;
    business logic is applied to either create or update the associated Applicant_Name record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: name template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = PersonalDetailsNameForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-name.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = PersonalDetailsNameForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
            # Create or update Applicant_Names record
            applicant_names_record = personal_name_logic(application_id_local, form)
            applicant_names_record.save()
            application.date_updated = current_date
            application.save()
            return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/dob/?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'personal-details-name.html', variables)


def personal_details_dob(request):
    """
    Method returning the template for the Your personal details: date of birth page (for a given application)
    and navigating to the Your personal details: home address page when successfully completed;
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: date of birth template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = PersonalDetailsDOBForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-dob.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = PersonalDetailsDOBForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
            # Update Applicant_Personal_Details record
            personal_details_record = personal_dob_logic(application_id_local, form)
            personal_details_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/personal-details/home-address?id=' + application_id_local + '&manual=False')
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'personal-details-dob.html', variables)


def personal_details_home_address(request):
    """
    Method returning the template for the Your personal details: home address page (for a given application)
    and navigating to the Your personal details: location of care page when successfully completed;
    business logic is applied to either create or update the associated Applicant_Name record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: home address template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        manual = request.GET["manual"]
        # Switch between manual address entry and postcode search
        if manual == 'False':
            form = PersonalDetailsHomeAddressForm(id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-home-address.html', variables)
        elif manual == 'True':
            form = PersonalDetailsHomeAddressManualForm(id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-home-address-manual.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        manual = request.POST["manual"]
        # Switch between manual address entry and postcode search
        if manual == 'False':
            form = PersonalDetailsHomeAddressForm(request.POST, id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            if form.is_valid():
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/home-address/?id=' + application_id_local +
                    '&manual=False')
            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'personal_details_status': application.personal_details_status
                }
                return render(request, 'personal-details-home-address.html', variables)
        if manual == 'True':
            form = PersonalDetailsHomeAddressManualForm(request.POST, id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            if form.is_valid():
                if Application.objects.get(pk=application_id_local).personal_details_status != 'COMPLETED':
                    status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
                # Create or update Application_Home_Address record
                home_address_record = personal_home_address_logic(application_id_local, form)
                home_address_record.save()
                application = Application.objects.get(pk=application_id_local)
                application.date_updated = current_date
                application.save()
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/location-of-care?id=' + application_id_local)
            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'personal_details_status': application.personal_details_status
                }
                return render(request, 'personal-details-home-address-manual.html', variables)


def personal_details_location_of_care(request):
    """
    Method returning the template for the Your personal details: location of care page (for a given application)
    and navigating to the Your personal details: childcare or summary page when successfully completed;
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: location of care template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=application_id_local).personal_detail_id
        applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                  current_address=True)
        # Delete childcare address if it is marked the same as the home address
        multiple_childcare_address_logic(personal_detail_id)
        street_line1 = applicant_home_address.street_line1
        street_line2 = applicant_home_address.street_line2
        town = applicant_home_address.town
        county = applicant_home_address.county
        postcode = applicant_home_address.postcode
        application = Application.objects.get(pk=application_id_local)
        if application.login_details_status != 'COMPLETED':
            status.update(application_id_local, 'login_details_status', 'COMPLETED')
        form = PersonalDetailsLocationOfCareForm(id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'street_line1': street_line1,
            'street_line2': street_line2,
            'town': town,
            'county': county,
            'postcode': postcode,
            'personal_details_status': application.login_details_status
        }
        return render(request, 'personal-details-location-of-care.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=application_id_local).personal_detail_id
        form = PersonalDetailsLocationOfCareForm(request.POST, id=application_id_local)
        if form.is_valid():
            application = Application.objects.get(pk=application_id_local)
            if application.personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
            # Update home address record
            home_address_record = personal_location_of_care_logic(application_id_local, form)
            home_address_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            # Delete childcare address if it is marked the same as the home address
            multiple_childcare_address_logic(personal_detail_id)
            if home_address_record.childcare_address == 'True':
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/summary?id=' + application_id_local)
            elif home_address_record.childcare_address == 'False':
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/childcare-address?id=' + application_id_local + '&manual=False')
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'personal-details-location-of-care.html', variables)


def personal_details_childcare_address(request):
    """
    Method returning the template for the Your personal details: childcare address page (for a given application)
    and navigating to the Your personal details: summary page when successfully completed;
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: childcare template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        manual = request.GET["manual"]
        # Switch between manual address entry and postcode search
        if manual == 'False':
            form = PersonalDetailsChildcareAddressForm(id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-childcare-address.html', variables)
        elif manual == 'True':
            form = PersonalDetailsChildcareAddressManualForm(id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-childcare-address-manual.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        manual = request.POST["manual"]
        # Switch between manual address entry and postcode search
        if manual == 'False':
            form = PersonalDetailsChildcareAddressForm(request.POST, id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            if form.is_valid():
                if Application.objects.get(pk=application_id_local).personal_details_status != 'COMPLETED':
                    status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
                return HttpResponseRedirect(settings.URL_PREFIX +
                                            '/personal-details/childcare-address/?id=' + application_id_local +
                                            '&manual=False')
            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'personal_details_status': application.personal_details_status
                }
                return render(request, 'personal-details-childcare-address.html', variables)
        if manual == 'True':
            form = PersonalDetailsChildcareAddressManualForm(request.POST, id=application_id_local)
            application = Application.objects.get(pk=application_id_local)
            if form.is_valid():
                application = Application.objects.get(pk=application_id_local)
                if application.personal_details_status != 'COMPLETED':
                    status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
                # Update Applicant_Home_Address record
                childcare_address_record = personal_childcare_address_logic(application_id_local, form)
                childcare_address_record.save()
                application.date_updated = current_date
                application.save()
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/summary?id=' + application_id_local)
            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'personal_details_status': application.personal_details_status
                }
                return render(request, 'personal-details-childcare-address-manual.html', variables)


def personal_details_summary(request):
    """
    Method returning the template for the Your personal details: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
        birth_day = personal_detail_id.birth_day
        birth_month = personal_detail_id.birth_month
        birth_year = personal_detail_id.birth_year
        applicant_name_record = ApplicantName.objects.get(personal_detail_id=personal_detail_id)
        first_name = applicant_name_record.first_name
        middle_names = applicant_name_record.middle_names
        last_name = applicant_name_record.last_name
        applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                         current_address=True)
        street_line1 = applicant_home_address_record.street_line1
        street_line2 = applicant_home_address_record.street_line2
        town = applicant_home_address_record.town
        county = applicant_home_address_record.county
        postcode = applicant_home_address_record.postcode
        location_of_childcare = applicant_home_address_record.childcare_address
        applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                              childcare_address=True)
        childcare_street_line1 = applicant_childcare_address_record.street_line1
        childcare_street_line2 = applicant_childcare_address_record.street_line2
        childcare_town = applicant_childcare_address_record.town
        childcare_county = applicant_childcare_address_record.county
        childcare_postcode = applicant_childcare_address_record.postcode
        form = PersonalDetailsSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        status.update(application_id_local, 'personal_details_status', 'COMPLETED')
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_name': first_name,
            'middle_names': middle_names,
            'last_name': last_name,
            'birth_day': birth_day,
            'birth_month': birth_month,
            'birth_year': birth_year,
            'street_line1': street_line1,
            'street_line2': street_line2,
            'town': town,
            'county': county,
            'postcode': postcode,
            'location_of_childcare': location_of_childcare,
            'childcare_street_line1': childcare_street_line1,
            'childcare_street_line2': childcare_street_line2,
            'childcare_town': childcare_town, 'childcare_county': childcare_county,
            'childcare_postcode': childcare_postcode,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = PersonalDetailsSummaryForm()
        if form.is_valid():
            status.update(application_id_local, 'personal_details_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'personal-details-summary.html', variables)


def first_aid_training_guidance(request):
    """
    Method returning the template for the First aid training: guidance page (for a given application)
    and navigating to the First aid training: details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingGuidanceForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingGuidanceForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.first_aid_training_status != 'COMPLETED':
                status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/details?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-training-guidance.html', variables)


def first_aid_training_details(request):
    """
    Method returning the template for the First aid training: details page (for a given application)
    and navigating to the First aid training: renew, declaration or training page depending on
    the age of the first aid training certificate when successfully completed;
    business logic is applied to either create or update the associated First_Aid_Training record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: details template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingDetailsForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingDetailsForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.first_aid_training_status != 'COMPLETED':
                status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
            # Create or update First_Aid_Training record
            first_aid_training_record = first_aid_logic(application_id_local, form)
            first_aid_training_record.save()
            application.date_updated = current_date
            application.save()
            # Calculate certificate age and determine which page to navigate to
            certificate_day = form.cleaned_data['course_date'].day
            certificate_month = form.cleaned_data['course_date'].month
            certificate_year = form.cleaned_data['course_date'].year
            certificate_date = date(certificate_year, certificate_month, certificate_day)
            today = date.today()
            certificate_age = today.year - certificate_date.year - (
                    (today.month, today.day) < (certificate_date.month, certificate_date.day))
            if certificate_age < 2.5:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/declaration?id=' + application_id_local)
            elif 2.5 <= certificate_age <= 3:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/renew?id=' + application_id_local)
            elif certificate_age > 3:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/training?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-details.html', variables)


def first_aid_training_declaration(request):
    """
    Method returning the template for the First aid training: declaration page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: declaration template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingDeclarationForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-declaration.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingDeclarationForm(request.POST)
        if form.is_valid():
            status.update(application_id_local, 'first_aid_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/summary?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-declaration.html', variables)


def first_aid_training_renew(request):
    """
    Method returning the template for the First aid training: renew page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: renew template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingRenewForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-renew.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingRenewForm(request.POST)
        if form.is_valid():
            status.update(application_id_local, 'first_aid_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/summary?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-renew.html', variables)


def first_aid_training_training(request):
    """
    Method returning the template for the First aid training: training page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: training template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingTrainingForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-training.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingTrainingForm(request.POST)
        if form.is_valid():
            status.update(application_id_local, 'first_aid_training_status', 'NOT_STARTED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/summary?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-training.html', variables)


def first_aid_training_summary(request):
    """
    Method returning the template for the First aid training: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        training_organisation = FirstAidTraining.objects.get(application_id=application_id_local).training_organisation
        training_course = FirstAidTraining.objects.get(application_id=application_id_local).course_title
        certificate_day = FirstAidTraining.objects.get(application_id=application_id_local).course_day
        certificate_month = FirstAidTraining.objects.get(application_id=application_id_local).course_month
        certificate_year = FirstAidTraining.objects.get(application_id=application_id_local).course_year
        form = FirstAidTrainingSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'training_organisation': training_organisation,
            'training_course': training_course,
            'certificate_day': certificate_day,
            'certificate_month': certificate_month,
            'certificate_year': certificate_year,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingSummaryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-summary.html', variables)


def eyfs(request):
    """
    Method returning the template for the Early Years knowledge page (for a given application) and navigating to
    the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        if application.eyfs_training_status != 'COMPLETED':
            status.update(application_id_local, 'eyfs_training_status', 'IN_PROGRESS')
        return render(request, 'eyfs.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSForm(request.POST)
        if form.is_valid():
            status.update(application_id_local, 'eyfs_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            # Return to the same page
            return render(request, 'eyfs.html', variables)


# View for the Your criminal record (DBS) check: guidance
def dbs_check_guidance(request):
    if request.method == 'GET':
        # If the Your criminal record (DBS) check form is not completed
        application_id_local = request.GET["id"]

        form = DBSCheckGuidanceForm()

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }

        # Access the task page
        return render(request, 'dbs-check-guidance.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = DBSCheckGuidanceForm(request.POST)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).criminal_record_check_status != 'COMPLETED':
                status.update(application_id_local, 'criminal_record_check_status', 'IN_PROGRESS')

            # Go to the phone numbers page
            return HttpResponseRedirect(settings.URL_PREFIX + '/dbs-check/dbs-details?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'dbs-check-guidance.html', variables)


# View for the Your criminal record (DBS) check task: DBS details
def dbs_check_dbs_details(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':
        # If the Your criminal record (DBS) check form is not completed
        application_id_local = request.GET["id"]

        form = DBSCheckDBSDetailsForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }

        # Access the task page
        return render(request, 'dbs-check-dbs-details.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = DBSCheckDBSDetailsForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).criminal_record_check_status != 'COMPLETED':
                status.update(application_id_local, 'criminal_record_check_status', 'IN_PROGRESS')

            # Perform business logic to create or update Your criminal record (DBS) check record in database
            dbs_check_record = dbs_check_logic(application_id_local, form)
            dbs_check_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()

            # Get answers
            cautions_convictions = form.cleaned_data['convictions']

            if cautions_convictions == 'True':

                # Go to the upload DBS page
                return HttpResponseRedirect(settings.URL_PREFIX + '/dbs-check/upload-dbs?id=' + application_id_local)

            elif cautions_convictions == 'False':

                # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
                if Application.objects.get(pk=application_id_local).criminal_record_check_status != 'COMPLETED':
                    status.update(application_id_local, 'criminal_record_check_status', 'COMPLETED')

                # Go to the summary page
                return HttpResponseRedirect(settings.URL_PREFIX + '/dbs-check/summary?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'dbs-check-dbs-details.html', variables)


# View for the Your criminal record (DBS) check: upload DBS
def dbs_check_upload_dbs(request):
    if request.method == 'GET':
        # If the Your criminal record (DBS) check form is not completed
        application_id_local = request.GET["id"]

        form = DBSCheckUploadDBSForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }

        # Access the task page
        return render(request, 'dbs-check-upload-dbs.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = DBSCheckUploadDBSForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Retrieve entered data
            declaration = form.cleaned_data['declaration']

            # Update DBS check record
            dbs_check_record = CriminalRecordCheck.objects.get(application_id=application_id_local)
            dbs_check_record.send_certificate_declare = declaration
            dbs_check_record.save()

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).criminal_record_check_status != 'COMPLETED':
                status.update(application_id_local, 'criminal_record_check_status', 'COMPLETED')

            # Go to the phone numbers page
            return HttpResponseRedirect(settings.URL_PREFIX + '/dbs-check/summary?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'dbs-check-upload-dbs.html', variables)


# View for the Your criminal record (DBS) check task: summary
def dbs_check_summary(request):
    if request.method == 'GET':
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]

        # Retrieve answers
        dbs_certificate_number = CriminalRecordCheck.objects.get(
            application_id=application_id_local).dbs_certificate_number
        cautions_convictions = CriminalRecordCheck.objects.get(application_id=application_id_local).cautions_convictions
        send_certificate_declare = CriminalRecordCheck.objects.get(
            application_id=application_id_local).send_certificate_declare

        form = DBSCheckSummaryForm()

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'dbs_certificate_number': dbs_certificate_number,
            'cautions_convictions': cautions_convictions,
            'criminal_record_check_status': application.criminal_record_check_status,
            'declaration': send_certificate_declare
        }

        # Access the task page
        return render(request, 'dbs-check-summary.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = DBSCheckSummaryForm(request.POST)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Go to the details page
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'dbs-check-summary.html', variables)


# View for the Your health task: intro
def health_intro(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]

        form = HealthIntroForm()

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'health_status': application.health_status
        }

        # Access the task page
        return render(request, 'health-intro.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = HealthIntroForm(request.POST)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).health_status != 'COMPLETED':
                status.update(application_id_local, 'health_status', 'IN_PROGRESS')

            # Go to the phone numbers page
            return HttpResponseRedirect(settings.URL_PREFIX + '/health/booklet?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'health-intro.html', variables)


# View for the Your health task: booklet
def health_booklet(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':
        application_id_local = request.GET["id"]

        form = HealthBookletForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'health_status': application.health_status
        }

        # Access the task page
        return render(request, 'health-booklet.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = HealthBookletForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            # Perform business logic to create or update Your health record in database
            hdb_record = health_check_logic(application_id_local, form)
            hdb_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).health_status != 'COMPLETED':
                status.update(application_id_local, 'health_status', 'COMPLETED')

            # Go to the phone numbers page
            return HttpResponseRedirect(settings.URL_PREFIX + '/health/check-answers?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'health-booklet.html', variables)


# View for the Your health task: summary
def health_check_answers(request):
    if request.method == 'GET':
        # If the Your health form is not completed
        application_id_local = request.GET["id"]

        # Retrieve answers
        send_hdb_declare = HealthDeclarationBooklet.objects.get(
            application_id=application_id_local).send_hdb_declare

        form = HealthBookletForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'send_hdb_declare': send_hdb_declare,
            'health_status': application.health_status,
        }

        # Access the task page
        return render(request, 'health-check-answers.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = HealthBookletForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Go to the details page
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'health-check-answers.html', variables)


# View for the 2 references task: intro
def references_intro(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]

        form = ReferenceIntroForm()

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }

        # Access the task page
        return render(request, 'references-intro.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = ReferenceIntroForm(request.POST)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local, 'references_status', 'IN_PROGRESS')

            # Go to the phone numbers page
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'references-intro.html', variables)


# View for the 2 references task: first reference
def references_first_reference(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':
        # If the 2 references form is not completed
        application_id_local = request.GET["id"]

        form = FirstReferenceForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }

        # Access the task page
        return render(request, 'references-first-reference.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = FirstReferenceForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local, 'references_status', 'IN_PROGRESS')

            # Perform business logic to create or update Your personal details record in database
            references_record = references_first_reference_logic(application_id_local, form)
            references_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()

            # Go to the next page
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/references/first-reference-address?id=' + application_id_local + '&manual=False')

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'references-first-reference.html', variables)


# View for the 2 references task: first reference address
def references_first_reference_address(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':

        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
        manual = request.GET["manual"]

        # If the user wants to use the postcode search
        if manual == 'False':

            form = ReferenceFirstReferenceAddressForm(id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }

            # Access the task page
            return render(request, 'references-first-reference-address.html', variables)

        # If the user wants to manually enter their address
        elif manual == 'True':

            form = ReferenceFirstReferenceAddressManualForm(id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }

            # Access the task page
            return render(request, 'references-first-reference-address-manual.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        manual = request.POST["manual"]

        # If the user wants to use the postcode search
        if manual == 'False':

            form = ReferenceFirstReferenceAddressForm(request.POST, id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            # If the form is successfully submitted (with valid details)
            if form.is_valid():

                # Return to the application's task list
                return HttpResponseRedirect(settings.URL_PREFIX +
                                            '/references/first-reference-address/?id=' + application_id_local + '&manual=False')

            else:

                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'references_status': application.references_status
                }

                # Access the task page
                return render(request, 'references-first-reference-address.html', variables)

        # If the user wants to manually enter their address
        if manual == 'True':

            # Initialise the Your login and contact details form
            form = ReferenceFirstReferenceAddressManualForm(request.POST, id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            # If the form is successfully submitted (with valid details)
            if form.is_valid():

                # Retrieve entered data
                street_line1 = form.cleaned_data.get('street_name_and_number')
                street_line2 = form.cleaned_data.get('street_name_and_number2')
                town = form.cleaned_data.get('town')
                county = form.cleaned_data.get('county')
                country = form.cleaned_data.get('country')
                postcode = form.cleaned_data.get('postcode')

                # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
                if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                    status.update(application_id_local, 'references_status', 'IN_PROGRESS')

                # Update the first reference record in the database
                references_first_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                                  reference=1)
                references_first_reference_address_record.street_line1 = street_line1
                references_first_reference_address_record.street_line2 = street_line2
                references_first_reference_address_record.town = town
                references_first_reference_address_record.county = county
                references_first_reference_address_record.country = country
                references_first_reference_address_record.postcode = postcode
                references_first_reference_address_record.save()

                # Update application date updated
                application = Application.objects.get(pk=application_id_local)
                application.date_updated = current_date
                application.save()

                # Return to the application's task list
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/references/first-reference-contact-details?id=' + application_id_local)

            else:

                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'references_status': application.references_status
                }

                # Access the task page
                return render(request, 'references-first-reference-address-manual.html', variables)


# View for the 2 references: first reference contact details
def references_first_reference_contact_details(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':
        # If the 2 references form is not completed
        application_id_local = request.GET["id"]

        form = ReferenceFirstReferenceContactForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }

        # Access the task page
        return render(request, 'references-first-reference-contact-details.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the 2 references form
        form = ReferenceFirstReferenceContactForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local, 'references_status', 'IN_PROGRESS')

            # Retrieve entered data
            email_address = form.cleaned_data.get('email_address')
            phone_number = form.cleaned_data.get('phone_number')

            # Update the first reference record in the database
            references_first_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                              reference=1)
            references_first_reference_address_record.phone_number = phone_number
            references_first_reference_address_record.email = email_address
            references_first_reference_address_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()

            # Return to the application's task list
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'references-first-reference-contact-details.html', variables)


# View for the 2 references task: first reference
def references_second_reference(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':
        # If the 2 references form is not completed
        application_id_local = request.GET["id"]

        form = SecondReferenceForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }

        # Access the task page
        return render(request, 'references-second-reference.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = SecondReferenceForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local, 'references_status', 'IN_PROGRESS')

            # Perform business logic to create or update Your personal details record in database
            references_record = references_second_reference_logic(application_id_local, form)
            references_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()

            # Go to the next page
            return HttpResponseRedirect(settings.URL_PREFIX +
                                        '/references/second-reference-address?id=' + application_id_local + '&manual=False')

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'references-second-reference.html', variables)


# View for the 2 references task: second reference address
def references_second_reference_address(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':

        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
        manual = request.GET["manual"]

        # If the user wants to use the postcode search
        if manual == 'False':

            form = ReferenceSecondReferenceAddressForm(id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }

            # Access the task page
            return render(request, 'references-second-reference-address.html', variables)

        # If the user wants to manually enter their address
        elif manual == 'True':

            form = ReferenceSecondReferenceAddressManualForm(id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }

            # Access the task page
            return render(request, 'references-second-reference-address-manual.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        manual = request.POST["manual"]

        # If the user wants to use the postcode search
        if manual == 'False':

            form = ReferenceSecondReferenceAddressForm(request.POST, id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            # If the form is successfully submitted (with valid details)
            if form.is_valid():

                # Return to the application's task list
                return HttpResponseRedirect(settings.URL_PREFIX +
                                            '/references/second-reference-address/?id=' + application_id_local + '&manual=False')

            else:

                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'references_status': application.references_status
                }

                # Access the task page
                return render(request, 'references-second-reference-address.html', variables)

        # If the user wants to manually enter their address
        if manual == 'True':

            # Initialise the Your login and contact details form
            form = ReferenceSecondReferenceAddressManualForm(request.POST, id=application_id_local)

            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)

            # If the form is successfully submitted (with valid details)
            if form.is_valid():

                # Retrieve entered data
                street_line1 = form.cleaned_data.get('street_name_and_number')
                street_line2 = form.cleaned_data.get('street_name_and_number2')
                town = form.cleaned_data.get('town')
                county = form.cleaned_data.get('county')
                country = form.cleaned_data.get('country')
                postcode = form.cleaned_data.get('postcode')

                # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
                if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                    status.update(application_id_local, 'references_status', 'IN_PROGRESS')

                # Update the first reference record in the database
                references_second_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                                   reference=2)
                references_second_reference_address_record.street_line1 = street_line1
                references_second_reference_address_record.street_line2 = street_line2
                references_second_reference_address_record.town = town
                references_second_reference_address_record.county = county
                references_second_reference_address_record.country = country
                references_second_reference_address_record.postcode = postcode
                references_second_reference_address_record.save()

                # Update application date updated
                application = Application.objects.get(pk=application_id_local)
                application.date_updated = current_date
                application.save()

                # Return to the application's task list
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/references/second-reference-contact-details?id=' + application_id_local)

            else:

                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'references_status': application.references_status
                }

                # Access the task page
                return render(request, 'references-second-reference-address-manual.html', variables)


# View for the 2 references: second reference contact details
def references_second_reference_contact_details(request):
    # Get current date and time
    current_date = datetime.datetime.today()

    if request.method == 'GET':
        # If the 2 references form is not completed
        application_id_local = request.GET["id"]

        form = ReferenceSecondReferenceContactForm(id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }

        # Access the task page
        return render(request, 'references-second-reference-contact-details.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the 2 references form
        form = ReferenceSecondReferenceContactForm(request.POST, id=application_id_local)

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
            status.update(application_id_local, 'references_status', 'COMPLETED')

            # Retrieve entered data
            email_address = form.cleaned_data.get('email_address')
            phone_number = form.cleaned_data.get('phone_number')

            # Update the first reference record in the database
            references_first_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                              reference=2)
            references_first_reference_address_record.phone_number = phone_number
            references_first_reference_address_record.email = email_address
            references_first_reference_address_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()

            # Return to the application's task list
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/summary?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'references-second-reference-contact-details.html', variables)


# View for the 2 references task: summary
def references_summary(request):
    if request.method == 'GET':
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]

        # Get associated reference record
        first_reference_record = Reference.objects.get(application_id=application_id_local, reference=1)
        second_reference_record = Reference.objects.get(application_id=application_id_local, reference=2)

        # Retrieve answers
        first_reference_first_name = first_reference_record.first_name
        first_reference_last_name = first_reference_record.last_name
        first_reference_relationship = first_reference_record.relationship
        first_reference_years_known = first_reference_record.years_known
        first_reference_months_known = first_reference_record.months_known
        first_reference_street_line1 = first_reference_record.street_line1
        first_reference_street_line2 = first_reference_record.street_line2
        first_reference_town = first_reference_record.town
        first_reference_county = first_reference_record.county
        first_reference_country = first_reference_record.country
        first_reference_postcode = first_reference_record.postcode
        first_reference_phone_number = first_reference_record.phone_number
        first_reference_email = first_reference_record.email
        second_reference_first_name = second_reference_record.first_name
        second_reference_last_name = second_reference_record.last_name
        second_reference_relationship = second_reference_record.relationship
        second_reference_years_known = second_reference_record.years_known
        second_reference_months_known = second_reference_record.months_known
        second_reference_street_line1 = second_reference_record.street_line1
        second_reference_street_line2 = second_reference_record.street_line2
        second_reference_town = second_reference_record.town
        second_reference_county = second_reference_record.county
        second_reference_country = second_reference_record.country
        second_reference_postcode = second_reference_record.postcode
        second_reference_phone_number = second_reference_record.phone_number
        second_reference_email = second_reference_record.email

        form = ReferenceSummaryForm()

        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)

        # Update the status of the task to 'COMPLETED'
        status.update(application_id_local, 'references_status', 'COMPLETED')

        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_reference_first_name': first_reference_first_name,
            'first_reference_last_name': first_reference_last_name,
            'first_reference_relationship': first_reference_relationship,
            'first_reference_years_known': first_reference_years_known,
            'first_reference_months_known': first_reference_months_known,
            'first_reference_street_line1': first_reference_street_line1,
            'first_reference_street_line2': first_reference_street_line2,
            'first_reference_town': first_reference_town,
            'first_reference_county': first_reference_county,
            'first_reference_country': first_reference_country,
            'first_reference_postcode': first_reference_postcode,
            'first_reference_phone_number': first_reference_phone_number,
            'first_reference_email': first_reference_email,
            'second_reference_first_name': second_reference_first_name,
            'second_reference_last_name': second_reference_last_name,
            'second_reference_relationship': second_reference_relationship,
            'second_reference_years_known': second_reference_years_known,
            'second_reference_months_known': second_reference_months_known,
            'second_reference_street_line1': second_reference_street_line1,
            'second_reference_street_line2': second_reference_street_line2,
            'second_reference_town': second_reference_town,
            'second_reference_county': second_reference_county,
            'second_reference_country': second_reference_country,
            'second_reference_postcode': second_reference_postcode,
            'second_reference_phone_number': second_reference_phone_number,
            'second_reference_email': second_reference_email,
            'references_status': application.references_status
        }

        # Access the task page
        return render(request, 'references-summary.html', variables)

    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Your login and contact details form
        form = PersonalDetailsSummaryForm()

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'references_status', 'COMPLETED')

            # Return to the application's task list
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'references-summary.html', variables)


# View for the People in your home task
def other_people(request):
    if request.method == 'POST':

        # Retrieve the application's ID         
        application_id_local = request.POST["id"]

        # Initialise the People in your home form        
        form = OtherPeopleForm(request.POST)

        # If the form is successfully submitted (with valid details)         
        if form.is_valid():
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'people_in_home_status', 'COMPLETED')

        # Return to the application's task list              
        return HttpResponseRedirect(settings.URL_PREFIX + '/task-list/?id=' + application_id_local)

    # If the People in your home form is not completed 
    application_id_local = request.GET["id"]

    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if Application.objects.get(pk=application_id_local).people_in_home_status != 'COMPLETED':
        status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')

    form = OtherPeopleForm()

    # Access the task page
    return render(request, 'other-people.html', {'application_id': application_id_local})


# View for the Declaration task
def declaration(request):
    if request.method == 'POST':

        # Retrieve the application's ID         
        application_id_local = request.POST["id"]

        # Initialise the Declaration form
        form = DeclarationForm(request.POST)

        # If the form is successfully submitted (with valid details) 
        if form.is_valid():
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'declarations_status', 'COMPLETED')

        # Return to the application's task list         
        return HttpResponseRedirect(settings.URL_PREFIX + '/task-list/?id=' + application_id_local)

    # If the People in your home form is not completed    
    application_id_local = request.GET["id"]

    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if Application.objects.get(pk=application_id_local).declarations_status != 'COMPLETED':
        status.update(application_id_local, 'declarations_status', 'COMPLETED')

    form = DeclarationForm()

    # Access the task page
    return render(request, 'declaration.html', {'application_id': application_id_local})


# View for the Confirm your details page
def confirmation(request):
    if request.method == 'POST':

        # Retrieve the application's ID
        application_id_local = request.POST["id"]

        # Initialise the Confirm your details form        
        form = ConfirmForm(request.POST)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            # Return to the application's task list
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list/?id=' + application_id_local)

    # If the Confirm your details form is not completed     
    application_id_local = request.GET["id"]
    form = ConfirmForm()

    # Access the page
    return render(request, 'confirm.html', {'application_id': application_id_local})


# View the Payment page
def payment_view(request):
    if request.method == 'GET':
        # Get the application
        application_id_local = request.GET["id"]

        # As not data is saved for this, a blank payment form is generated with each get request       
        form = PaymentForm()

        # Access the task page
        return render(request, 'payment.html', {'form': form, 'application_id': application_id_local})

    if request.method == 'POST':

        # Retrieve the application's ID        
        application_id_local = request.POST["id"]

        # Initialise the Payment form        
        form = PaymentForm(request.POST)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Get selected payment method
            payment_method = form.cleaned_data['payment_method']

            if (payment_method == 'Credit'):

                # Navigate to the payment details page
                return HttpResponseRedirect(settings.URL_PREFIX + '/payment-details/?id=' + application_id_local)

            elif (payment_method == 'PayPal'):

                # Stay on the same page
                paypal_url = payment.make_paypal_payment("GB", 3500, "GBP", "Childminder Registration Fee",
                                                         application_id_local,
                                                         "http://127.0.0.1:8000/childminder/confirmation/?id=" + application_id_local,
                                                         "http://127.0.0.1:8000/childminder/payment/?id=" + application_id_local,
                                                         "http://127.0.0.1:8000/childminder/payment/?id=" + application_id_local,
                                                         "http://127.0.0.1:8000/childminder/payment/?id=" + application_id_local)

                return HttpResponseRedirect(paypal_url)

        # If there are invalid details
        else:

            # Return to the same page
            return render(request, 'payment.html', {'form': form, 'application_id': application_id_local})


# View the Payment Details page
def card_payment_details(request):
    if request.method == 'GET':
        # Get the application
        application_id_local = request.GET["id"]

        # As no data is saved for this, a blank payment form is generated with each get request       
        form = PaymentDetailsForm()

        # Access the task page
        return render(request, 'payment-details.html', {'form': form, 'application_id': application_id_local})

    if request.method == 'POST':

        # Get the application
        application_id_local = request.POST["id"]

        # Initialise the Payment Details form
        form = PaymentDetailsForm(request.POST)

        # If the form is successfully submitted (with valid details)
        if form.is_valid():

            # Retrieve data
            card_number = re.sub('[ -]+', '', request.POST["card_number"])
            cardholders_name = request.POST["cardholders_name"]
            card_security_code = request.POST["card_security_code"]
            expiry_month = request.POST["expiry_date_0"]
            expiry_year = request.POST["expiry_date_1"]

            # Make payment
            payment_response = payment.make_payment(3500, cardholders_name, card_number, card_security_code,
                                                    expiry_month, expiry_year, 'GBP', application_id_local,
                                                    application_id_local)
            # Parse payment response
            parsed_payment_response = json.loads(payment_response.text)
            # If the payment is successful
            if payment_response.status_code == 201:
                application = Application.objects.get(pk=application_id_local)
                login_id = application.login_id.login_id
                login_record = UserDetails.objects.get(pk=login_id)
                personal_detail_id = ApplicantPersonalDetails.objects.get(
                    application_id=application_id_local).personal_detail_id
                applicant_name_record = ApplicantName.objects.get(personal_detail_id=personal_detail_id)
                email_response = payment.payment_email(login_record.email, applicant_name_record.first_name)

                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'order_code': parsed_payment_response["orderCode"],
                }

                # Go to payment confirmation page                         
                return HttpResponseRedirect(request, '/confirmation/?id=' + application_id_local, variables)

            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'error_flag': 1,
                    'error_message': parsed_payment_response["message"],
                }

            # Return to the application's task list    
            return HttpResponseRedirect(request, '/payment-details/?id=' + application_id_local, variables)

        # If there are invalid details
        else:

            variables = {
                'form': form,
                'application_id': application_id_local
            }

            # Return to the same page
            return render(request, 'payment-details.html', variables)


def payment_confirmation(request):
    if request.method == 'GET':

        application_id_local = request.GET['id']
        order_code = request.GET['orderCode']

        if payment.check_payment(order_code) == 200:
            variables = {
                'application_id': application_id_local,
                'order_code': request.GET["orderCode"],
            }

            return render(request, 'payment-confirmation.html', variables)
        else:

            form = PaymentForm()

            variables = {'form': form, 'application_id': application_id_local}

            return HttpResponseRedirect(settings.URL_PREFIX + '/payment/?id=' + application_id_local, variables)


# View the Application saved page
def application_saved(request):
    if request.method == 'POST':

        # Retrieve the application's ID         
        application_id_local = request.POST["id"]

        # Initialise the Application saved form        
        form = ApplicationSavedForm(request.POST)

        # If the form is successfully submitted (with valid details)        
        if form.is_valid():
            # Stay on the same page
            return HttpResponseRedirect(settings.URL_PREFIX + '/application-saved/?id=' + application_id_local)

    # If the Application saved form is not completed
    application_id_local = request.GET["id"]
    form = ApplicationSavedForm()

    # Access the page
    return render(request, 'application-saved.html', {'form': form, 'application_id': application_id_local})


# Reset view, to set all tasks to To Do
def reset(request):
    # Create a list of task statuses
    SECTION_LIST = ['login_details_status', 'personal_details_status', 'childcare_type_status',
                    'first_aid_training_status', 'eyfs_training_status', 'criminal_record_check_status',
                    'health_status', 'references_status', 'people_in_home_status', 'declarations_status']

    # Retrieve the application's ID     
    application_id_local = request.GET["id"]

    # For each task in the list of task statuses
    for section in SECTION_LIST:
        # Set the progress status to To Do
        status.update(application_id_local, section, 'NOT_STARTED')

    # Access the task list   
    return HttpResponseRedirect(settings.URL_PREFIX + '/task-list/?id=' + application_id_local)
