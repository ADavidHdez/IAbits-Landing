"""Rutas del proyecto.

- `settings.ADMIN_URL`  → panel de administración (ruta secreta en producción).
- `/accounts/login/`    → acceso de staff (sin registro público).
- `/`                   → página de inicio.
- `/landing/`           → la landing y el POST del formulario de leads.
- `/robots.txt`, `/sitemap.xml`, `/favicon.ico` → para buscadores y navegadores.
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.common.sitemaps import SITEMAPS
from apps.common.views import favicon, robots_txt

urlpatterns = [
    path('robots.txt', robots_txt, name='robots'),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('favicon.ico', favicon, name='favicon'),
    path(settings.ADMIN_URL, admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('landing/', include('apps.landing.urls', namespace='landing')),
    path('', include('apps.home.urls', namespace='home')),
]
