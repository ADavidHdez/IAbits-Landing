# Integraciones — Webhook de leads y chat → n8n

Cada lead que entra por el formulario se guarda en la BD y se reenvía a n8n, que lo
registra en Airtable y avisa por Telegram.

Código: [`apps/landing/webhooks.py`](../apps/landing/webhooks.py) ·
Workflow: [`n8n/lead-webhook.workflow.json`](../n8n/lead-webhook.workflow.json)
(importable desde **Workflows → ⋯ → Import from File**).

```
Django ──POST JSON──► [Webhook lead] ──► [¿Token válido?] ──sí──► [Normalizar lead]
                                                │                          │
                                                no                         ▼
                                                ▼                  [Crear en Airtable]
                                          [Responder 401]                  │
                                                                           ▼
                                                                  [Notificar Telegram]
                                                                           │
                                                                           ▼
                                                                    [Responder 200]
```

## Payload que envía Django

```json
{
  "event": "lead.created",
  "source": "landing",
  "sent_at": "2026-08-16T10:00:00+00:00",
  "lead": {
    "id": "b0e1...uuid",
    "name": "Ana Pérez",
    "email": "ana@empresa.com",
    "company": "Empresa SA",
    "service_interest": "base-conocimiento",
    "service_label": "Base de conocimiento con IA",
    "message": "Quiero una base de conocimiento.",
    "ip_address": "203.0.113.7",
    "user_agent": "Mozilla/5.0 ...",
    "created_at": "2026-08-16T10:00:00+00:00"
  }
}
```

Cabeceras: `Content-Type: application/json` y `X-Webhook-Token: <N8N_WEBHOOK_TOKEN>`.

Dentro de n8n los datos llegan en `{{ $json.body.lead.* }}` y el token en
`{{ $json.headers['x-webhook-token'] }}`.

## Variables de entorno en Django

| Variable | Descripción |
|---|---|
| `N8N_WEBHOOK_URL` | URL de producción del webhook. Vacío = desactivado. |
| `N8N_WEBHOOK_TOKEN` | Secreto compartido; debe coincidir con el nodo *¿Token válido?*. |
| `N8N_WEBHOOK_TIMEOUT` | Segundos de espera (por defecto 10). |
| `N8N_WEBHOOK_SOURCE` | Etiqueta de origen si un día hay varias webs (por defecto `landing`). |

## Qué hace el workflow con cada lead

`Normalizar lead → Crear en Airtable → Notificar Telegram → Responder 200`

### Airtable (CRM)

1. En Airtable, crea (o reutiliza) una base con una tabla de columnas: `Nombre`,
   `Email`, `Empresa`, `Servicio`, `Mensaje`, `IP`, `Creado en`, `Lead ID`.
