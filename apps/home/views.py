from urllib.parse import urlencode

from django.urls import reverse
from django.views.generic import CreateView, TemplateView

from apps.landing.forms import ContactForm
from apps.landing.models import Lead
from apps.landing.views import LeadSubmitMixin

from . import content, seo


class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(content.get_home_context())
        ctx['json_ld'] = seo.home_json_ld(self.request)
        return ctx


class ContactView(LeadSubmitMixin, CreateView):
    """Página de contacto a la que llevan los botones de productos y soporte.

    Guarda un Lead igual que la landing (mismo honeypot, throttle y webhook a
    n8n), pero con su propio formulario y source='contacto'.
    """

    form_class = ContactForm
    template_name = 'home/contact.html'
    lead_source = Lead.Source.CONTACT
    success_message = content.CONTACT_FORM['success_message']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # ?producto=<slug> llega desde el botón pulsado en la home y decide el
        # <h1> y el producto del lead. Sin él, o con uno que no existe, es una
        # petición de información.
        self.contact_request = content.get_contact_request(request.GET.get('producto', ''))

    def get_initial(self):
        initial = super().get_initial()
        initial['product'] = self.contact_request['slug']
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(content.get_contact_context())
        ctx['contact_request'] = self.contact_request
        ctx['json_ld'] = seo.contact_json_ld(self.request)
        return ctx

    def get_success_url(self):
        # Se conserva ?producto= para que, sin JS, la página de vuelta muestre
        # el mismo <h1> junto al mensaje de éxito.
        url = reverse('home:contact') + '?' + urlencode({'producto': self.contact_request['slug']})
        return url + '#contacto'
