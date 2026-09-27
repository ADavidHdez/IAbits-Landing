"""Lectura fiable de datos de la petición HTTP.

`apps.common` no es una app de Django (no está en INSTALLED_APPS ni tiene
modelos): es el sitio donde vive el código que usan al menos dos apps.
"""
import ipaddress

from django.conf import settings


def _clean_ip(value: str) -> str | None:
    """Devuelve la IP si `value` es una dirección válida; si no, None.

    Se valida siempre porque el valor puede venir de una cabecera enviada por
    el cliente: sin validar acabaría en la BD (o en un filtro) texto arbitrario.
    """
    candidate = (value or '').strip()
    if not candidate:
        return None
    # Algunos proxies anotan "ip:puerto" para IPv4 y "[ipv6]:puerto".
    if candidate.startswith('['):
        candidate = candidate[1:].split(']', 1)[0]
    elif candidate.count(':') == 1:
        candidate = candidate.split(':', 1)[0]
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def get_client_ip(request) -> str | None:
    """IP real del visitante, a prueba de cabeceras falsificadas.

    X-Forwarded-For es una lista que crece por la derecha: cada proxy añade al
    final la IP de quien le habló. Por eso **la última entrada es la única que
    no controla el cliente** — si alguien envía `X-Forwarded-For: 1.2.3.4`, el
    proxy de Easypanel lo deja como `1.2.3.4, <ip real>` y quedarse con el
    primer valor permitiría rotar de IP a voluntad y saltarse el throttle.

    `TRUSTED_PROXY_DEPTH` es el número de proxies propios que hay delante de
    gunicorn (1 con Easypanel). Se descartan tantas entradas por la derecha
    como proxies haya menos uno.
    """
    depth = max(getattr(settings, 'TRUSTED_PROXY_DEPTH', 1), 1)
    chain = [
        part for part in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',') if part.strip()
    ]
    if chain:
        index = -depth if len(chain) >= depth else 0
        ip = _clean_ip(chain[index])
        if ip:
            return ip
    return _clean_ip(request.META.get('REMOTE_ADDR', ''))
