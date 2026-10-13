from django.views.generic import TemplateView

from apps.home.content import FOOTER
from apps.landing.content import THEME

from . import content


class LegalPageView(TemplateView):
    """Una página legal (aviso legal, privacidad o cookies).

    Las tres comparten plantilla: cambia solo el documento de content.py que
    se indica en `page` al registrar la ruta.
    """

    template_name = 'legal/page.html'
    page = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'page': self.page,
            'site': self.page['site'],
            'theme': THEME,
            'footer': FOOTER,
            'updated': content.UPDATED,
            'updated_label': content.UPDATED_LABEL,
        })
        return ctx
