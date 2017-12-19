'''
Created on 7 Dec 2017

OFS-MORE: Apply to be a Childminder Beta

@author: Informed Solutions
'''

from application import status

from .business_logic import Childcare_Type_Logic, First_Aid_Logic, Login_Contact_Logic, Personal_Logic, dbs_check_logic
from django.template import Context
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from .forms import TypeOfChildcare, ContactEmail, DBSCheck, PersonalDetails, FirstAidTraining, EYFS, HealthDeclarationBooklet, OtherPeople, ReferenceForm, Declaration, Confirm, Payment

from .models import Application, Criminal_Record_Check, Login_And_Contact_Details, Applicant_Personal_Details, Applicant_Names, First_Aid_Training, Health_Declaration_Booklet, References, Childcare_Type
from application.business_logic import references_check_logic,\
    health_check_logic



# View for the start page
def StartPageView(request):
    
    # Create a new application
    application = Application.objects.create(
        login_details_status = 'NOT_STARTED',
        personal_details_status = 'NOT_STARTED',
        childcare_type_status = 'NOT_STARTED',
        first_aid_training_status = 'NOT_STARTED',
        eyfs_training_status = 'NOT_STARTED',
        criminal_record_check_status = 'NOT_STARTED',
        health_status = 'NOT_STARTED',
        references_status = 'NOT_STARTED',
        people_in_home_status = 'NOT_STARTED',
        declarations_status = 'NOT_STARTED'
    )
    
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
            
            # When the Declarations task is complete, enable link to confirm details
            if (application_status_context['declaration_status'] == 'COMPLETED'):
                
                application_status_context['confirm_details'] = True
                
            else:
                
                application_status_context['confirm_details'] = False

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
    # Update the status of the task to 'IN_PROGRESS'
    status.update(application_id_local, 'childcare_type_status', 'IN_PROGRESS')
    form = TypeOfChildcare(id = application_id_local)
    
    # Return to the application's task list
    return render(request, 'childcare.html', {'form': form, 'application_id': application_id_local})


# View for the Your login and contact details task
def ContactEmailView(request):
    
    if request.method =='POST':
        
        # Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your login and contact details form
        form = ContactEmail(request.POST,id = application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'login_details_status', 'COMPLETED')
            
            # Perform business logic to create or update Your login and contact details record in database
            login_and_contact_details_record = Login_Contact_Logic(application_id_local, form)
            login_and_contact_details_record.save()
            
        # Return to the application's task list    
        return HttpResponseRedirect('/task-list?id=' + application_id_local)

    # If the Your login and contact details form is not completed
    application_id_local = request.GET["id"]
    # Update the status of the task to 'IN_PROGRESS'
    status.update(application_id_local, 'login_details_status', 'IN_PROGRESS')
    form = ContactEmail(id = application_id_local)       
    
    # Return to the application's task list
    return render(request, 'contact-email.html', {'form': form,'application_id': application_id_local})


# View for the Your personal details task
def PersonalDetailsView(request):
    
    if request.method =='POST':
        
        #Retrieve the application's ID
        application_id_local = request.POST["id"]
        
        # Initialise the Your personal details form
        form = PersonalDetails(request.POST, id = application_id_local)
        
        # If the form is successfully submitted (with valid details)
        if form.is_valid():            
            
            # Update the status of the task to 'COMPLETED'
            status.update(application_id_local, 'personal_details_status', 'COMPLETED')
            
            # Perform business logic to create or update Your personal details record in database
            applicant_names_record = Personal_Logic(application_id_local, form)
            applicant_names_record.save()
        
        # Return to the application's task list
        return HttpResponseRedirect('/task-list?id=' + application_id_local)

    # If the Your personal detaails form is not completed
    application_id_local = request.GET["id"]
    # Update the status of the task to 'IN_PROGRESS'
    status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')
    form = PersonalDetails(id = application_id_local)
    
    # Return to the application's task list
    return render(request, 'personal-details.html', {'form': form,'application_id': application_id_local})


# View for the First aid training task
def FirstAidTrainingView(request):
    
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
    
        # Return to the application's task list   
        return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    # If the First aid training form is not completed
    application_id_local = request.GET["id"]
    # Update the status of the task to 'IN_PROGRESS'
    status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
    form = FirstAidTraining(id = application_id_local)
    
    # Return to the application's task list    
    return render(request, 'first-aid.html', {'form': form,'application_id': application_id_local})



