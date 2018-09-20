from application.models import AdultInHome
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView


class PITHApplyView(PITHTemplateView):
    template_name = 'PITH_templates/PITH_apply.html'
    success_url = 'Other-People-Children-Question-View'

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)
        adults = AdultInHome.objects.filter(application_id=application_id)

        adult_list = [adult for adult in adults if not adult.capita and not adult.on_update]

        return super().get_context_data(adult_list=adult_list, **kwargs)