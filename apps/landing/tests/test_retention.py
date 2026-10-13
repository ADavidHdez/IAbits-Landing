from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.landing.models import ChatConversation, ChatMessage, Lead
from apps.landing.retention import purge_expired

TOKEN = 'token-de-prueba'


def make_lead(days_ago):
    lead = Lead.objects.create(name='Ana Pérez', email='ana@empresa.com')
    # auto_now_add no deja fijar la fecha al crear: se retrasa con update().
    Lead.objects.filter(pk=lead.pk).update(created_at=timezone.now() - timedelta(days=days_ago))
    return lead


def make_conversation(days_since_last_message):
    conversation = ChatConversation.objects.create()
    ChatMessage.objects.create(conversation=conversation, role=ChatMessage.Role.USER, text='Hola')
    ChatConversation.objects.filter(pk=conversation.pk).update(
        updated_at=timezone.now() - timedelta(days=days_since_last_message)
    )
    return conversation


@override_settings(LEAD_RETENTION_DAYS=90, CHAT_RETENTION_DAYS=180)
class PurgeExpiredTests(TestCase):
    def test_deletes_only_leads_past_their_period(self):
        old = make_lead(days_ago=91)
        recent = make_lead(days_ago=89)
        result = purge_expired()
        self.assertEqual(result['leads'], 1)
        self.assertFalse(Lead.objects.filter(pk=old.pk).exists())
        self.assertTrue(Lead.objects.filter(pk=recent.pk).exists())

    def test_deletes_old_conversations_with_their_messages(self):
        old = make_conversation(days_since_last_message=181)
        recent = make_conversation(days_since_last_message=179)
        result = purge_expired()
        self.assertEqual(result['chat_conversations'], 1)
        self.assertFalse(ChatConversation.objects.filter(pk=old.pk).exists())
        self.assertFalse(ChatMessage.objects.filter(conversation_id=old.pk).exists())
        self.assertTrue(ChatConversation.objects.filter(pk=recent.pk).exists())

    def test_management_command(self):
        make_lead(days_ago=100)
        out = StringIO()
        call_command('purgar_datos', stdout=out)
        self.assertIn('Borrados 1 leads', out.getvalue())
        self.assertEqual(Lead.objects.count(), 0)


@override_settings(N8N_WEBHOOK_TOKEN=TOKEN, LEAD_RETENTION_DAYS=90, CHAT_RETENTION_DAYS=180)
class RetentionPurgeViewTests(TestCase):
    url = reverse('retention_purge')

    def test_valid_token_purges_and_returns_counts(self):
        make_lead(days_ago=120)
        make_conversation(days_since_last_message=200)
        response = self.client.post(self.url, headers={'x-webhook-token': TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True, 'leads': 1, 'chat_conversations': 1})

    def test_wrong_or_missing_token_is_rejected_and_deletes_nothing(self):
        make_lead(days_ago=120)
        for headers in ({'x-webhook-token': 'otro'}, {}):
            response = self.client.post(self.url, headers=headers)
            self.assertEqual(response.status_code, 401)
        self.assertEqual(Lead.objects.count(), 1)

    def test_get_is_not_allowed(self):
        response = self.client.get(self.url, headers={'x-webhook-token': TOKEN})
        self.assertEqual(response.status_code, 405)

    @override_settings(N8N_WEBHOOK_TOKEN='')
    def test_without_configured_token_the_endpoint_does_not_exist(self):
        """Sin token, cualquiera con un token vacío podría lanzar la purga."""
        make_lead(days_ago=120)
        response = self.client.post(self.url, headers={'x-webhook-token': ''})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Lead.objects.count(), 1)
