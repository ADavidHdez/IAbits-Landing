from django.contrib import messages
from django.http import JsonResponse
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
        if self.is_ajax:
            return JsonResponse({
                'ok': True,
                'message': content.FORM_SECTION['success_message'],
            })
        messages.success(self.request, content.FORM_SECTION['success_message'])
        return response

    def form_invalid(self, form):
        if self.is_ajax:
            return JsonResponse(
                {'ok': False, 'errors': form.errors.get_json_data()},
                status=400,
            )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('landing:home') + '#contacto'

    @property
    def is_ajax(self) -> bool:
        """El formulario se envía por fetch() desde static/js/lead-form.js.

        Sin JS el navegador hace un POST normal y se mantiene el flujo
        Post/Redirect/Get con mensajes de Django.
        """
        return self.request.headers.get('x-requested-with') == 'XMLHttpRequest'
