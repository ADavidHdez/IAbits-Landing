from .base import *
import dj_database_url
from decouple import config

DEBUG = False

DATABASES = {
    # SSL de BD desactivado a propósito: Postgres vive en la misma red privada
    # de Docker de Easypanel y nunca se expone a internet.
    'default': dj_database_url.config(conn_max_age=600, conn_health_checks=True)
}

# Dominios (con esquema) desde los que Django acepta POSTs con CSRF.
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://proyecto-web-landing-page.qk5lk3.easypanel.host',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()],
)

# Todo a stdout/stderr: Easypanel captura la consola del contenedor.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{asctime} {levelname} {name} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
        'django.security': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'apps': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

# El storage con manifest requiere collectstatic; solo tiene sentido en producción.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# El proxy de Easypanel termina el HTTPS y habla con gunicorn por HTTP interno;
# esta cabecera le dice a Django cuándo la petición original sí era HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
