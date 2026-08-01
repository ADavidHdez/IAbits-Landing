from .base import *
import dj_database_url

DEBUG = False

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
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
