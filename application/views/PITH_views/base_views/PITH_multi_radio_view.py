from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin

from application.utils import build_url, get_id
from application.models import AdultInHome

class PITHMultiRadioView(TemplateView, TemplateResponseMixin):
    template_name = None
    form_class = None
    success_url = None
    field_name = None

    def get_context_data(self, **kwargs):
        if 'form_list' not in kwargs:
            kwargs['form_list'] = self.get_form_list()
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self, kwargs):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs.update({
            'initial': self.get_initial()
        })

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        return kwargs

    def get_success_url(self, get=None):
        """
        This view redirects to three potential phases.
        This method is overridden to return those specific three cases.
        :param get:
        :return:
        """
        application_id = get_id(self.request)

        if not get:
            return build_url(self.get_choice_url(application_id), get={'id': application_id})
        else:
            return build_url(self.get_choice_url(application_id), get=get)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_list = self.get_form_list()
        if all(form.is_valid() for form in form_list):
            return self.form_valid(form_list)
        else:
            return self.form_invalid(form_list)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form_list=form))

    def get_form_list(self):
        raise ImproperlyConfigured(
            "No form_list to get, please implement get_form_list")

    def get_initial(self):
        raise ImproperlyConfigured(
            "No initial data to get, please implement get_initial")

    def get_choice_url(self, app_id):
        raise ImproperlyConfigured(
            "No URL to redirect to, please implement get_choice_url")