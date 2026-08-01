from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Sirve estáticos desde static/ sin collectstatic y evita el aviso de STATIC_ROOT inexistente.
WHITENOISE_AUTOREFRESH = True
