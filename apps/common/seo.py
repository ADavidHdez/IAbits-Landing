"""Utilidades de SEO compartidas por la home y la landing.

Las URLs absolutas se construyen siempre desde la petición: el dominio de
producción no está escrito en ningún sitio del código.
"""
import json
import re

from django.templatetags.static import static
from django.utils.safestring import mark_safe

# Sin escapar, un texto con "</script>" cerraría el bloque JSON-LD y lo que
# siguiera se interpretaría como HTML. Las secuencias \u00XX siguen siendo JSON
# válido y el parser las devuelve como el carácter original.
_JSON_LD_ESCAPES = {ord('<'): '\\u003c', ord('>'): '\\u003e', ord('&'): '\\u0026'}

# Un precio "limpio": '290 €', '1.500 €' o '1.500,50 €'. Lo que lleve texto
# alrededor ('desde 1.500 €') no es un precio exacto y no se publica como tal.
_PRICE_RE = re.compile(r'^\s*(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{1,2}))?\s*€\s*$')


def canonical_url(request) -> str:
    """URL absoluta de la página sin querystring (?utm_…, ?page=…)."""
    return request.build_absolute_uri(request.path)


def absolute_static(request, path) -> str:
    return request.build_absolute_uri(static(path))


def json_ld(data) -> str:
    """Serializa `data` para un <script type="application/ld+json">.

    `json_script` de Django no sirve aquí porque fuerza type="application/json".
    """
    return mark_safe(json.dumps(data, ensure_ascii=False).translate(_JSON_LD_ESCAPES))


def price_amount(text) -> str | None:
    """'290 €' → '290', '1.500,50 €' → '1500.50'; None si no es un precio exacto."""
    match = _PRICE_RE.match(text or '')
    if not match:
        return None
    integer, decimals = match.groups()
    amount = integer.replace('.', '')
    return f'{amount}.{decimals}' if decimals else amount
