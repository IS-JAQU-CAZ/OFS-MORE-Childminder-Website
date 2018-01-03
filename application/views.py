'''
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- Views --

@author: Informed Solutions
'''

from application import status

from .business_logic import (Childcare_Type_Logic, dbs_check_logic, First_Aid_Logic, health_check_logic, Login_Contact_Logic, Login_Contact_Logic_Phone, Personal_DOB_Logic, Personal_Home_Address_Logic,
                            Personal_Name_Logic, references_check_logic)

from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ApplicationSaved, Confirm, ContactEmail, ContactPhone, ContactSummary, DBSCheck, EmailLogin, Declaration, EYFS, FirstAidTraining, HealthDeclarationBooklet, OtherPeople, Payment, PaymentDetails, PersonalDetailsDOB, PersonalDetailsName, PersonalDetailsGuidance, PersonalDetailsHomeAddress, PersonalDetailsHomeAddressManual, Question, ReferenceForm, TypeOfChildcare

from .models import Application, Login_And_Contact_Details

import datetime



# View for the start page
def StartPageView(request):
    
    # Create a blank user
    user = Login_And_Contact_Details.objects.create()
    
    # Create a new application
    application = Application.objects.create(
        application_type = 'CHILDMINDER',
        login_id = user,
        application_status = 'DRAFTING',
        cygnum_urn = '',
        login_details_status = 'NOT_STARTED',
        personal_details_status = 'NOT_STARTED',
        childcare_type_status = 'NOT_STARTED',
        first_aid_training_status = 'NOT_STARTED',
        eyfs_training_status = 'NOT_STARTED',
        criminal_record_check_status = 'NOT_STARTED',
        health_status = 'NOT_STARTED',
        references_status = 'NOT_STARTED',
        people_in_home_status = 'NOT_STARTED',
        declarations_status = 'NOT_STARTED',
        date_created = datetime.datetime.today(),
        date_updated = datetime.datetime.today(),
        date_accepted = None
    )
    
    # Access the task page
    return render(request, 'start-page.html', ({'id': application.application_id}))


# View for the task list
def LogInView(request):
           
    if request.method == 'GET':
        
        # Retrieve the application's ID
        application_id = request.GET["id"]
        
        # Retrieve application from database
        application = Application.objects.get(pk=application_id)
        
        # Generate a context for task statuses
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
        
        # Temporarily disable Declarations task if other tasks are still in progress
        temp_context = application_status_context
        del temp_context['declaration_status']
        
        if ('NOT_STARTED' in temp_context.values()) or ('IN_PROGRESS' in temp_context.values()):
            
            application_status_context['all_complete'] = False
            
        else:
            
            # Enable Declarations task when all other tasks are complete
            application_status_context['all_complete'] = True
            application_status_context['declaration_status'] = application.declarations_status
            
            # When the Declarations task is complete, enable button to confirm details
            if (application_status_context['declaration_status'] == 'COMPLETED'):
                
                application_status_context['confirm_details'] = True
            
            # Otherwise, disable the button to confirm details    
            else:
                
                application_status_context['confirm_details'] = False

    # Access the task page
    return render(request, 'task-list.html', application_status_context)


# View for the Type of childcare task
def TypeOfChildcareView(request):
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Type of childcare form
        form = TypeOfChildcare(request.POST, id = application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'childcare_type_status', 'COMPLETED')
            
            # Perform business logic to create or update Type of childcare record in database
            childcare_type_record = Childcare_Type_Logic(application_id_local, form)
            childcare_type_record.save()
            
        # Return to the application's task list
        return HttpResponseRedirect('/task-list?id=' + application_id_local)
    
    # If the Type of childcare form is not completed    
    application_id_local = request.GET["id"]
    
    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).childcare_type_status != 'COMPLETED':
        
        status.update(application_id_local, 'childcare_type_status', 'IN_PROGRESS')
        
    form = TypeOfChildcare(id = application_id_local)
    
    # Access the task page
    return render(request, 'childcare.html', {'form': form, 'application_id': application_id_local})


