'''
Created on 15 Dec 2017

OFS-MORE: Apply to be a Childminder Beta

@author: Informed Solutions
'''

from .models import Applicant_Names, Applicant_Personal_Details, Application, Childcare_Type, First_Aid_Training, Login_And_Contact_Details, Criminal_Record_Check, References, Health_Declaration_Booklet
from childminder.wsgi import application


# Business logic to create or update a Type of childcare record
def Childcare_Type_Logic(application_id_local, zero_to_five_status, five_to_eight_status, eight_plus_status):
    
    # Retrieve the application's ID
    this_application = Application.objects.get(application_id=application_id_local)
    
    # If the user entered information for this task for the first time
    if Childcare_Type.objects.filter(application_id=application_id_local).count() == 0:
                
        # Create a new Type of childcare record with the entered data
        childcare_type_record = Childcare_Type(zero_to_five=zero_to_five_status, five_to_eight=five_to_eight_status, eight_plus=eight_plus_status, application_id=this_application)
            
    # If the user previously entered information for this task
    elif Childcare_Type.objects.filter(application_id=application_id_local).count() > 0:
            
        # Retrieve the Type of childcare record corresponding to the application
        childcare_type_record = Childcare_Type.objects.get(application_id=application_id_local)
        # Update the record
        childcare_type_record.zero_to_five = zero_to_five_status
        childcare_type_record.five_to_eight = five_to_eight_status
        childcare_type_record.eight_plus = eight_plus_status
    
    return childcare_type_record


# Business logic to create or update a Your login and contact details record
def Login_Contact_Logic(application_id_local, email_address):

    # Retrieve the application's ID
    this_application = Application.objects.get(application_id=application_id_local)

    # If the user entered information for this task for the first time
    if Login_And_Contact_Details.objects.filter(application_id=application_id_local).count() == 0:
            
        # Create a new Your login and contact details record corresponding to the application
        login_and_contact_details_record = Login_And_Contact_Details(email=email_address, application_id=this_application)
            
    # If the user previously entered information for this task
    elif Login_And_Contact_Details.objects.filter(application_id=application_id_local).count() > 0:
                
        # Retrieve the Your login and contact details record corresponding to the application
        login_and_contact_details_record = Login_And_Contact_Details.objects.get(application_id=application_id_local)
        # Update the record
        login_and_contact_details_record.email = email_address

    return login_and_contact_details_record


# Business logic to create or update a Your personal details record
def Personal_Logic(application_id_local, first_name, middle_names, last_name):

    # Retrieve the application's ID
    this_application = Application.objects.get(application_id=application_id_local)
    
    # If the user entered information for this task for the first time
    if Applicant_Personal_Details.objects.filter(application_id=application_id_local).count() == 0:
        
        # Create a new Applicant_Personal_Details record corresponding to the application, of which the generated personal_details_id will be used        
        personal_details_record = Applicant_Personal_Details(birth_day=0, birth_month=0, birth_year=0, application_id=this_application)
        personal_details_record.save()
        personal_detail_id_local = Applicant_Personal_Details.objects.get(application_id=application_id_local)
        
        # Create a new Your personal details record corresponding to the application    
        applicant_names_record = Applicant_Names(current_name='True', first_name=first_name, middle_names=middle_names, last_name=last_name, personal_detail_id=personal_detail_id_local)
            
    # If a record exists, update it
    elif Applicant_Personal_Details.objects.filter(application_id=application_id_local).count() > 0:
        
        # Retrieve the personal_details_id corresponding to the application       
        personal_detail_id_local = Applicant_Personal_Details.objects.get(application_id=application_id_local).personal_detail_id
        # Retrieve the Your personal details record corresponding to the application
        applicant_names_record = Applicant_Names.objects.get(personal_detail_id=personal_detail_id_local)
        # Update the record
        applicant_names_record.first_name = first_name
        applicant_names_record.middle_names = middle_names
        applicant_names_record.last_name = last_name
    
    return applicant_names_record


