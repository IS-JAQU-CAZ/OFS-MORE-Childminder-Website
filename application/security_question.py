"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- security_question.py --

@author: Informed Solutions
"""

from django.shortcuts import render

from application.forms import SecurityQuestionForm, SecurityDateForm
from application.utils import date_combiner
from . import login_redirect_helper
from .middleware import CustomAuthenticationHandler
from .models import Application, UserDetails, ApplicantHomeAddress, ApplicantPersonalDetails, AdultInHome, \
    CriminalRecordCheck


def load(request):
    """
    Method returning the template for the security question verification page
    and navigating to the corresponding task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered security question verification template
    """
    if request.method == 'GET':
        app_id = request.GET['id']
        question = get_security_question(app_id)
        forms = get_forms(app_id, question)

        variables = {'forms': forms, 'application_id': app_id, 'question': question}

        return render(request, 'security_question.html', variables)

    if request.method == 'POST':
        app_id = request.POST['id']
        question = get_security_question(app_id)
        forms = post_forms(question, request.POST, app_id)
        application = Application.objects.get(pk=app_id)
        acc = UserDetails.objects.get(application_id=application)
        security_question = acc.security_question
        if forms:
            response = login_redirect_helper.redirect_by_status(application)

            # Create session issue custom cookie to user
            CustomAuthenticationHandler.create_session(response, acc.email)

            # Forward back onto application
            return response
        else:
            variables = {
                'forms': get_forms(app_id, question),
                'application_id': app_id,
                'question': question
            }
            return render(request, 'security_question.html', variables)


def get_answer(question, app_id):
    question = ''
    date = {'day':'','month':'','year':''}

    app = Application.objects.get(application_id=app_id)
    acc = UserDetails.objects.get(application_id=app)
    if 'mobile' in question:
        print(acc.mobile_number)
        question = acc.mobile_number
    if 'postcode' in question:
        home = ApplicantHomeAddress.objects.get(application_id=app)
        date = ApplicantPersonalDetails.objects.get(application_id=app)
        question = home.postcode
        date['day'] = date.birth_day
        date['month'] = date.birth_month
        date['year'] = date.birth_year
    if 'oldest' in question:
        date = AdultInHome.objects.get(application_id=app)
        date['day'] = date.day
        date['month'] = date.month
        date['year'] = date.year
    if 'dbs' in question:
        dbs = CriminalRecordCheck.objects.get(application_id=app)
        question = dbs.dbs_certificate_number

    return {'question':question,'date':date}


def post_forms(question, r, app_id):
    form_list = []
    answer = get_answer(question, app_id)
    field_answer = answer['question']
    date_answer = answer['date']
    if 'mobile' in question:
        form_list.append(SecurityQuestionForm(r, answer=field_answer))
    if 'postcode' in question:
        form_list.append(SecurityQuestionForm(r, answer=field_answer))
        form_list.append(SecurityDateForm(r, day=date_answer['day'], month=date_answer['month'], year=date_answer['year']))
    if 'oldest' in question:
        form_list.append(SecurityDateForm(r, day=date_answer['day'], month=date_answer['month'], year=date_answer['year']))
    if 'dbs' in question:
        form_list.append(SecurityQuestionForm(r, answer=field_answer))

    for i in form_list:
        if not i.is_valid():
            return False
        else:
            i.clean_security_answer()

    return True


def get_forms(app_id, question):
    form_list = []
    app = Application.objects.get(application_id=app_id)
    acc = UserDetails.objects.get(application_id=app)
    if 'mobile' in question:
        form_list.append(SecurityQuestionForm(answer=acc.mobile_number))
    if 'postcode' in question:
        home = ApplicantHomeAddress.objects.get(application_id=app)
        date = ApplicantPersonalDetails.objects.get(application_id=app)
        form_list.append(SecurityQuestionForm(answer=home.postcode))
        form_list.append(SecurityDateForm(day=date.birth_day, month=date.birth_month, year=date.birth_year))
    if 'oldest' in question:
        date = AdultInHome.objects.get(application_id=app)
        form_list.append(SecurityDateForm(day=date.day, month=date.month, year=date.year))
    if 'dbs' in question:
        dbs = CriminalRecordCheck.objects.get(application_id=app)
        form_list.append(SecurityQuestionForm(answer=dbs.dbs_certificate_number))

    return form_list


def get_security_question(app_id):
    app = Application.objects.get(pk=app_id)
    acc = UserDetails.objects.get(application_id=app_id)
    question = ''
    if len(acc.mobile_number) != 0:
        question = 'mobile'
        if app.personal_details_status == 'COMPLETED':
            # set form to ask for birth day and postcode
            question = 'postcode'
            if app.people_in_home_status == 'COMPLETED':
                question = 'oldest'
                if app.criminal_record_check_status == 'COMPLETED':
                    question = 'dbs'
    return question