2. En n8n, abre el nodo **"Crear en Airtable"** → en *Credential* crea una nueva
   ("Airtable Personal Access Token", generado en
   [airtable.com/create/tokens](https://airtable.com/create/tokens) con permisos
   `data.records:write` sobre esa base).
3. Sustituye `PON-AQUI-TU-BASE-ID` por el ID de tu base (`app...`, visible en la
   URL de Airtable) y `PON-AQUI-TU-TABLA-ID` por el ID o nombre de la tabla.
4. Si usas otros nombres de columna, ajusta el mapeo dentro de *Columns*.

### Telegram (solo notificación, sin datos del lead)

1. Crea un bot con [@BotFather](https://t.me/BotFather) (`/newbot`) y copia el
   token que te da.
2. En n8n, abre el nodo **"Notificar Telegram"** → en *Credential* crea una
   nueva "Telegram API" pegando ese token.
3. Consigue tu `chat_id`: escríbele algo a tu bot y visita
   `https://api.telegram.org/bot<TOKEN>/getUpdates` — ahí aparece `"chat":{"id":...}`.
   (Si notificas a un grupo, añade el bot al grupo y usa el id del grupo, que
   empieza por `-`.)
4. Pega ese id en `PON-AQUI-TU-CHAT-ID-TELEGRAM`. El mensaje ya está fijado a
   **"🆕 Nuevo Lead"**, sin datos del lead — solo un aviso.

## Comportamiento ante fallos

El lead se guarda **siempre** en la base de datos; el envío a n8n ocurre después,
en un hilo aparte, para que el visitante nunca espere. Si n8n falla, el error se
registra en el log y el lead queda en el admin con la columna *enviado a n8n* en
rojo: se puede reintentar seleccionándolo y usando la acción **Reenviar a n8n**.

Con `N8N_WEBHOOK_URL` vacío la integración queda desactivada por completo y el lead
solo se guarda en la BD — es el comportamiento por defecto en desarrollo y en los tests.

## Red interna vs. pública (Easypanel)

Si n8n y la web vivieran en el **mismo proyecto** de Easypanel, podrían hablarse por la
red privada de Docker: `http://<nombre-servicio-n8n>:5678/webhook/lead-landing`.

En esta instalación están en **proyectos distintos del mismo VPS**, y cada proyecto tiene
su red Docker aislada, así que se usa la URL pública HTTPS. El tráfico resuelve a la IP
del propio servidor y no llega a salir a internet de verdad; va cifrado y protegido por
el token. Conectar ambas redes a mano (`docker network connect`) es posible pero se
pierde en cada redeploy de n8n, así que se descartó.

## Si cambias el payload

`build_payload()` en `webhooks.py` define los nombres de los campos. Si los cambias,
hay que actualizar también el workflow de n8n (nodo *Normalizar lead*) y el test
`test_posts_json_payload_with_token_header`. Los tres van juntos.

---

# Chat con el agente de IA

El botón flotante de la esquina abre un chat en el que responde un agente de IA
montado en n8n. El navegador nunca habla con n8n: envía cada mensaje a `POST /landing/chat/`
y Django lo reenvía, así que la URL y el token no se ven en la web.

Código: [`apps/landing/chat.py`](../apps/landing/chat.py) (llamada a n8n) ·
`ChatView` en [`views.py`](../apps/landing/views.py) ·
[`static/js/chat.js`](../static/js/chat.js) ·
[`apps/landing/templates/landing/partials/chat-widget.html`](../apps/landing/templates/landing/partials/chat-widget.html) ·
Workflow: [`n8n/chat-agent.workflow.json`](../n8n/chat-agent.workflow.json)

```
chat.js ──fetch──► POST /landing/chat/ ──► [Webhook chat] ──► [¿Token válido?] ──sí──► [Agente IAbits] ◄── [Modelo Anthropic]
   ▲                  │                                     │                         │
   │                  │                                     no                        ▼
   └──── { reply } ◄──┘◄──────────────────────────── [Responder 401]    [Responder con la respuesta]
```

## Qué hace Django con cada mensaje

1. Valida el texto (1–500 caracteres) y el CSRF.
2. Aplica el límite por IP (`CHAT_THROTTLE_*`, por defecto 20 mensajes/hora), contado
   sobre la IP de **quien envía** cada mensaje vía `get_client_ip()`.
3. Recupera la conversación (`conversation_id`) o empieza una nueva si no existe.
4. Guarda el mensaje del visitante **antes** de llamar a n8n: queda en el admin aunque falle.
5. Llama a n8n de forma síncrona (el visitante espera la respuesta) con `N8N_CHAT_TIMEOUT`.
6. Guarda la respuesta y la devuelve. Si n8n falla, tarda o responde sin `reply`, el
   visitante ve `content.CHAT['error_message']` con un enlace al formulario (HTTP 503).

La memoria de la conversación vive en la BD de Django: cada petición lleva los últimos
10 mensajes en `history`, así que el workflow no guarda nada entre llamadas y un
reinicio de n8n no borra ninguna conversación.

Las conversaciones se leen en `/admin/` → **Conversaciones del chat** (solo lectura).

## Payload que envía Django

```json
{
  "event": "chat.message",
  "source": "landing",
  "sent_at": "2026-09-27T10:00:00+00:00",
  "conversation_id": "b0e1...uuid",
  "message": "¿Y cuánto cuesta?",
  "history": [
    {"role": "user", "text": "Hola"},
    {"role": "assistant", "text": "¡Hola! ¿Qué tarea te gustaría automatizar?"}
  ]
}
```

Cabeceras: `Content-Type: application/json` y `X-Webhook-Token: <N8N_WEBHOOK_TOKEN>`
(el mismo token que el webhook de leads).

**n8n debe responder** `{"reply": "texto de la respuesta"}` con un 2xx. El texto se
muestra tal cual, como texto plano (se respetan los saltos de línea; el Markdown no
se interpreta), y se recorta a 4000 caracteres.

## Variables de entorno en Django

| Variable | Descripción |
|---|---|
| `N8N_CHAT_WEBHOOK_URL` | URL de producción del webhook del chat. Vacío = el chat no se muestra y `/landing/chat/` da 404. |
| `N8N_CHAT_TIMEOUT` | Segundos de espera a la respuesta del agente (por defecto 25; menos que los 60 de gunicorn). |
| `CHAT_THROTTLE_MAX` / `CHAT_THROTTLE_WINDOW_MINUTES` | Mensajes por IP y ventana (por defecto 20 / 60 min). Cada mensaje es una llamada de pago al modelo. |

## Puesta en marcha del workflow

1. En n8n: **Workflows → ⋯ → Import from File** → `n8n/chat-agent.workflow.json`.
2. Nodo **¿Token válido?**: sustituye `PON-AQUI-EL-MISMO-TOKEN-QUE-EN-N8N_WEBHOOK_TOKEN`.
3. Nodo **Modelo Anthropic** → *Credential* → nueva "Anthropic API" con una API key de
   [console.anthropic.com](https://console.anthropic.com). Viene con Claude Haiku 4.5
   (rápido y barato para un chat); se cambia en el desplegable *Model*.
   Para usar OpenAI, borra ese nodo, añade *OpenAI Chat Model* y conéctalo al agente
   en la entrada *Chat Model*.
4. El comportamiento del agente (servicios, tono, reglas) está en el nodo
   **Agente IAbits → Options → System Message**. Si cambian los servicios en
   `content.py`, actualízalo también allí.
5. Activa el workflow, copia la **Production URL** del nodo *Webhook chat* y ponla en
   `N8N_CHAT_WEBHOOK_URL`.

## Si cambias el payload

`build_payload()` en `chat.py` define los campos, y el workflow los lee en el campo
*Text* del nodo *Agente IAbits* (`$json.body.message` y `$json.body.history`). El test
`test_sends_payload_with_token_and_history` los fija. Los tres van juntos.
