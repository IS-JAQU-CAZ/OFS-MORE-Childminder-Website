from application.models import AdultInHome
from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView
from application.utils import build_url, get_id
from django.http import HttpResponseRedirect


class PITHPostView(PITHTemplateView):
    template_name = 'PITH_templates/PITH_post.html'
    success_url = ('PITH-Apply-View', 'Other-People-Children-Question-View')

    def post(self, request, *args, **kwargs):
        application_id = get_id(request)
        adults = AdultInHome.objects.filter(application_id=application_id)

        yes_url, no_url = self.success_url

        if any(not adult.capita and not adult.on_update for adult in adults):
            redirect_url = build_url(yes_url, get={'id': application_id})
        else:
            redirect_url = build_url(no_url, get={'id': application_id})

        return HttpResponseRedirect(redirect_url)

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)
        adults = AdultInHome.objects.filter(application_id=application_id)

        adult_list = [adult for adult in adults if adult.on_update]

        return super().get_context_data(adult_list=adult_list, **kwargs)