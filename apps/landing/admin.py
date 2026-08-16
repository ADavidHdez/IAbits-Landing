from django.contrib import admin, messages

from . import content, webhooks
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'service_label', 'created_at', 'sent_to_n8n']
    search_fields = ['name', 'email', 'company']
    list_filter = ['service_interest', 'created_at']
    readonly_fields = ['id', 'ip_address', 'user_agent', 'created_at', 'webhook_delivered_at']
    date_hierarchy = 'created_at'
    actions = ['resend_to_n8n']

    @admin.display(description='servicio de interés')
    def service_label(self, obj):
        return dict(content.service_choices()).get(obj.service_interest, obj.service_interest)

    @admin.display(description='enviado a n8n', boolean=True)
    def sent_to_n8n(self, obj):
        return obj.webhook_delivered_at is not None

    @admin.action(description='Reenviar a n8n')
    def resend_to_n8n(self, request, queryset):
        if not webhooks.is_enabled():
            self.message_user(
                request, 'El webhook de n8n no está configurado.', messages.ERROR
            )
            return
        sent = sum(webhooks.send_lead(lead) for lead in queryset)
        failed = queryset.count() - sent
        self.message_user(
            request,
            f'{sent} lead(s) enviados a n8n, {failed} con error.',
            messages.WARNING if failed else messages.SUCCESS,
        )
