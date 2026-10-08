from apps.common.seo import absolute_static

from . import content


def brand(request):
    """Datos de marca para base.html, que también pinta páginas sin contexto
    propio de contenido (como el login)."""
    return {
        'brand': content.BRAND,
        'social_image_url': absolute_static(request, content.BRAND['social_image']),
    }
