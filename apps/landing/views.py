from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView

from . import content
from .forms import LeadForm
from .models import Lead


class LandingView(CreateView):
    model = Lead
    form_class = LeadForm
    template_name = 'landing/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(content.get_landing_context())
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, content.FORM_SECTION['success_message'])
        return response

    def get_success_url(self):
        return reverse('landing:home') + '#contacto'
