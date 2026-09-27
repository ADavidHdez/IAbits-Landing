import json
import urllib.error
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.landing import chat, content
from apps.landing.models import ChatConversation, ChatMessage

CHAT_SETTINGS = {
    'N8N_CHAT_WEBHOOK_URL': 'https://n8n.example/webhook/chat-landing',
    'N8N_WEBHOOK_TOKEN': 'token-de-prueba',
    'N8N_CHAT_TIMEOUT': 5,
    'N8N_WEBHOOK_SOURCE': 'landing',
}

URLOPEN = 'apps.landing.chat.urllib.request.urlopen'


def fake_response(body):
    """Respuesta de n8n. `body` puede ser un dict (se serializa) o bytes crudos."""
    response = MagicMock()
    response.read.return_value = body if isinstance(body, bytes) else json.dumps(body).encode()
    response.__enter__.return_value = response
    return response


@override_settings(**CHAT_SETTINGS)
class ChatViewTests(TestCase):
    def setUp(self):
        self.url = reverse('landing:chat')

    def post(self, message='¿Qué podéis automatizar?', conversation_id='', **extra):
        return self.client.post(
            self.url,
            {'message': message, 'conversation_id': conversation_id},
            headers={'x-requested-with': 'XMLHttpRequest'},
            **extra,
        )

    def test_returns_agent_reply_and_stores_both_messages(self):
        with patch(URLOPEN, return_value=fake_response({'reply': 'Casi todo lo repetitivo.'})):
            response = self.post()

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['reply'], 'Casi todo lo repetitivo.')

        conversation = ChatConversation.objects.get()
        self.assertEqual(data['conversation_id'], str(conversation.id))
        self.assertEqual(
            list(conversation.messages.values_list('role', 'text')),
            [('user', '¿Qué podéis automatizar?'), ('assistant', 'Casi todo lo repetitivo.')],
        )

    def test_sends_payload_with_token_and_history(self):
        with patch(URLOPEN, return_value=fake_response({'reply': 'Primera respuesta'})):
            first = self.post('Hola')
        conversation_id = first.json()['conversation_id']

        with patch(URLOPEN, return_value=fake_response({'reply': 'Segunda respuesta'})) as urlopen:
            self.post('¿Y cuánto cuesta?', conversation_id=conversation_id)

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, CHAT_SETTINGS['N8N_CHAT_WEBHOOK_URL'])
        self.assertEqual(request.get_header('X-webhook-token'), 'token-de-prueba')
        self.assertEqual(urlopen.call_args.kwargs['timeout'], 5)

        payload = json.loads(request.data)
        self.assertEqual(payload['event'], 'chat.message')
        self.assertEqual(payload['conversation_id'], conversation_id)
        self.assertEqual(payload['message'], '¿Y cuánto cuesta?')
        # El mensaje actual va en `message`, no repetido en el historial.
        self.assertEqual(
            payload['history'],
            [{'role': 'user', 'text': 'Hola'}, {'role': 'assistant', 'text': 'Primera respuesta'}],
        )
        self.assertEqual(ChatConversation.objects.count(), 1)

    def test_history_is_limited(self):
        conversation = ChatConversation.objects.create()
        for i in range(chat.HISTORY_LENGTH + 5):
            ChatMessage.objects.create(conversation=conversation, role='user', text=f'm{i}')
        current = ChatMessage.objects.create(conversation=conversation, role='user', text='último')

        history = chat.build_payload(current)['history']
        self.assertEqual(len(history), chat.HISTORY_LENGTH)
        self.assertEqual(history[-1]['text'], f'm{chat.HISTORY_LENGTH + 4}')

    def test_unknown_or_invalid_conversation_id_starts_a_new_one(self):
        for bad_id in ('no-es-un-uuid', '6f1c53f0-0000-4000-8000-000000000000'):
            with patch(URLOPEN, return_value=fake_response({'reply': 'ok'})):
                response = self.post(conversation_id=bad_id)
            self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatConversation.objects.count(), 2)

    def test_empty_message_is_rejected(self):
        with patch(URLOPEN) as urlopen:
            response = self.post('   ')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], content.CHAT['invalid_message'])
        urlopen.assert_not_called()
        self.assertEqual(ChatMessage.objects.count(), 0)

    def test_too_long_message_is_rejected(self):
        with patch(URLOPEN) as urlopen:
            response = self.post('a' * (chat.MESSAGE_MAX_LENGTH + 1))
        self.assertEqual(response.status_code, 400)
        urlopen.assert_not_called()

    def test_invalid_message_text_matches_the_limit(self):
        """El texto de error menciona el límite: si cambia uno, cambia el otro."""
        self.assertIn(str(chat.MESSAGE_MAX_LENGTH), content.CHAT['invalid_message'])

    def test_n8n_down_returns_503_and_keeps_visitor_message(self):
        with patch(URLOPEN, side_effect=urllib.error.URLError('sin conexión')):
            response = self.post()

        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertEqual(data['error'], content.CHAT['error_message'])
        self.assertIn('conversation_id', data)
        self.assertEqual(ChatMessage.objects.get().role, 'user')

    def test_n8n_http_error_returns_503(self):
        error = urllib.error.HTTPError(CHAT_SETTINGS['N8N_CHAT_WEBHOOK_URL'], 500, 'Error', {}, None)
        with patch(URLOPEN, side_effect=error):
            self.assertEqual(self.post().status_code, 503)

    def test_n8n_timeout_returns_503(self):
        with patch(URLOPEN, side_effect=TimeoutError('timed out')):
            self.assertEqual(self.post().status_code, 503)

    def test_malformed_n8n_response_returns_503(self):
        for body in (b'<html>no es json</html>', {'output': 'sin reply'}, {'reply': '   '}, ['lista']):
            with patch(URLOPEN, return_value=fake_response(body)):
                self.assertEqual(self.post().status_code, 503, body)
        self.assertFalse(ChatMessage.objects.filter(role='assistant').exists())

    def test_long_reply_is_truncated(self):
        long_reply = 'x' * (chat.REPLY_MAX_LENGTH + 100)
        with patch(URLOPEN, return_value=fake_response({'reply': long_reply})):
            response = self.post()
        self.assertEqual(len(response.json()['reply']), chat.REPLY_MAX_LENGTH)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_post_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        with patch(URLOPEN) as urlopen:
            response = client.post(self.url, {'message': 'Hola'})
        self.assertEqual(response.status_code, 403)
        urlopen.assert_not_called()


