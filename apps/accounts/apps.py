import logging

from django.apps import AppConfig
from django.contrib.auth.signals import user_login_failed

logger = logging.getLogger('apps.accounts')


def log_login_failure(sender, credentials, request, **kwargs):
    logger.warning('Login fallido para usuario=%r', credentials.get('username'))


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Cuentas'

    def ready(self):
        user_login_failed.connect(log_login_failure)
