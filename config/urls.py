"""Rutas del proyecto.

- `settings.ADMIN_URL`  → panel de administración (ruta secreta en producción).
- `/accounts/login/`    → acceso de staff (sin registro público).
- `/`                   → página de inicio.
- `/landing/`           → la landing y el POST del formulario de leads.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('landing/', include('apps.landing.urls', namespace='landing')),
    path('', include('apps.home.urls', namespace='home')),
]
