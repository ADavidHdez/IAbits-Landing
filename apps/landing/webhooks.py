"""Notificación de leads a n8n mediante webhook HTTP.

El lead se guarda siempre en la base de datos: n8n solo recibe una copia. Si el
webhook falla, el lead no se pierde — queda en el admin con la columna "enviado
a n8n" en rojo y puede reenviarse desde allí con la acción correspondiente.

Se usa urllib de la stdlib para no añadir dependencias al proyecto.
"""
import json
import logging
import threading
import urllib.error
import urllib.request
from urllib.parse import urlparse

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger('apps.landing')

ALLOWED_SCHEMES = ('http', 'https')


def is_enabled() -> bool:
    url = getattr(settings, 'N8N_WEBHOOK_URL', '')
    return bool(url) and urlparse(url).scheme in ALLOWED_SCHEMES


def build_payload(lead) -> dict:
    """Cuerpo JSON que recibe n8n. Los nombres son estables: si cambian, hay
    que actualizar también el workflow de n8n que los consume."""
    from . import content

    services = dict(content.service_choices())
    return {
        'event': 'lead.created',
        'source': settings.N8N_WEBHOOK_SOURCE,
        'sent_at': timezone.now().isoformat(),
        'lead': {
            'id': str(lead.id),
            'name': lead.name,
            'email': lead.email,
            'company': lead.company,
            'service_interest': lead.service_interest,
            'service_label': services.get(lead.service_interest, ''),
            'message': lead.message,
            'ip_address': lead.ip_address,
            'user_agent': lead.user_agent,
            'created_at': lead.created_at.isoformat() if lead.created_at else None,
        },
    }


def send_lead(lead) -> bool:
    """POST síncrono a n8n. Devuelve True si n8n respondió 2xx.

    Marca el lead como entregado en la BD; nunca propaga excepciones para que un
    n8n caído no rompa el envío del formulario.
    """
    if not is_enabled():
        logger.debug('Webhook n8n no configurado; lead %s solo se guarda en BD', lead.pk)
        return False

    body = json.dumps(build_payload(lead)).encode('utf-8')
    request = urllib.request.Request(settings.N8N_WEBHOOK_URL, data=body, method='POST')
    request.add_header('Content-Type', 'application/json')
    if settings.N8N_WEBHOOK_TOKEN:
        request.add_header('X-Webhook-Token', settings.N8N_WEBHOOK_TOKEN)

    try:
        with urllib.request.urlopen(request, timeout=settings.N8N_WEBHOOK_TIMEOUT) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        logger.error('n8n devolvió %s para el lead %s', exc.code, lead.pk)
        return False
    except (urllib.error.URLError, OSError) as exc:
        logger.error('No se pudo contactar con n8n para el lead %s: %s', lead.pk, exc)
        return False

    from .models import Lead

    Lead.objects.filter(pk=lead.pk).update(webhook_delivered_at=timezone.now())
    logger.info('Lead %s enviado a n8n (HTTP %s)', lead.pk, status)
    return True


def send_lead_async(lead) -> None:
    """Envía en un hilo aparte: el visitante no espera a que n8n responda."""
    if not is_enabled():
        return

    def worker():
        try:
            send_lead(lead)
        finally:
            # El hilo abre su propia conexión a la BD; hay que devolverla.
            close_old_connections()

    threading.Thread(target=worker, name=f'n8n-lead-{lead.pk}', daemon=True).start()