# View for the Your login and contact details task: e-mail address
def ContactEmailView(request):
    
    # Get current date and time
    current_date = datetime.datetime.today()
        
    if request.method =='GET':
          
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
            
        form = ContactEmail(id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
        
        # Access the task page
        return render(request, 'contact-email.html', {'form': form,'application_id': application_id_local, 'login_details_status': application.login_details_status})
    
    if request.method =='POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = ContactEmail(request.POST,id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Perform business logic to create or update Your login and contact details record in database
            login_and_contact_details_record = Login_Contact_Logic(application_id_local, form)
            login_and_contact_details_record.save()
            
            # Update application date updated
            application.date_updated = current_date
            application.save()
            
            # Go to the phone numbers page   
            return HttpResponseRedirect('/account/phone?id=' + application_id_local)
        
        # If there are invalid details
        else:
            
            # Return to the same page
            return render(request, 'contact-email.html', {'form': form,'application_id': application_id_local})


# View for the Your login and contact details task: phone numbers
def ContactPhoneView(request):
    
    # Get current date and time
    current_date = datetime.datetime.today()
    
    if request.method == 'GET':
        
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
            
        form = ContactPhone(id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local) 
    
        # Access the task page
        return render(request, 'contact-phone.html', {'form': form,'application_id': application_id_local, 'login_details_status': application.login_details_status})
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = ContactPhone(request.POST,id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Perform business logic to create or update Your login and contact details record in database
            login_and_contact_details_record = Login_Contact_Logic_Phone(application_id_local, form)
            login_and_contact_details_record.save()
            
            # Update application date updated
            application.date_updated = current_date
            application.save()
            
            # Return to the application's task list    
            return HttpResponseRedirect('/account/question?id=' + application_id_local)
    
        # If there are invalid details
        else:
            
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            
            # Return to the same page
            return render(request, 'contact-phone.html', variables)


# View for the Your login and contact details task: knowledge-based question
def QuestionView(request):
    
    if request.method == 'GET':
        
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
            
        form = Question(id = application_id_local)  
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)      
    
        # Access the task page
        return render(request, 'question.html', {'form': form,'application_id': application_id_local, 'login_details_status': application.login_details_status})
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = Question(request.POST,id = application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Return to the application's task list    
            return HttpResponseRedirect('/account/summary?id=' + application_id_local)
    
        # If there are invalid details
        else:
            
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            
            # Return to the same page
            return render(request, 'question.html', variables)
        

# View for the Your login and contact details task: phone numbers
def ContactSummaryView(request):
    
    if request.method == 'GET':
        
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
        
        # Get associated user login ID
        login_id = Application.objects.get(pk=application_id_local).login_id.login_id
        
        # Retrieve answers
        email = Login_And_Contact_Details.objects.get(login_id=login_id).email
        mobile_number = Login_And_Contact_Details.objects.get(login_id=login_id).mobile_number
        add_phone_number = Login_And_Contact_Details.objects.get(login_id=login_id).add_phone_number
        
        # Update the status of the task to 'COMPLETED'
        if  Application.objects.get(pk = application_id_local).login_details_status != 'COMPLETED':
            
            status.update(application_id_local, 'login_details_status', 'COMPLETED')
            
        form = ContactSummary()
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)      
    
        # Access the task page
        return render(request, 'contact-summary.html', {'form': form,'application_id': application_id_local,'email': email,'mobile_number': mobile_number,'add_phone_number': add_phone_number, 'login_details_status': application.login_details_status, 'childcare_type_status': application.childcare_type_status})
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = ContactSummary()
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'login_details_status', 'COMPLETED')
            
            # Return to the application's task list    
            return HttpResponseRedirect('/childcare?id=' + application_id_local)
    
        # If there are invalid details
        else:
            
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            
            # Return to the same page
            return render(request, 'contact-summary.html', variables)


# View for the Your personal details task: guidance
def PersonalDetailsGuidanceView(request):
        
    if request.method =='GET':
          
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
            
        form = PersonalDetailsGuidance()
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
        
        # Access the task page
        return render(request, 'personal-details-guidance.html', {'form': form,'application_id': application_id_local, 'personal_details_status': application.personal_details_status})
    
    if request.method =='POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = PersonalDetailsGuidance(request.POST)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed    
            if  Application.objects.get(pk = application_id_local).personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
            
            # Go to the phone numbers page   
            return HttpResponseRedirect('/personal-details/name?id=' + application_id_local)
        
        # If there are invalid details
        else:
            
            # Return to the same page
            return render(request, 'personal-details-guidance.html', {'form': form,'application_id': application_id_local})


