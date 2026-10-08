# CLAUDE.md — IAbits Landing

Web de **IAbits Studio** (agencia de automatización con IA): una home de presentación
en `/` y una landing de captación en `/landing/`, sin enlaces entre ellas.
La landing capta leads por formulario → los guarda en BD → los reenvía a n8n por webhook.

**Django 6 · Python 3.13 · SQLite (dev) / Postgres (prod) · Docker + Easypanel**

> **Idioma**: contenido de cara al usuario, comentarios del código, docstrings y
> mensajes de commit **en español**.

---

## Reglas que no se negocian

1. **No tocar diseño ni estilo salvo petición explícita.** Si una tarea es de backend,
   `main.css`, los `.js` de animación y la estructura de `landing.html` se quedan como están.
2. **`apps/landing/content.py` es la única fuente** de textos, colores, servicios y datos
   de contacto. Nunca escribas texto literal en una plantilla ni un color en el CSS.
3. **CSP estricta** (`SECURE_CSP` en `config/settings/base.py`): prohibido JS inline,
   `onclick=`, CSS inline y recursos externos (CDN, Google Fonts). El único inline
   permitido es el `<style>` del tema, que va con nonce.
4. **Nada de secretos en el repo.** Todo por variables de entorno vía `python-decouple`.
5. **Tests con cada cambio de lógica**: `python manage.py test apps` (125 en verde hoy).
6. Sin dependencias nuevas salvo necesidad real — la stack es deliberadamente pequeña.

---

## Mapa del código

| Ruta | Qué es | Cuándo tocarlo |
|---|---|---|
| `apps/landing/content.py` | **Textos, colores, servicios, contacto** | Cambiar cualquier copy o color |
| `apps/landing/models.py` | `Lead` (UUID pk), `ChatConversation` y `ChatMessage` | Nuevo campo → requiere migración |
| `apps/landing/forms.py` | `LeadForm` + honeypot `website` | Cambiar campos del formulario |
| `apps/landing/views.py` | `LandingView` (CreateView): honeypot, throttle, AJAX/JSON · `ChatView` (`POST /landing/chat/`) | Lógica de envío y del chat |
| `apps/landing/webhooks.py` | Envío del lead a n8n (stdlib `urllib`, hilo aparte) | Integración n8n |
| `apps/landing/chat.py` | Llamada síncrona al agente de IA de n8n para el chat | Integración del chat |
| `apps/landing/admin.py` | Tabla de leads + acción "Reenviar a n8n" · conversaciones del chat (solo lectura) | Panel `/admin/` |
| `apps/landing/templates/landing/partials/chat-widget.html` | HTML del chat flotante (se incluye solo si el chat está activo) | Estructura del chat |
| `apps/landing/templates/landing/landing.html` | La landing entera (175 líneas) | Estructura de secciones |
| `apps/home/` | Web home (`HomeView`, `TemplateView`) con su plantilla `home/home.html`. Sin modelos. Textos en `apps/home/content.py` (comparte `THEME` y `CONTACT` con la landing) | Presentación de la empresa |
| `templates/base.html` | Molde: `<head>`, nonce, variables CSS del tema | Rara vez |
| `static/css/main.css` | Todo el estilo (839 líneas, usa `var(--…)`) | Solo en tareas de diseño |
| `static/js/*.js` | `lead-form` (AJAX), `chat`, `reveal`, `cards-3d`, `confetti`, `timeline` | Solo en tareas de diseño |
| `apps/accounts/` | `User` custom (`AbstractUser`), `LoginAttempt` y `ThrottledLoginView`. Solo staff, sin registro público | Casi nunca |
| `apps/common/http.py` | `get_client_ip()`: IP real del visitante a prueba de cabeceras falsas | Nada que dependa de la IP |
| `apps/common/{seo,views,sitemaps,context_processors}.py` | SEO técnico: canónica, `json_ld()` seguro para HTML, `robots.txt`, `sitemap.xml`, redirección de `/favicon.ico` | Nueva página indexable → añadirla a `StaticViewSitemap` |
| `apps/{landing,home}/seo.py` | JSON-LD (schema.org) de cada página, generado en Python | Cambian datos de la organización u ofertas |
| `templates/partials/seo-meta.html` | Meta description, Open Graph, Twitter Card y JSON-LD (lee `site.title`/`site.meta_description`) | Rara vez |
| `config/settings/{base,development,production}.py` | Configuración por entorno | Nueva variable de entorno |
| `n8n/lead-webhook.workflow.json` | Workflow importable en n8n | Cambia el payload del webhook |
| `n8n/chat-agent.workflow.json` | Workflow del agente de IA del chat (prompt de sistema incluido) | Cambia el payload o el comportamiento del agente |

