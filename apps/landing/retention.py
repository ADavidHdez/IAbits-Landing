"""Borrado de los datos que superan su plazo de conservación.

Los plazos los promete la política de privacidad (apps/legal/content.RETENTION):
si cambian aquí, hay que cambiar también el texto. Lo ejecuta cada día el
workflow n8n/retention-purge.workflow.json a través de RetentionPurgeView, y
también se puede lanzar a mano con `python manage.py purgar_datos`.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import ChatConversation, Lead

logger = logging.getLogger('apps.landing')


def purge_expired(now=None) -> dict:
    """Borra los leads y las conversaciones del chat caducados.

    Un lead caduca LEAD_RETENTION_DAYS después de crearse: si llega a ser
    cliente, sus datos ya viven en el CRM. Una conversación caduca
    CHAT_RETENTION_DAYS después de su último mensaje, y se lleva sus mensajes.
    Devuelve cuántos se han borrado de cada uno.
    """
    now = now or timezone.now()
    lead_limit = now - timedelta(days=settings.LEAD_RETENTION_DAYS)
    chat_limit = now - timedelta(days=settings.CHAT_RETENTION_DAYS)

    # delete() cuenta también las filas borradas en cascada (los mensajes del
    # chat): se cuentan antes solo las de cada modelo.
    leads = Lead.objects.filter(created_at__lt=lead_limit)
    conversations = ChatConversation.objects.filter(updated_at__lt=chat_limit)
    result = {'leads': leads.count(), 'chat_conversations': conversations.count()}
    leads.delete()
    conversations.delete()

    logger.info(
        'Purga por plazos: %(leads)s leads y %(chat_conversations)s conversaciones borrados',
        result,
    )
    return result
