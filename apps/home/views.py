from django.views.generic import TemplateView

from . import content, seo


class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(content.get_home_context())
        ctx['json_ld'] = seo.home_json_ld(self.request)
        return ctx
