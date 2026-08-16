# Webhook de leads → n8n

`lead-webhook.workflow.json` es el workflow listo para importar en n8n
(**Workflows → ⋯ → Import from File**).

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
