import uuid

from django.db import models


class Lead(models.Model):
    class Source(models.TextChoices):
        LANDING = 'landing', 'landing'
        CONTACT = 'contacto', 'página de contacto'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Con el default, los leads ya guardados y los de la landing quedan como
    # 'landing' sin tocar LandingView.
    source = models.CharField('origen', max_length=20, choices=Source.choices, default=Source.LANDING)
    name = models.CharField('nombre', max_length=120)
    email = models.EmailField('email')
    phone = models.CharField('teléfono', max_length=20, blank=True)
    company = models.CharField('empresa', max_length=120, blank=True)
    # Sin choices, igual que service_interest: las opciones salen de content.py
    # y añadir una no exige migración.
    service_interest = models.CharField('servicio de interés', max_length=60, blank=True)
    product = models.CharField('producto', max_length=60, blank=True)
    contact_preference = models.CharField('preferencia de contacto', max_length=20, blank=True)
    message = models.TextField('mensaje', blank=True)
    ip_address = models.GenericIPAddressField('IP de origen', null=True, blank=True)
    user_agent = models.CharField('user agent', max_length=255, blank=True)
    created_at = models.DateTimeField('fecha de creación', auto_now_add=True)
    webhook_delivered_at = models.DateTimeField(
        'enviado a n8n', null=True, blank=True,
        help_text='Momento en que n8n confirmó la recepción del lead.',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'lead'
        verbose_name_plural = 'leads'

    def __str__(self):
        return f'{self.name} <{self.email}>'


class ChatConversation(models.Model):
    """Una conversación del chat de la landing con el agente de IA."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField('IP de origen', null=True, blank=True)
    user_agent = models.CharField('user agent', max_length=255, blank=True)
    created_at = models.DateTimeField('inicio', auto_now_add=True)
    updated_at = models.DateTimeField('último mensaje', auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'conversación del chat'
        verbose_name_plural = 'conversaciones del chat'

    def __str__(self):
        return f'Conversación {str(self.id)[:8]}'


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'visitante'
        ASSISTANT = 'assistant', 'asistente'

    conversation = models.ForeignKey(
        ChatConversation, on_delete=models.CASCADE, related_name='messages',
        verbose_name='conversación',
    )
    role = models.CharField('autor', max_length=10, choices=Role.choices)
    text = models.TextField('texto')
    # IP de quien envió este mensaje, no la de la conversación: el throttle
    # cuenta por mensaje para que reutilizar una conversación abierta desde
    # otra IP no sirva para saltárselo.
    ip_address = models.GenericIPAddressField('IP de origen', null=True, blank=True)
    created_at = models.DateTimeField('fecha', auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']
        indexes = [models.Index(fields=['ip_address', 'created_at'])]
        verbose_name = 'mensaje del chat'
        verbose_name_plural = 'mensajes del chat'

    def __str__(self):
        return f'{self.get_role_display()}: {self.text[:60]}'
