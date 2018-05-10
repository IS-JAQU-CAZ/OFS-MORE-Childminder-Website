"""
Selenium test cases for the Childminder service
"""

import os
import random
from datetime import datetime

from django.core.management import call_command
from django.test import LiveServerTestCase, override_settings, tag
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from .selenium_task_executor import SeleniumTaskExecutor

from faker import Faker

# Configure faker to use english locale
faker = Faker('en_GB')
selenium_driver_out = None


def try_except_method(func):
    """
    :param func: assert method to be used in try/except statement
    :return: decorated method to use in try/except statement
    """

    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            capture_screenshot(func)
            raise e

    return func_wrapper


def capture_screenshot(func):
    global selenium_driver_out
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    scr = selenium_driver_out.find_element_by_tag_name('html')
    scr.screenshot('selenium/screenshot-%s-%s.png' % (func.__name__, now))


@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class ApplyAsAChildminder(LiveServerTestCase):
    port = 8000

    if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
        host = '127.0.0.1'
    else:
        host = '0.0.0.0'

    current_year = datetime.now().year

    def setUp(self):
        base_url = os.environ.get('DJANGO_LIVE_TEST_SERVER_ADDRESS')

        if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
            # If running on a windows host, make sure to drop the
            # geckodriver.exe into your Python/Scripts installation folder
            self.selenium_driver = webdriver.Firefox()
        else:
            # If not using local driver, default requests to a selenium grid server
            self.selenium_driver = webdriver.Remote(
                command_executor=os.environ['SELENIUM_HOST'],
                desired_capabilities={'platform': 'ANY', 'browserName': 'firefox', 'version': ''}
            )

        self.selenium_driver.maximize_window()
        self.selenium_driver.implicitly_wait(20)

        self.verification_errors = []
        self.accept_next_alert = True

        self.selenium_task_executor = SeleniumTaskExecutor(self.selenium_driver, base_url)

        global selenium_driver_out
        selenium_driver_out = self.selenium_driver

        super(ApplyAsAChildminder, self).setUp()

    @try_except_method
    def test_directed_to_local_authority_if_not_eyfs_register(self):
        """
        Tests that a user is directed toward guidance advising them to contact their local authority if
        the ages of children they are minding does not
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 5 to 7 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 10).until(
            expected_conditions.title_contains("Childcare Register"))

        self.assertEqual("Childcare Register",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/form/div/h1").text)

    @try_except_method
    def test_shown_eyfs_only_guidance(self):
        """
        Test to make sure guidance page shown when only minding children up to the age of five gets shown
        if only the "0 to 5 year olds' option is selected on the Age of Children page
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 0-5 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.assertEqual("Early Years Register", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//main[@id='content']/form/div/h1").text)

    @try_except_method
    def test_shown_eyfs_compulsory_part_guidance(self):
        """
        Test to make sure the correct guidance page gets shown when only minding children both up
        to the age of five and between 5 and 7
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 0-5 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

        # Choose 5-7 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.assertEqual("Early Years and Childcare Register (compulsory part)",
                         self.selenium_task_executor.get_driver()
                         .find_element_by_xpath("//main[@id='content']/form/div/h1").text)

    @try_except_method
    def test_can_create_application_using_email_with_apostrophe_and_hyphen(self):
        """
        Test to ensure a user can enter an email where the name includes an apostrophe and/or hyphen
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = 'Alfie-James.O\'Brien@emailtestworld.com'
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)

        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address(test_email)

        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_complete_people_in_your_home_task_with_other_adults_and_children_containing_apostrophe_in_name(self):
        """
        Tests that the people in your home task can still be completed when answering Yes to the question
        'Does anyone aged 16 or over live or work in your home?' but No to the question 'Do you live with any children
        under 16?'
        """
        self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(True, "Dan-D'arcy", "John-O'Paul",
                                                                      "Omar-O\'Leary",
                                                                      random.randint(1, 29),
                                                                      random.randint(1, 12),
                                                                      random.randint(1950, 1990),
                                                                      'Friend', 121212121212, True,
                                                                      "Billie'o-Jo", "Bri'an-James",
                                                                      "O\'Malley-Micheals",
                                                                      random.randint(1, 28),
                                                                      random.randint(1, 12),
                                                                      random.randint(self.current_year - 14,
                                                                                     self.current_year - 1), 'Child')

        self.assertEqual("Done", self.selenium_task_executor.get_driver()
                         .find_element_by_xpath("//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_can_create_application_using_email_with_apostrophe_and_hyphen(self):
        """
        Test to ensure a user can enter an email where the name includes an apostrophe and/or hyphen
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = 'Alfie-James.O\'Brien@emailtestworld.com'
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)

        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address(test_email)

        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_complete_people_in_your_home_task_with_other_adults_and_children_containing_apostrophe_in_name(self):
        """
        Tests that the people in your home task can still be completed when answering Yes to the question
        'Does anyone aged 16 or over live or work in your home?' but No to the question 'Do you live with any children under 16?'
        """
        self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            "Dan-D'arcy", "John-O'Paul", "Omar-O\'Leary",
            random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            True, "Billie'o-Jo", "Bri'an-James", "O\'Malley-Micheals",
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child'
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_shown_both_parts_guidance(self):
        """
        Test to make sure the correct guidance page gets shown when only minding children of all ages
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 0-5 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

        # Choose 5-7 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

        # Choose 8+ year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_2").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.assertEqual("Early Years and Childcare Register (both parts)",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/form/div/h1").text)

    @try_except_method
    def test_can_complete_personal_details_task_when_location_of_care_is_same_as_home_address(self):
        """
        Test to make sure a user can choose Yes to the question Is this where you will be looking after the children?
        """
        self.create_standard_eyfs_application()

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990), True)

        # Check task status marked as Done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

    @try_except_method
    def test_can_complete_dbs_task_without_cautions_or_convictions(self):
        """
        Tests the Criminal record (DBS) check task can be completed when stating that you do not have cautions
        or convictions
        """
        self.create_standard_eyfs_application()

        test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
        self.selenium_task_executor.complete_dbs_task(test_dbs, False)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='dbs']/td/a/strong").text)

    @try_except_method
    def test_can_complete_people_in_your_home_task_without_other_adults_but_with_other_children(self):
        """
        Tests that the people in your home task can still be completed when answering No to the question
        'Does anyone aged 16 or over live or work in your home?'
        """
        self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(
            False,
            None, None, None,
            None, None, None, None, None,
            True, faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child'
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_can_complete_people_in_your_home_task_with_other_adults_but_without_other_children(self):
        """
        Tests that the people in your home task can still be completed when answering Yes to the question
        'Does anyone aged 16 or over live or work in your home?' but No to the question 'Do you live with any children under 16?'
        """
        self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            False, None, None, None,
            None, None, None,
            None
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_can_apply_as_a_childminder_full_question_set(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        self.complete_full_question_set()

        self.selenium_task_executor.complete_review()
        self.selenium_task_executor.complete_declaration()

        # Card number must be 5454... due to this being a Worldpay API test value
        test_cvc = ''.join(str(random.randint(0, 9)) for _ in range(3))
        self.selenium_task_executor.complete_payment(True, 'Visa', '5454545454545454', str(random.randint(1, 12)),
                                                     str(random.randint(self.current_year + 1, self.current_year + 5)),
                                                     faker.name(),
                                                     test_cvc)

    @try_except_method
    def test_sign_out_link_not_shown_when_unauthenticated(self):
        """
        Tests that the sign-out link is not present if a user is not logged in
        """

        self.selenium_task_executor.navigate_to_base_url()
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out')

    @try_except_method
    def test_can_sign_out_when_authenticated(self):
        """
        Tests that the sign-out link is present if a user is logged in and they can successfully sign out
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        self.assertEqual("Application saved", self.selenium_task_executor.get_driver().title)

        # After signing out make sure sign out link no longer shows
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out')

    @try_except_method
    def test_banner_link_returns_user_to_task_list_when_authenticated(self):
        """
        Tests that when a user is logged in clicking the "Register as a childminder" link in the banner returns them to the
        task list
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Register as a childminder').click()
        self.assertEqual("Register as a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_costs_without_authenticating(self):
        """
        Tests the costs page can be accessed without logging in.
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Costs').click()
        self.assertEqual("Costs of becoming a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_costs_when_authenticated(self):
        """
        Tests the costs page can be accessed when logged in.
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Costs').click()
        self.assertEqual("Costs of becoming a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_costs_not_shown_if_further_information_required(self):
        """
        Tests that the costs link is not shown if an application has been returned to the applicant
        """
        # Load fixtures to populate a test application
        call_command("loaddata", "test_returned_application.json", verbosity=0)

        # Note that this email address is loaded from fixture
        self.selenium_task_executor.sign_back_in('test@informed.com')

        # Test that costs link is not shown in header
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('Costs')

        # Test that costs link is not shown above task list
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('more about costs')

        # Test that the grayed out class is present (for unflagged tasks which are disabled)
        self.assertTrue(self.selenium_task_executor.get_driver().find_element_by_class_name('grayed-out'))

        # Test that the task-disabled class is present (for unflagged tasks which are disabled)
        self.assertTrue(self.selenium_task_executor.get_driver().find_element_by_class_name('task-disabled'))

    @try_except_method
    def test_declaration_cannot_be_replayed(self):
        """
        Tests that the costs link is not shown if an application has been returned to the applicant
        """
        # Load fixtures to populate a test application
        call_command("loaddata", "test_returned_application.json", verbosity=0)

        # Note that this email address is loaded from fixture
        self.selenium_task_executor.sign_back_in('test@informed.com')

        self.selenium_task_executor.get_driver().find_element_by_id("health").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//a[contains(@href,'health/booklet/')]").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='review']/td/a/span").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_background_check_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_inspect_home_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_interview_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_share_info_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_display_contact_details_on_web").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_information_correct_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_change_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 10).until(
            expected_conditions.title_contains("Payment confirmed"))

        self.selenium_task_executor.get_driver().back()

        # Check user is redirected to the summary
        self.assertEqual("Payment confirmed", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_help_without_authenticating(self):
        """
        Tests the help page can be accessed without logging in.
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Help').click()
        self.assertEqual("Help and advice", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_help_when_authenticated(self):
        """
        Tests the help page can be accessed once logged in.
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Help').click()
        self.assertEqual("Help and advice", self.selenium_task_executor.get_driver().title)
        self.selenium_task_executor.get_driver().find_element_by_link_text("Return to application").click()
        self.assertEqual("Register as a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_costs(self):
        """
        Tests that the costs page can be reached
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Costs").click()
        self.assertEqual("Costs of becoming a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_begin_returning_user_sign_in_process(self):
        """
        Tests that the sign in page for returning users can be reached
        """
        test_email = self.create_standard_eyfs_application()
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Start now']").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_acc_selection_1-label").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(test_email)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_apply_as_a_childminder_using_full_question_set(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        self.create_standard_eyfs_application()

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            False
        )

        # Check task status marked as Done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

        # When completing first aid training task ensure that certification is within last 3 years
        self.selenium_task_executor.complete_first_aid_training(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 2, self.current_year - 1),
            False
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='first_aid']/td/a/strong").text)

        self.selenium_task_executor.complete_health_declaration_task()

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='health']/td/a/strong").text)

        test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
        self.selenium_task_executor.complete_dbs_task(test_dbs, False)

        self.assertEqual("Done",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//tr[@id='dbs']/td/a/strong").text)

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            True, faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child'
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

        self.selenium_task_executor.complete_references_task(
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email(),
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email()
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='references']/td/a/strong").text)

        self.selenium_task_executor.complete_review()
        self.selenium_task_executor.complete_declaration()

        # Card number must be 5454... due to this being a Worldpay API test value
        test_cvc = ''.join(str(random.randint(0, 9)) for _ in range(3))
        self.selenium_task_executor.complete_payment(True, 'Visa', '5454545454545454', str(random.randint(1, 12)),
                                                     str(random.randint(self.current_year + 1, self.current_year + 5)),
                                                     faker.name(),
                                                     test_cvc)

    @try_except_method
    def test_can_apply_as_a_childminder_no_overnight_care(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, False)

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)

    @try_except_method
    def test_first_aid_out_of_date_guidance_shown(self):
        """
        Test to check that if a first aid training certificate is expired a user is informed they need to update their traininig
        """
        self.create_standard_eyfs_application()

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            False
        )

        # Check task status marked as Done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

        # When completing first aid training task set expired certification year
        self.selenium_task_executor.complete_first_aid_training(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), 2012,
            True
        )

        self.assertEqual("Update your first aid training",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/form/div/h1").text)

    @try_except_method
    def test_cannot_change_email_to_preexisting_one(self):
        """
        Complete application contact details then attempt to change email to one which exists under another application.
        Should .......
        """
        first_email = self.create_standard_eyfs_application()
        second_email = self.create_standard_eyfs_application()

        # Click through to changing email for second account.
        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='email_address']/td/a").click()

        # Change email of second account to the first one.
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(first_email)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        self.assertEqual("We've sent a link to {}".format(first_email),
                         self.selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/p").text)

        # Try to grab email validation URL.
        # Should redirect to bad link; no email validation link sent for preexsiting email.
        self.selenium_task_executor.navigate_to_email_validation_url()
        self.assertEqual('Bad link', self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_cannot_create_multiple_applications_using_same_email(self):
        """
        Test to ensure a user cannot register twice with the same email address
        """
        test_email = self.create_standard_eyfs_application()
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address(test_email)

        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_cancel_application(self):
        """
        Test to assert a new application can be cancelled
        """
        self.create_standard_eyfs_application()

        self.selenium_task_executor.get_driver().find_element_by_link_text("Cancel application").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Cancel Application']").click()
        self.assertEqual("Application Cancelled", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_save_and_exit(self):
        """
        Test to assert a user can save and exit an application
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Save and exit").click()
        self.assertEqual("Application saved", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_task_summaries_display_on_completion(self):
        """
        Tests that once a task is marked as Done, clicking that task from the task list shows the summary page
        """
        self.complete_full_question_set()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='children']/td/a/span").click()
        self.assertEqual("Check your answers: Type of childcare",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='personal_details']/td/a/span").click()
        self.assertEqual("Check your answers: your personal details",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='first_aid']/td/a/span").click()
        self.assertEqual("Check your answers: first aid training",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='health']/td/a/span").click()
        self.assertEqual("Check your answers: your health",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='dbs']/td/a/span").click()
        self.assertEqual("Check your answers: criminal record (DBS) check",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
        self.assertEqual("Check your answers: people in your home",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//input[@value='Confirm and continue']").send_keys(
            Keys.RETURN)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='references']/td/a/span").click()
        self.assertEqual("Check your answers: references",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='review']/td/a/span").click()

    def complete_full_question_set(self):
        """
        Helper method for completing all questions in an application
        """
        self.create_standard_eyfs_application()

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            False
        )

        # Check task status marked as Done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

        # When completing first aid training task ensure that certification is within last 3 years
        self.selenium_task_executor.complete_first_aid_training(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 2, self.current_year - 1),
            False
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='first_aid']/td/a/strong").text)

        self.selenium_task_executor.complete_health_declaration_task()

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='health']/td/a/strong").text)

        test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
        self.selenium_task_executor.complete_dbs_task(test_dbs, True)

        self.assertEqual("Done",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//tr[@id='dbs']/td/a/strong").text)

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            True, faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child'
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

        self.selenium_task_executor.complete_references_task(
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email(),
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email()
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='references']/td/a/strong").text)

    def create_standard_eyfs_application(self):
        """
        Helper method for starting a new application
        :return: email address used to register the application
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)

        return test_email

    def tearDown(self):
        self.selenium_driver.quit()
        super(ApplyAsAChildminder, self).tearDown()
        self.assertEqual([], self.verification_errors)