# View for the Your personal details task: names
def PersonalDetailsNameView(request):

    # Get current date and time
    current_date = datetime.datetime.today()
    
    if request.method == 'GET':
        
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
            
        form = PersonalDetailsName(id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
    
        # Access the task page
        return render(request, 'personal-details-name.html', {'form': form,'application_id': application_id_local, 'personal_details_status': application.personal_details_status})
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = PersonalDetailsName(request.POST,id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed    
            if  Application.objects.get(pk = application_id_local).personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
            
            # Perform business logic to create or update Your personal details record in database
            applicant_names_record = Personal_Name_Logic(application_id_local, form)
            applicant_names_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            
            # Go to the date of birth page    
            return HttpResponseRedirect('/personal-details/dob/?id=' + application_id_local)
    
        # If there are invalid details
        else:
            
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            
            # Return to the same page
            return render(request, 'personal-details-name.html', variables)


# View for the Your personal details task: date of birth
def PersonalDetailsDOBView(request):

    # Get current date and time
    current_date = datetime.datetime.today()
    
    if request.method == 'GET':
        
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
            
        form = PersonalDetailsDOB(id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
    
        # Access the task page
        return render(request, 'personal-details-dob.html', {'form': form,'application_id': application_id_local, 'personal_details_status': application.personal_details_status})
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = PersonalDetailsDOB(request.POST,id = application_id_local)
        
        # Retrieve application from database for Back button/Return to list link logic
        application = Application.objects.get(pk=application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'personal_details_status', 'COMPLETED')
            
            # Perform business logic to create or update Your personal details record in database
            personal_details_record = Personal_DOB_Logic(application_id_local, form)
            personal_details_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            
            # Return to the application's task list    
            return HttpResponseRedirect('/personal-details/home-address?id=' + application_id_local + '&manual=False')
    
        # If there are invalid details
        else:
            
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            
            # Return to the same page
            return render(request, 'personal-details-dob.html', variables)
        

# View for the Your personal details task: home address
def PersonalDetailsHomeAddressView(request):

    # Get current date and time
    current_date = datetime.datetime.today()
    
    if request.method == 'GET':
        
        # If the Your login and contact details form is not completed
        application_id_local = request.GET["id"]
        manual = request.GET["manual"]
        
        if manual == 'False':    
            
            form = PersonalDetailsHomeAddress(id = application_id_local)
            
            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)
        
            # Access the task page
            return render(request, 'personal-details-home-address.html', {'form': form,'application_id': application_id_local, 'personal_details_status': application.personal_details_status})
        
        elif manual == 'True':    
            
            form = PersonalDetailsHomeAddressManual(id = application_id_local)
            
            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)
        
            # Access the task page
            return render(request, 'personal-details-home-address-manual.html', {'form': form,'application_id': application_id_local, 'personal_details_status': application.personal_details_status})
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        manual = request.POST["manual"]
        
        if manual == 'False':
        
            # Initialise the Your login and contact details form
            form = PersonalDetailsHomeAddress(request.POST,id = application_id_local)
            
            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)
            
            # If the form is successfully submitted (with valid details)
            if form.is_valid():
                
                # Return to the application's task list    
                return HttpResponseRedirect('/personal-details/home-address/?id=' + application_id_local + '&manual=False')
            
            else: 
            
                # Access the task page
                return render(request, 'personal-details-home-address.html', {'form': form,'application_id': application_id_local, 'personal_details_status': application.personal_details_status})
            
        if manual == 'True':
        
            # Initialise the Your login and contact details form
            form = PersonalDetailsHomeAddressManual(request.POST,id = application_id_local)
            
            # Retrieve application from database for Back button/Return to list link logic
            application = Application.objects.get(pk=application_id_local)
            
            # If the form is successfully submitted (with valid details)
            if form.is_valid():
                
                # Update the status of the task to 'COMPLETED'
                status.update(application_id_local, 'personal_details_status', 'COMPLETED')
                
                # Perform business logic to create or update Your personal details record in database
                home_address_record = Personal_Home_Address_Logic(application_id_local, form)
                home_address_record.save()
    
                # Update application date updated
                application = Application.objects.get(pk=application_id_local)
                application.date_updated = current_date
                application.save()
                
                # Return to the application's task list    
                return HttpResponseRedirect('/task-list?id=' + application_id_local)
            
            else: 
            
                # Access the task page
                return render(request, 'personal-details-home-address-manual.html', {'form': form,'application_id': application_id_local, 'personal_details_status': application.personal_details_status})   
        
            

