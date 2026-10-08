from pathlib import Path

from decouple import config
from django.utils.csp import CSP

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Sin django.contrib.sites: el sitemap toma el dominio de la petición.
    'django.contrib.sitemaps',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.landing',
    'apps.home',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csp.ContentSecurityPolicyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Ruta del panel de administración, configurable por entorno. En producción
# usar un valor no adivinable terminado en '/', p. ej. ADMIN_URL=gestion-x7k2/
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Content Security Policy (middleware nativo de Django 6). Vive en base para
# que cualquier recurso que la viole se detecte ya en desarrollo.
# El único contenido inline permitido es el <style> del tema, vía nonce.
SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [CSP.SELF],
    'style-src': [CSP.SELF, CSP.NONCE],
    'img-src': [CSP.SELF, 'data:'],
    'font-src': [CSP.SELF],
    'connect-src': [CSP.SELF],
    'form-action': [CSP.SELF],
    'frame-ancestors': [CSP.NONE],
    'base-uri': [CSP.SELF],
    'object-src': [CSP.NONE],
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.csp',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.common.context_processors.canonical',
                'apps.landing.context_processors.brand',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # Solo existen cuentas de staff/admin: exigir contraseñas largas.
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Cookies y cabeceras ---------------------------------------------------
# En producción se les añade el flag Secure (ver production.py).
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_REFERRER_POLICY = 'same-origin'

# --- Límites de uso --------------------------------------------------------
# Proxies propios delante de gunicorn (Easypanel pone 1). Se usa para leer la
# IP real del visitante sin fiarse de las cabeceras que envía el cliente;
# ver apps/common.py.
TRUSTED_PROXY_DEPTH = config('TRUSTED_PROXY_DEPTH', default=1, cast=int)

# Envíos del formulario de leads por IP dentro de la ventana.
LEAD_THROTTLE_MAX = config('LEAD_THROTTLE_MAX', default=5, cast=int)
LEAD_THROTTLE_WINDOW_MINUTES = config('LEAD_THROTTLE_WINDOW_MINUTES', default=60, cast=int)

# Intentos de login fallidos por IP antes de bloquear la ventana.
LOGIN_THROTTLE_MAX = config('LOGIN_THROTTLE_MAX', default=5, cast=int)
LOGIN_THROTTLE_WINDOW_MINUTES = config('LOGIN_THROTTLE_WINDOW_MINUTES', default=15, cast=int)

# Webhook de n8n que recibe cada lead. Vacío = desactivado (el lead solo se
# guarda en la BD). El token viaja en la cabecera X-Webhook-Token para que n8n
# pueda rechazar peticiones que no vengan de esta web.
N8N_WEBHOOK_URL = config('N8N_WEBHOOK_URL', default='')
N8N_WEBHOOK_TOKEN = config('N8N_WEBHOOK_TOKEN', default='')
N8N_WEBHOOK_TIMEOUT = config('N8N_WEBHOOK_TIMEOUT', default=10, cast=int)
N8N_WEBHOOK_SOURCE = config('N8N_WEBHOOK_SOURCE', default='landing')

# Chat de la landing: cada mensaje se reenvía a un agente de IA en n8n y se
# espera su respuesta. Vacío = el chat no se muestra. Usa el mismo
# N8N_WEBHOOK_TOKEN. El timeout es mayor que el de leads porque el modelo tarda
# unos segundos en escribir, y menor que el de gunicorn (60 s).
N8N_CHAT_WEBHOOK_URL = config('N8N_CHAT_WEBHOOK_URL', default='')
N8N_CHAT_TIMEOUT = config('N8N_CHAT_TIMEOUT', default=25, cast=int)

# Mensajes del chat por IP dentro de la ventana: cada uno es una llamada de
# pago al modelo de IA.
CHAT_THROTTLE_MAX = config('CHAT_THROTTLE_MAX', default=20, cast=int)
CHAT_THROTTLE_WINDOW_MINUTES = config('CHAT_THROTTLE_WINDOW_MINUTES', default=60, cast=int)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
