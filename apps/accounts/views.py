"""Acceso de staff. No hay registro público: las cuentas se crean desde el admin."""
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.views import LoginView
from django.utils import timezone

from apps.common.http import get_client_ip

from .models import LoginAttempt

logger = logging.getLogger('apps.accounts')

THROTTLE_MESSAGE = (
    'Demasiados intentos fallidos desde tu conexión. '
    'Espera unos minutos antes de volver a probar.'
)


def is_throttled(ip: str | None) -> bool:
    """True si esa IP ha agotado los intentos permitidos en la ventana actual."""
    if not ip:
        return False
    window_start = timezone.now() - timedelta(minutes=settings.LOGIN_THROTTLE_WINDOW_MINUTES)
    # Purga oportunista: evita que la tabla crezca sin límite sin necesidad de cron.
    LoginAttempt.objects.filter(created_at__lt=window_start).delete()
    recientes = LoginAttempt.objects.filter(
        ip_address=ip, created_at__gte=window_start
    ).count()
    return recientes >= settings.LOGIN_THROTTLE_MAX


class ThrottledLoginView(LoginView):
    """Login de staff con límite de intentos por IP.

    Los fallos los registra la señal `user_login_failed` (ver apps.py), que
    también cubre los del admin de Django; el bloqueo se aplica aquí, que es la
    única puerta de entrada pública.
    """

    template_name = 'accounts/login.html'

    def post(self, request, *args, **kwargs):
        ip = get_client_ip(request)
        if is_throttled(ip):
            logger.warning('Login bloqueado por throttle (ip=%s)', ip)
            form = self.get_form()
            form.errors['__all__'] = form.error_class([THROTTLE_MESSAGE])
            return self.render_to_response(self.get_context_data(form=form), status=429)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Contraseña correcta: se limpia el contador para no penalizar al dueño
        # de la conexión por los fallos previos.
        LoginAttempt.objects.filter(ip_address=get_client_ip(self.request)).delete()
        return super().form_valid(form)