# View for the First aid training task
def FirstAidTrainingView(request):

    # Get current date and time
    current_date = datetime.datetime.today()
    
    if request.method =='POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the First aid training form
        form = FirstAidTraining(request.POST,id = application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'first_aid_training_status', 'COMPLETED')
            
            # Perform business logic to create or update First aid training record in database
            first_aid_training_record = First_Aid_Logic(application_id_local, form)
            first_aid_training_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
    
        # Return to the application's task list   
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the First aid training form is not completed
    application_id_local = request.GET["id"]

    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).first_aid_training_status != 'COMPLETED':
        
        status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
        
    form = FirstAidTraining(id = application_id_local)
    
    # Access the task page    
    return render(request, 'first-aid.html', {'form': form,'application_id': application_id_local})


# View for the Early Years knowledge task
def EYFSView(request):
   
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Early Years knowledge form
        form = EYFS(request.POST)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'eyfs_training_status', 'COMPLETED')
            
        # Return to the application's task list    
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the Early Years knowledge form is not completed
    application_id_local = request.GET["id"]

    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).eyfs_training_status != 'COMPLETED':
        
        status.update(application_id_local, 'eyfs_training_status', 'IN_PROGRESS')
    
    form = EYFS()
    
    # Access the task page
    return render(request, 'eyfs.html', {'application_id': application_id_local})


# View for the Your criminal record (DBS) check task
def DBSCheckView(request):

    # Get current date and time
    current_date = datetime.datetime.today()
   
    if request.method =='POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your criminal record (DBS) check form
        form = DBSCheck(request.POST, id = application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'criminal_record_check_status', 'COMPLETED')
            
            # Perform business logic to create or update Your criminal record (DBS) check record in database
            dbs_check_record = dbs_check_logic(application_id_local, form)
            dbs_check_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            
        # Return to the application's task list
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the Your criminal record (DBS) check form is not completed
    application_id_local = request.GET["id"]
    
    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).criminal_record_check_status != 'COMPLETED':
        
        status.update(application_id_local, 'criminal_record_check_status', 'IN_PROGRESS')
    
    form = DBSCheck(id = application_id_local)
    
    # Access the task page
    return render(request, 'dbs-check.html', {'form': form,'application_id': application_id_local})


# View for the Your health task
def HealthView(request):
    
    # Get current date and time
    current_date = datetime.datetime.today()
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your health form
        form = HealthDeclarationBooklet(request.POST, id = application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'            
            status.update(application_id_local, 'health_status', 'COMPLETED')
            
            # Perform business logic to create or update Your health record in database            
            health_record = health_check_logic(application_id_local, form)
            health_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            
        # Return to the application's task list
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the Your health form is not completed    
    application_id_local = request.GET["id"]
    
    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).health_status != 'COMPLETED':
        
        status.update(application_id_local, 'health_status', 'IN_PROGRESS')
    
    form = HealthDeclarationBooklet(id = application_id_local)
    
    # Access the task page
    return render(request, 'health.html', {'form': form,'application_id': application_id_local})


# View for the 2 references task
def ReferencesView(request):

    # Get current date and time
    current_date = datetime.datetime.today()
    
    if request.method == 'POST':
        
        # Retrieve the application's ID        
        application_id_local = request.POST["id"]
        
        # Initialise the 2 references form
        form = ReferenceForm(request.POST,id = application_id_local)
        
        # If the form is successfully submitted (with valid details) 
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'              
            status.update(application_id_local, 'references_status', 'COMPLETED')

            # Perform business logic to create or update 2 references record in database              
            references_record = references_check_logic(application_id_local, form)
            references_record.save()

            # Update application date updated
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()

        # Return to the application's task list            
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the 2 references form is not completed 
    application_id_local = request.GET["id"]

    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).references_status != 'COMPLETED':
        
        status.update(application_id_local, 'references_status', 'IN_PROGRESS')
    
    form = ReferenceForm(id = application_id_local)
    
    # Access the task page
    return render(request, 'references.html', {'form': form,'application_id': application_id_local})  


