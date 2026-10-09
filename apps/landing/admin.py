from django.contrib import admin, messages
from django.db.models import Count, OuterRef, Subquery
from django.utils.text import Truncator

from apps.home import content as home_content

from . import content, webhooks
from .models import ChatConversation, ChatMessage, Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'company', 'source', 'interest_label', 'created_at', 'sent_to_n8n',
    ]
    search_fields = ['name', 'email', 'company', 'phone']
    list_filter = ['source', 'service_interest', 'product', 'created_at']
    readonly_fields = [
        'id', 'source', 'ip_address', 'user_agent', 'created_at', 'webhook_delivered_at',
    ]
    date_hierarchy = 'created_at'
    actions = ['resend_to_n8n']

    @admin.display(description='interés')
    def interest_label(self, obj):
        """Servicio (landing) o producto (contacto), según de dónde venga el lead."""
        if obj.product:
            return dict(home_content.product_choices()).get(obj.product, obj.product)
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


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    fields = ['created_at', 'role', 'text']
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    """Conversaciones del chat, solo lectura: se consultan o se borran."""

    list_display = ['created_at', 'first_message', 'message_count', 'ip_address', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['messages__text', 'ip_address']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'ip_address', 'user_agent', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]

    def get_queryset(self, request):
        first_user_text = (
            ChatMessage.objects.filter(conversation=OuterRef('pk'), role=ChatMessage.Role.USER)
            .order_by('created_at', 'id')
            .values('text')[:1]
        )
        return super().get_queryset(request).annotate(
            num_messages=Count('messages'), first_text=Subquery(first_user_text)
        )

    @admin.display(description='primer mensaje')
    def first_message(self, obj):
        return Truncator(obj.first_text or '').chars(80)

    @admin.display(description='mensajes', ordering='num_messages')
    def message_count(self, obj):
        return obj.num_messages

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
