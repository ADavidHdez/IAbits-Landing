import logging

from django.apps import AppConfig
from django.contrib.auth.signals import user_login_failed

logger = logging.getLogger('apps.accounts')


def registrar_login_fallido(sender, credentials, request, **kwargs):
    """Deja rastro del fallo y suma un intento al throttle de esa IP.

    Va en una señal —y no solo en la vista— para cubrir también los intentos
    contra el admin de Django, cuyo formulario de login no controlamos.
    """
    from apps.common.http import get_client_ip

    from .models import LoginAttempt

    username = (credentials or {}).get('username') or ''
    ip = get_client_ip(request) if request is not None else None
    logger.warning('Login fallido para usuario=%r (ip=%s)', username, ip)
    LoginAttempt.objects.create(ip_address=ip, username=username[:150])


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Cuentas'

    def ready(self):
        user_login_failed.connect(registrar_login_fallido)
