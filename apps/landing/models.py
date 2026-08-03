import uuid

from django.db import models


class Lead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('nombre', max_length=120)
    email = models.EmailField('email')
    company = models.CharField('empresa', max_length=120, blank=True)
    service_interest = models.CharField('servicio de interés', max_length=60, blank=True)
    message = models.TextField('mensaje', blank=True)
    ip_address = models.GenericIPAddressField('IP de origen', null=True, blank=True)
    user_agent = models.CharField('user agent', max_length=255, blank=True)
    created_at = models.DateTimeField('fecha de creación', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'lead'
        verbose_name_plural = 'leads'

    def __str__(self):
        return f'{self.name} <{self.email}>'