**URLs**: `/` → home · `/landing/` → landing · `/landing/chat/` (POST JSON) · `/accounts/login/` · `/robots.txt` · `/sitemap.xml` · `/favicon.ico` · admin en `settings.ADMIN_URL` (secreto en prod; **nunca** en `robots.txt`).

---

## Invariantes que se rompen fácil

- **Tema → CSS**: `content.THEME` se inyecta como variables CSS en `base.html`; `main.css`
  las consume con `var(--color-primary, #fallback)`. Cambiar un color = editar `content.py`.
- **Servicios**: `content.service_choices()` alimenta el `<select>` del formulario. Añadir
  un servicio en `SERVICES` actualiza la web y el formulario **sin migración**.
- **Formulario, tres capas de defensa**: honeypot `website` (finge éxito), throttle por IP
  respaldado en BD (`LEAD_THROTTLE_*`, funciona con varios workers) y CSRF.
- **IP del visitante**: siempre vía `apps.common.http.get_client_ip()`. Coge la **última**
  entrada de `X-Forwarded-For` (la que añade el proxy; las anteriores las controla el
  cliente) y la valida. Leer la cabecera a mano reabre un bypass del throttle.
- **Login**: `/accounts/login/` corta a los `LOGIN_THROTTLE_MAX` fallos por IP y responde
  429. Los fallos los apunta la señal `user_login_failed` en `LoginAttempt`.
- **AJAX con degradación**: `lead-form.js` envía por `fetch` con `X-Requested-With`; la
  vista responde JSON. Sin JS, POST clásico + Post/Redirect/Get. **Mantén ambos caminos.**
- **Webhook**: se dispara en `transaction.on_commit` y en un hilo daemon. El lead se guarda
  **siempre** primero; si n8n falla, se loguea y se reintenta desde el admin. Nunca bloquear
  la respuesta al visitante.
- **Chat**: el widget solo se renderiza si `N8N_CHAT_WEBHOOK_URL` es válida y llega con
  `hidden` (sin JS no aparece). A diferencia del webhook de leads, la llamada a n8n es
  **síncrona** (el visitante espera la respuesta); por eso gunicorn corre con `--threads`.
  La memoria de la conversación es la BD: Django manda el historial en cada petición.
  El throttle cuenta por IP de quien envía cada mensaje, no por la de la conversación.
  Las respuestas del agente se pintan con `textContent`, nunca `innerHTML`.
- **SEO**: `title` y `meta_description` de cada página viven en su `SITE` (≤ 60 y ≤ 158
  caracteres; un test lo vigila) y alimentan `<title>`, meta, Open Graph y JSON-LD.
  Los datos de marca comunes (nombre, logo y sus medidas, imagen social) están en
  `BRAND` de `apps/landing/content.py` y llegan a toda plantilla por context processor.
  Ninguna URL absoluta lleva dominio fijo: todo sale de la petición.
- **Arranque en producción**: el `CMD` del Dockerfile corre `migrate` → `collectstatic` →
  `check --deploy --fail-level ERROR` → gunicorn. **Un check en ERROR impide arrancar.**

---

## Comandos

```bash
python manage.py runserver              # dev (usa config.settings.development)
python manage.py test apps              # suite completa
python manage.py makemigrations landing
python manage.py check --deploy         # antes de desplegar
```

En Windows el intérprete del venv es `.venv/Scripts/python.exe`.

---

## Documentación por temas — léela solo si la tarea lo pide

| Archivo | Cuándo abrirlo |
|---|---|
| [docs/arquitectura.md](docs/arquitectura.md) | Flujo completo de una petición, decisiones de diseño y por qué |
| [docs/contenido-y-estilo.md](docs/contenido-y-estilo.md) | Editar textos, colores, secciones o animaciones |
| [docs/integraciones.md](docs/integraciones.md) | Webhook n8n: payload, variables, Airtable/Telegram · chat con el agente de IA |
| [docs/despliegue.md](docs/despliegue.md) | Easypanel, Docker, variables de entorno, checklist de deploy |
| [docs/convenciones.md](docs/convenciones.md) | Estilo de código y patrones Django aplicables aquí |

`notas-aprendizaje.md` (gitignored) son apuntes personales del dueño del repo: sirve de
contexto histórico, **no lo edites** salvo que te lo pidan.
