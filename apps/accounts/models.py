from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.username


class LoginAttempt(models.Model):
    """Intento de login fallido, para limitar la fuerza bruta.

    Se guarda en BD —y no en caché de proceso— por el mismo motivo que el
    throttle de leads: gunicorn corre con varios workers y cada uno tendría su
    propio contador en memoria. Las filas se borran al acertar la contraseña y
    las caducadas se purgan en cada comprobación.
    """

    ip_address = models.GenericIPAddressField('IP de origen', null=True, blank=True)
    username = models.CharField('usuario probado', max_length=150, blank=True)
    created_at = models.DateTimeField('fecha', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'intento de login'
        verbose_name_plural = 'intentos de login'
        indexes = [models.Index(fields=['ip_address', 'created_at'])]

    def __str__(self):
        return f'{self.username or "?"} desde {self.ip_address or "?"}'
