import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView

from apps.common.http import get_client_ip

from . import chat, content, webhooks
from .forms import LeadForm
from .models import ChatConversation, ChatMessage, Lead

logger = logging.getLogger('apps.landing')

THROTTLE_MESSAGE = 'Has enviado demasiadas solicitudes. Inténtalo de nuevo más tarde.'


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
        ctx['chat_enabled'] = chat.is_enabled()
        ctx['chat_max_length'] = chat.MESSAGE_MAX_LENGTH
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


class ChatView(View):
    """Recibe un mensaje del chat flotante y devuelve la respuesta del agente.

    Solo JSON: el widget (static/js/chat.js) no se muestra sin JavaScript, así
    que no hay camino clásico que mantener. El mensaje del visitante se guarda
    antes de llamar a n8n para que quede en el admin aunque n8n falle.
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not chat.is_enabled():
            raise Http404

        text = (request.POST.get('message') or '').strip()
        if not text or len(text) > chat.MESSAGE_MAX_LENGTH:
            return self.error(content.CHAT['invalid_message'], status=400)

        # Throttle por IP respaldado en BD: cada mensaje es una llamada de pago al modelo.
        ip = get_client_ip(request)
        window_start = timezone.now() - timedelta(minutes=settings.CHAT_THROTTLE_WINDOW_MINUTES)
        if ip and (
            ChatMessage.objects.filter(
                role=ChatMessage.Role.USER, ip_address=ip, created_at__gte=window_start
            ).count()
            >= settings.CHAT_THROTTLE_MAX
        ):
            logger.warning('Mensaje de chat rechazado por throttle (ip=%s)', ip)
            return self.error(content.CHAT['throttle_message'], status=429)

        conversation = self.get_conversation(request.POST.get('conversation_id'), ip)
        user_message = ChatMessage.objects.create(
            conversation=conversation, role=ChatMessage.Role.USER, text=text, ip_address=ip
        )

        try:
            reply = chat.ask_agent(user_message)
        except chat.ChatUnavailable:
            return self.error(content.CHAT['error_message'], status=503, conversation=conversation)

        ChatMessage.objects.create(
            conversation=conversation, role=ChatMessage.Role.ASSISTANT, text=reply
        )
        # auto_now solo se actualiza al guardar: marca la hora del último mensaje.
        conversation.save(update_fields=['updated_at'])
        return JsonResponse({'ok': True, 'reply': reply, 'conversation_id': str(conversation.id)})

    def get_conversation(self, conversation_id, ip):
        """Continúa la conversación indicada o, si no existe, empieza una nueva.

        Un id inválido o caducado no es un error: el visitante simplemente
        arranca de cero, igual que al abrir la web en otra pestaña.
        """
        try:
            existing = ChatConversation.objects.filter(pk=uuid.UUID(conversation_id or '')).first()
        except ValueError:
            existing = None
        if existing:
            return existing
        return ChatConversation.objects.create(
            ip_address=ip, user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:255]
        )

    def error(self, message, status, conversation=None):
        data = {'ok': False, 'error': message}
        if conversation:
            data['conversation_id'] = str(conversation.id)
        return JsonResponse(data, status=status)