def DeclarationView(request):

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = Declaration(request.POST)
        
        print(form.is_valid())
        
        if form.is_valid():
            
            status.update(application_id_local, 'declarations_status', 'COMPLETED')
            
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    application_id_local = request.GET["id"]
    status.update(application_id_local, 'declarations_status', 'COMPLETED')
    form = Declaration()
    
    return render(request, 'declaration.html', {'application_id': application_id_local})


def DBSCheckView(request):
    if request.method =='POST':
        application_id_local = request.POST["id"]
        form = DBSCheck(request.POST, id = application_id_local)
        
        if form.is_valid():
            
            status.update(application_id_local, 'criminal_record_check_status', 'COMPLETED')
            
            dbs_check_record = dbs_check_logic(application_id_local, form)
            dbs_check_record.save()
            
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    application_id_local = request.GET["id"]
    
    status.update(application_id_local, 'criminal_record_check_status', 'IN_PROGRESS')

    form = DBSCheck(id = application_id_local)       
    return render(request, 'dbs-check.html', {'form': form,'application_id': application_id_local})

def EYFSView(request):
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFS(request.POST)
        
        if form.is_valid():
            
            status.update(application_id_local, 'eyfs_training_status', 'COMPLETED')
            
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    application_id_local = request.GET["id"]
    status.update(application_id_local, 'eyfs_training_status', 'IN_PROGRESS')
    form = EYFS()
    
    return render(request, 'eyfs.html', {'application_id': application_id_local})

def ConfirmationView(request):
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = Confirm(request.POST)
        
        if form.is_valid():
            
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    application_id_local = request.GET["id"]
    form = Confirm()
    
    return render(request, 'confirm.html', {'application_id': application_id_local})

def OtherPeopleView(request):
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeople(request.POST)
        
        if form.is_valid():
            
            status.update(application_id_local, 'people_in_home_status', 'COMPLETED')
            
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    application_id_local = request.GET["id"]
    status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')
    form = OtherPeople()
    
    
    return render(request, 'other-people.html', {'application_id': application_id_local})

def ReferencesView(request):
    
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceForm(request.POST,id = application_id_local)
        
        if form.is_valid():
            
            status.update(application_id_local, 'references_status', 'COMPLETED')
            
            references_record = references_check_logic(application_id_local, form)
            references_record.save()
            
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    application_id_local = request.GET["id"]
    status.update(application_id_local, 'references_status', 'IN_PROGRESS')
    form = ReferenceForm(id = application_id_local)
    
    return render(request, 'references.html', {'form': form,'application_id': application_id_local})   

def HealthView(request):
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = HealthDeclarationBooklet(request.POST, id = application_id_local)
        
        if form.is_valid():
            
            status.update(application_id_local, 'health_status', 'COMPLETED')
            
            health_record = health_check_logic(application_id_local, form)
            health_record.save()
            
            return HttpResponseRedirect('/task-list/?id=' + application_id_local)
    
    application_id_local = request.GET["id"]
    status.update(application_id_local, 'health_status', 'IN_PROGRESS')
    form = HealthDeclarationBooklet(id = application_id_local)
    
    return render(request, 'health.html', {'form': form,'application_id': application_id_local})

def ResetView(request):
    SECTION_LIST = ['login_details_status', 'personal_details_status', 'childcare_type_status', 
                    'first_aid_training_status', 'eyfs_training_status', 'criminal_record_check_status'
                    , 'health_status', 'references_status', 'people_in_home_status', 'declarations_status']    
    application_id_local = request.GET["id"]
    
    for section in SECTION_LIST:
        status.update(application_id_local, section, 'NOT_STARTED')
        
    return HttpResponseRedirect('/task-list/?id=' + application_id_local)

def PaymentView(request):
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = Payment(request.POST)
        
        if form.is_valid():
            
            return HttpResponseRedirect('/payment/?id=' + application_id_local)
    
    application_id_local = request.GET["id"]
    form = Payment()
    
    return render(request, 'payment.html', {'form': form, 'application_id': application_id_local})