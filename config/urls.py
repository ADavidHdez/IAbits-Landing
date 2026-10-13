"""Rutas del proyecto.

- `settings.ADMIN_URL`  → panel de administración (ruta secreta en producción).
- `/accounts/login/`    → acceso de staff (sin registro público).
- `/`                   → página de inicio.
- `/landing/`           → la landing y el POST del formulario de leads.
- `/chat/`              → POST del chat flotante (lo comparten la landing y la home).
- `/aviso-legal/`, `/privacidad/`, `/cookies/` → textos legales comunes a las dos webs.
- `/interno/purgar-datos/` → POST de n8n (con token) que borra los datos caducados.
- `/robots.txt`, `/sitemap.xml`, `/favicon.ico` → para buscadores y navegadores.
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.common.sitemaps import SITEMAPS
from apps.common.views import favicon, robots_txt
from apps.landing.views import ChatView, RetentionPurgeView

urlpatterns = [
    path('robots.txt', robots_txt, name='robots'),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('favicon.ico', favicon, name='favicon'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('interno/purgar-datos/', RetentionPurgeView.as_view(), name='retention_purge'),
    path(settings.ADMIN_URL, admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('landing/', include('apps.landing.urls', namespace='landing')),
    path('', include('apps.legal.urls', namespace='legal')),
    path('', include('apps.home.urls', namespace='home')),
]
