"""
View logic for rendering the costs page
"""
from django.shortcuts import render
from ..utils import build_url
from ..models import Application


def costs(request):
    """
    Method for rendering the costs page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered costs template
    """
    application_id_local = request.GET.get('id')
    context = {
        'application_id': application_id_local
    }
    if application_id_local is not None:
        application = Application.objects.get(pk=application_id_local)
        url_params = {'id': application_id_local, 'get': True}
        status = application.application_status

        # render either confirmation or task list view, depending on if application has been submitted
        if status == 'SUBMITTED':
            return_view = 'Payment-Confirmation'
            url_params['orderCode'] = str(application.order_code)
        elif status == 'ARC_REVIEW':
            return_view = 'Awaiting-Review-View'
            url_params['orderCode'] = str(application.order_code)
        elif status == 'ACCEPTED':
            return_view = 'Accepted-View'
            url_params['orderCode'] = str(application.order_code)
        else:
            return_view = 'Task-List-View'

        # build url to be passed to the return button
        context['return_url'] = build_url(return_view, get=url_params)

    return render(request, 'costs-guidance.html', context)