@override_settings(**CHAT_SETTINGS, CHAT_THROTTLE_MAX=3, CHAT_THROTTLE_WINDOW_MINUTES=60)
class ChatThrottleTests(TestCase):
    def setUp(self):
        self.url = reverse('landing:chat')

    def post(self, conversation_id='', **extra):
        with patch(URLOPEN, return_value=fake_response({'reply': 'ok'})):
            return self.client.post(
                self.url, {'message': 'Hola', 'conversation_id': conversation_id}, **extra
            )

    def test_messages_over_limit_same_ip_are_throttled(self):
        for _ in range(3):
            self.post(REMOTE_ADDR='203.0.113.7')
        response = self.post(REMOTE_ADDR='203.0.113.7')

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()['error'], content.CHAT['throttle_message'])
        self.assertEqual(ChatMessage.objects.filter(role='user').count(), 3)

    def test_other_ip_not_affected(self):
        for _ in range(3):
            self.post(REMOTE_ADDR='203.0.113.7')
        self.assertEqual(self.post(REMOTE_ADDR='198.51.100.9').status_code, 200)

    def test_spoofed_forwarded_header_does_not_bypass_throttle(self):
        for i in range(5):
            self.post(HTTP_X_FORWARDED_FOR=f'203.0.113.{i}, 10.0.0.2')
        self.assertEqual(ChatMessage.objects.filter(role='user').count(), 3)

    def test_reusing_a_conversation_from_another_ip_counts_for_the_sender(self):
        """El límite es por IP de quien envía, no por IP de la conversación.

        Si contase la IP con la que se abrió la conversación, bastaría abrirla
        desde una IP y seguir escribiendo desde otra para no toparse nunca.
        """
        opened = self.post(REMOTE_ADDR='198.51.100.9')
        conversation_id = opened.json()['conversation_id']
        for _ in range(4):
            response = self.post(conversation_id=conversation_id, REMOTE_ADDR='203.0.113.7')
        self.assertEqual(response.status_code, 429)


class ChatDisabledTests(TestCase):
    @override_settings(N8N_CHAT_WEBHOOK_URL='')
    def test_endpoint_returns_404_when_disabled(self):
        response = self.client.post(reverse('landing:chat'), {'message': 'Hola'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(ChatMessage.objects.count(), 0)

    @override_settings(N8N_CHAT_WEBHOOK_URL='http://n8n.example/webhook/chat-landing')
    def test_plain_http_to_remote_host_disables_chat(self):
        self.assertFalse(chat.is_enabled())

    @override_settings(N8N_CHAT_WEBHOOK_URL='http://localhost:5678/webhook/chat-landing')
    def test_plain_http_to_localhost_is_allowed(self):
        self.assertTrue(chat.is_enabled())


class ChatWidgetRenderTests(TestCase):
    def setUp(self):
        self.url = reverse('landing:home')

    @override_settings(N8N_CHAT_WEBHOOK_URL='')
    def test_widget_is_not_rendered_when_disabled(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, 'data-chat')
        self.assertNotContains(response, 'js/chat.js')

    @override_settings(**CHAT_SETTINGS)
    def test_widget_is_rendered_hidden_with_content_texts(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'data-chat')
        self.assertContains(response, 'js/chat.js')
        self.assertContains(response, content.CHAT['greeting'])
        self.assertContains(response, reverse('landing:chat'))
        self.assertContains(response, f'maxlength="{chat.MESSAGE_MAX_LENGTH}"')
        # Llega oculto: solo chat.js lo muestra, así que sin JS no aparece.
        self.assertContains(response, 'class="chat" hidden')

    @override_settings(**CHAT_SETTINGS)
    def test_widget_adds_nothing_inline(self):
        """CSP estricta: ni atributos on*, ni style= ni <script> sin src."""
        html = self.client.get(self.url).content.decode()
        start = html.index('class="chat"')
        widget = html[start:html.index('<script', start)]
        self.assertNotIn(' style=', widget)
        self.assertNotIn(' onclick=', widget)
        self.assertNotIn('<script', widget)
