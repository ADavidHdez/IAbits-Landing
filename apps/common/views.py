"""Rutas técnicas para buscadores y navegadores: robots.txt y favicon.ico."""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_safe


@require_safe
def robots_txt(request):
    # ADMIN_URL es secreto en producción: nombrarlo aquí lo publicaría.
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /accounts/',
        f'Disallow: {reverse("landing:chat")}',
        '',
        f'Sitemap: {request.build_absolute_uri(reverse("sitemap"))}',
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain; charset=utf-8')


@require_safe
def favicon(request):
    # Los navegadores piden /favicon.ico aunque la página declare su icono.
    # Redirección temporal: en producción la URL estática lleva hash y cambia
    # con cada versión del archivo; una 301 cacheada acabaría en un 404.
    return redirect(static('img/favicon.ico'))
