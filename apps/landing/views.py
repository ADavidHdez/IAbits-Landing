import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView

from . import content, webhooks
from .forms import LeadForm
from .models import Lead

logger = logging.getLogger('apps.landing')

THROTTLE_MESSAGE = 'Has enviado demasiadas solicitudes. Inténtalo de nuevo más tarde.'


def get_client_ip(request):
    """Primera IP de X-Forwarded-For (la añade el proxy de Easypanel) o REMOTE_ADDR.

    Solo es fiable porque el puerto del contenedor no es alcanzable desde
    internet: la única vía de entrada es el proxy.
    """
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class LandingView(CreateView):
    model = Lead
    form_class = LeadForm
    template_name = 'landing/home.html'

    def post(self, request, *args, **kwargs):
        self.object = None

        # Honeypot: fingir éxito para no revelar al bot cuál es el campo trampa.
        if request.POST.get('website'):
            logger.info('Lead descartado por honeypot (ip=%s)', get_client_ip(request))
            return self.fake_success()

        # Throttle por IP respaldado en BD (funciona con varios workers de gunicorn).
        ip = get_client_ip(request)
        window_start = timezone.now() - timedelta(minutes=settings.LEAD_THROTTLE_WINDOW_MINUTES)
        if ip and (
            Lead.objects.filter(ip_address=ip, created_at__gte=window_start).count()
            >= settings.LEAD_THROTTLE_MAX
        ):
            logger.warning('Lead rechazado por throttle (ip=%s)', ip)
            return self.throttled_response()

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(content.get_landing_context())
        return ctx

    def form_valid(self, form):
        form.instance.ip_address = get_client_ip(self.request)
        form.instance.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:255]
        response = super().form_valid(form)
        # on_commit: el hilo del webhook marca el lead como entregado desde otra
        # conexión, así que la fila tiene que estar ya confirmada en la BD.
        transaction.on_commit(lambda: webhooks.send_lead_async(self.object))
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

    def fake_success(self):
        if self.is_ajax:
            return JsonResponse({
                'ok': True,
                'message': content.FORM_SECTION['success_message'],
            })
        messages.success(self.request, content.FORM_SECTION['success_message'])
        return redirect(self.get_success_url())

    def throttled_response(self):
        if self.is_ajax:
            return JsonResponse(
                {'ok': False, 'errors': {'__all__': [{'message': THROTTLE_MESSAGE, 'code': 'throttled'}]}},
                status=429,
            )
        messages.error(self.request, THROTTLE_MESSAGE)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('landing:home') + '#contacto'

    @property
    def is_ajax(self) -> bool:
        """El formulario se envía por fetch() desde static/js/lead-form.js.

        Sin JS el navegador hace un POST normal y se mantiene el flujo
        Post/Redirect/Get con mensajes de Django.
        """
        return self.request.headers.get('x-requested-with') == 'XMLHttpRequest'