# View for the People in your home task
def OtherPeopleView(request):
    
    if request.method == 'POST':
        
        # Retrieve the application's ID         
        application_id_local = request.POST["id"]
        
        # Initialise the People in your home form        
        form = OtherPeople(request.POST)
        
        # If the form is successfully submitted (with valid details)         
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED' 
            status.update(application_id_local, 'people_in_home_status', 'COMPLETED')
        
        # Return to the application's task list              
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the People in your home form is not completed 
    application_id_local = request.GET["id"]
    
    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).people_in_home_status != 'COMPLETED':
        
        status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')
    
    form = OtherPeople()
    
    # Access the task page
    return render(request, 'other-people.html', {'application_id': application_id_local}) 


# View for the Declaration task
def DeclarationView(request):

    if request.method == 'POST':
        
        # Retrieve the application's ID         
        application_id_local = request.POST["id"]
        
        # Initialise the Declaration form
        form = Declaration(request.POST)
        
        # If the form is successfully submitted (with valid details) 
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'            
            status.update(application_id_local, 'declarations_status', 'COMPLETED')
            
        # Return to the application's task list         
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the People in your home form is not completed    
    application_id_local = request.GET["id"]
    
    # Update the status of the task to 'IN_PROGRESS' if the task has not yet been completed
    if  Application.objects.get(pk = application_id_local).declarations_status != 'COMPLETED':
    
        status.update(application_id_local, 'declarations_status', 'COMPLETED')
    
    form = Declaration()
    
    # Access the task page
    return render(request, 'declaration.html', {'application_id': application_id_local})


# View for the Confirm your details page
def ConfirmationView(request):
    
    if request.method == 'POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Confirm your details form        
        form = Confirm(request.POST)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Return to the application's task list 
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)

    # If the Confirm your details form is not completed     
    application_id_local = request.GET["id"]
    form = Confirm()
    
    # Access the page
    return render(request, 'confirm.html', {'application_id': application_id_local})


# View the Payment page
def PaymentView(request):
    
    if request.method == 'POST':
        
        # Retrieve the application's ID        
        application_id_local = request.POST["id"]
        
        # Initialise the Payment form        
        form = Payment(request.POST)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Stay on the same page
            return HttpResponseRedirect('/payment-details/?id=' + application_id_local)
    
    # If the Payment form is not completed  
    application_id_local = request.GET["id"]
    form = Payment()
    
    # Access the page
    return render(request, 'payment.html', {'form': form, 'application_id': application_id_local})



def CardPaymentDetailsView(request):
    
    if request.method == 'POST':
        
        application_id_local = request.POST["id"]
        
        form = PaymentDetails(request.POST)
        
        if form.is_valid():
            
            return HttpResponseRedirect('/paymentconfirmation/?id=' + application_id_local)
        
    application_id_local = request.GET["id"]
    form = PaymentDetails()
    
    return render(request, 'payment-details.html', {'form': form, 'application_id': application_id_local})


# View the Application saved page
def ApplicationSavedView(request):
    
    if request.method == 'POST':
        
        # Retrieve the application's ID         
        application_id_local = request.POST["id"]
        
        # Initialise the Application saved form        
        form = ApplicationSaved(request.POST)
        
        # If the form is successfully submitted (with valid details)        
        if form.is_valid():
            
            # Stay on the same page
            return HttpResponseRedirect('/application-saved/?id=' + application_id_local)
    
    # If the Application saved form is not completed
    application_id_local = request.GET["id"]
    form = ApplicationSaved()
    
    # Access the page
    return render(request, 'application-saved.html', {'form': form, 'application_id': application_id_local})


# Reset view, to set all tasks to To Do
def ResetView(request):
    
    # Create a list of task statuses
    SECTION_LIST = ['login_details_status', 'personal_details_status', 'childcare_type_status', 'first_aid_training_status', 'eyfs_training_status', 'criminal_record_check_status', 'health_status', 'references_status', 'people_in_home_status', 'declarations_status']    
    
    # Retrieve the application's ID     
    application_id_local = request.GET["id"]
    
    # For each task in the list of task statuses
    for section in SECTION_LIST:
        
        # Set the progress status to To Do
        status.update(application_id_local, section, 'NOT_STARTED')
     
    # Access the task list   
    return HttpResponseRedirect('/task-list/?id=' + application_id_local)





#Test View, will change
def existingApplicationView(request):
    form = EmailLogin()
    if request.method =='POST':
        print (request)
    return render(request, 'existing-application.html', {'form': form})