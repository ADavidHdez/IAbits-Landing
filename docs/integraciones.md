# Integraciones — Webhook de leads → n8n

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
