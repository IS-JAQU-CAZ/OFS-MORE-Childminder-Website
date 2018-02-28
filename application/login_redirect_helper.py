"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- login_redirect_help.py --

@author: Informed Solutions
"""

from django.conf import settings
from django.http import HttpResponseRedirect


def redirect_by_status(application):
    """
    Helper method to calculate a redirect that a user should be issued after logging in
    based on an application's current status
    :param application: the application to be logged into
    :return: an HttpResponseRedirect to a landing page based on an application's current status
    """
    # If application is still being drafted, return user to task list
    if application.application_status == 'DRAFTING':
        response = HttpResponseRedirect(
            settings.URL_PREFIX + '/task-list/?id=' + str(application.application_id))

    # If application is submitted but awaiting ARC review, or in the process of being reviewed,
    # redirect the user to an information page informing them that no action is required of them
    if application.application_status == 'ARC_REVIEW' or application.application_status == 'SUBMITTED':
        response = HttpResponseRedirect(
            settings.URL_PREFIX + '/awaiting-review/?id=' + str(application.application_id))

    # If application status indicates user must supply further information or correct a submission,
    # redirect them to the task list
    if application.application_status == 'FURTHER_INFORMATION':
        response = HttpResponseRedirect(
            settings.URL_PREFIX + '/task-list/?id=' + str(application.application_id))

    # If accepted move to SUBMITTED send to confirmation view saying Ofsted are performing background
    # checks
    if application.application_status == 'ACCEPTED':
        response = HttpResponseRedirect(
            settings.URL_PREFIX + '/accepted/?id=' + str(application.application_id))

    return response