# Business logic to create or update a First aid training record
def First_Aid_Logic(application_id_local, training_organisation, course_title, course_day, course_month, course_year):
    
    # Retrieve the application's ID
    this_application = Application.objects.get(application_id=application_id_local)
    
    # If the user entered information for this task for the first time
    if First_Aid_Training.objects.filter(application_id=application_id_local).count() == 0:
                
        # Create a new First aid training record corresponding to the application
        first_aid_training_record = First_Aid_Training(training_organisation=training_organisation,course_title=course_title, course_day=course_day, course_month=course_month, course_year=course_year, application_id=this_application)
            
    # If a record exists, update it
    elif First_Aid_Training.objects.filter(application_id=application_id_local).count() > 0:
        
        # Retrieve the First aid training record corresponding to the application      
        first_aid_training_record = First_Aid_Training.objects.get(application_id=application_id_local)
        # Return the record
        first_aid_training_record.training_organisation = training_organisation
        first_aid_training_record.course_title = course_title
        first_aid_training_record.course_day = course_day
        first_aid_training_record.course_month = course_month
        first_aid_training_record.course_year = course_year
    
    return first_aid_training_record

def dbs_check_logic(application_id_local, form):
    
    # If no record exists, create a new one
    if Criminal_Record_Check.objects.filter(application_id=application_id_local).count() == 0:
    
        c = Criminal_Record_Check(dbs_certificate_number=form.cleaned_data.get('dbs_certificate_number'), cautions_convictions=form.cleaned_data.get('convictions'), application_id=Application.objects.get(application_id=application_id_local))
    
    # If a record exists, update it
    elif Criminal_Record_Check.objects.filter(application_id=application_id_local).count() > 0:
        
        c = Criminal_Record_Check.objects.get(application_id=application_id_local)
        c.dbs_certificate_number = form.cleaned_data.get('dbs_certificate_number')
        c.cautions_convictions = form.cleaned_data.get('convictions')
        
    return(c)
                
def references_check_logic(application_id_local, form):
    
    # If no record exists, create a new one
    if References.objects.filter(application_id=application_id_local).count() == 0:
        
        r = References(first_name=form.cleaned_data.get('first_name'),last_name=form.cleaned_data.get('last_name'),relationship=form.cleaned_data.get('relationship'),years_known=0,months_known=0,street_line1='',street_line2='',town='',county='',country='',postcode='',phone_number='',email='',application_id=Application.objects.get(application_id=application_id_local))
    
    # If a record exists, update it
    elif References.objects.filter(application_id=application_id_local).count() > 0:
        
        r = References.objects.get(application_id=application_id_local)
        r.first_name = form.cleaned_data.get('first_name')
        r.last_name = form.cleaned_data.get('last_name')
        r.relationship = form.cleaned_data.get('relationship')

    return(r)

def health_check_logic(application_id_local, form):
    
    # If no record exists, create a new one
    if Health_Declaration_Booklet.objects.filter(application_id=application_id_local).count() == 0:
                
        h = Health_Declaration_Booklet(movement_problems=form.cleaned_data.get('walking_bending'), breathing_problems=form.cleaned_data.get('asthma_breathing'), heart_disease=form.cleaned_data.get('heart_disease'), blackout_epilepsy=form.cleaned_data.get('blackout_epilepsy'), mental_health_problems=form.cleaned_data.get('mental_health'), alcohol_drug_problems=form.cleaned_data.get('alcohol_drugs'), application_id=Application.objects.get(application_id=application_id_local))

            
    # If a record exists, update it
    elif Health_Declaration_Booklet.objects.filter(application_id=application_id_local).count() > 0:
                
        h = Health_Declaration_Booklet.objects.get(application_id=application_id_local)
        h.movement_problems = form.cleaned_data.get('walking_bending')
        h.breathing_problems = form.cleaned_data.get('asthma_breathing')
        h.heart_disease = form.cleaned_data.get('heart_disease')
        h.blackout_epilepsy = form.cleaned_data.get('blackout_epilepsy')
        h.mental_health_problems = form.cleaned_data.get('mental_health')
        h.alcohol_drug_problems = form.cleaned_data.get('alcohol_drugs')

    return(h)