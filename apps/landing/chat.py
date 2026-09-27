"""Conversación del chat de la landing con el agente de IA de n8n.

A diferencia del webhook de leads, aquí el visitante espera la respuesta, así
que la llamada es síncrona y con timeout. La memoria de la conversación vive en
la BD de Django: cada petición lleva los últimos mensajes y el workflow de n8n
no guarda nada entre llamadas (su memoria en RAM se perdería en cada reinicio).

Se usa urllib de la stdlib para no añadir dependencias al proyecto.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.utils import timezone

from . import webhooks

logger = logging.getLogger('apps.landing')

# Largo máximo del mensaje del visitante. Si cambia, actualiza también
# content.CHAT['invalid_message'].
MESSAGE_MAX_LENGTH = 500
# Mensajes previos que se envían a n8n como contexto de la conversación.
HISTORY_LENGTH = 10
# Tope de la respuesta que se guarda y se muestra, por si el agente se desboca.
REPLY_MAX_LENGTH = 4000


class ChatUnavailable(Exception):
    """n8n no ha devuelto una respuesta utilizable."""


def is_enabled() -> bool:
    """True si hay un webhook de chat configurado y su URL es aceptable."""
    return webhooks.is_valid_webhook_url(
        getattr(settings, 'N8N_CHAT_WEBHOOK_URL', ''), 'N8N_CHAT_WEBHOOK_URL'
    )


def build_payload(user_message) -> dict:
    """Cuerpo JSON que recibe n8n. Los nombres son estables: si cambian, hay
    que actualizar también n8n/chat-agent.workflow.json."""
    conversation = user_message.conversation
    previous = (
        conversation.messages.exclude(pk=user_message.pk)
        .order_by('-created_at', '-id')[:HISTORY_LENGTH]
    )
    return {
        'event': 'chat.message',
        'source': settings.N8N_WEBHOOK_SOURCE,
        'sent_at': timezone.now().isoformat(),
        'conversation_id': str(conversation.id),
        'message': user_message.text,
        'history': [{'role': m.role, 'text': m.text} for m in reversed(previous)],
    }


def ask_agent(user_message) -> str:
    """Envía el mensaje a n8n y devuelve la respuesta del agente.

    Lanza ChatUnavailable si n8n falla, tarda demasiado o responde algo sin
    el campo `reply`. El llamador decide qué ve el visitante.
    """
    body = json.dumps(build_payload(user_message)).encode('utf-8')
    request = urllib.request.Request(settings.N8N_CHAT_WEBHOOK_URL, data=body, method='POST')
    request.add_header('Content-Type', 'application/json')
    if settings.N8N_WEBHOOK_TOKEN:
        request.add_header('X-Webhook-Token', settings.N8N_WEBHOOK_TOKEN)

    conversation_id = user_message.conversation_id
    try:
        with urllib.request.urlopen(request, timeout=settings.N8N_CHAT_TIMEOUT) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        logger.error('n8n devolvió %s en la conversación %s', exc.code, conversation_id)
        raise ChatUnavailable from exc
    except (urllib.error.URLError, OSError) as exc:
        logger.error('No se pudo contactar con n8n (conversación %s): %s', conversation_id, exc)
        raise ChatUnavailable from exc
    except ValueError as exc:
        logger.error('n8n devolvió algo que no es JSON (conversación %s)', conversation_id)
        raise ChatUnavailable from exc

    reply = data.get('reply') if isinstance(data, dict) else None
    if not isinstance(reply, str) or not reply.strip():
        logger.error('Respuesta de n8n sin "reply" (conversación %s)', conversation_id)
        raise ChatUnavailable
    return reply.strip()[:REPLY_MAX_LENGTH]
