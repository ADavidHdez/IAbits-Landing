# CLAUDE.md — IAbits Landing

Landing de una sola página para **IAbits Studio** (agencia de automatización con IA).
Capta leads por formulario → los guarda en BD → los reenvía a n8n por webhook.

**Django 6 · Python 3.13 · SQLite (dev) / Postgres (prod) · Docker + Easypanel**

> **Idioma**: contenido de cara al usuario, comentarios del código, docstrings y
> mensajes de commit **en español**.

---

## Reglas que no se negocian

1. **No tocar diseño ni estilo salvo petición explícita.** Si una tarea es de backend,
   `main.css`, los `.js` de animación y la estructura de `home.html` se quedan como están.
2. **`apps/landing/content.py` es la única fuente** de textos, colores, servicios y datos
   de contacto. Nunca escribas texto literal en una plantilla ni un color en el CSS.
3. **CSP estricta** (`SECURE_CSP` en `config/settings/base.py`): prohibido JS inline,
   `onclick=`, CSS inline y recursos externos (CDN, Google Fonts). El único inline
   permitido es el `<style>` del tema, que va con nonce.
4. **Nada de secretos en el repo.** Todo por variables de entorno vía `python-decouple`.
5. **Tests con cada cambio de lógica**: `python manage.py test apps` (47 en verde hoy).
6. Sin dependencias nuevas salvo necesidad real — la stack es deliberadamente pequeña.

---

## Mapa del código

| Ruta | Qué es | Cuándo tocarlo |
|---|---|---|
| `apps/landing/content.py` | **Textos, colores, servicios, contacto** | Cambiar cualquier copy o color |
| `apps/landing/models.py` | Modelo `Lead` (UUID pk) | Nuevo campo del lead → requiere migración |
| `apps/landing/forms.py` | `LeadForm` + honeypot `website` | Cambiar campos del formulario |
| `apps/landing/views.py` | `LandingView` (CreateView): honeypot, throttle, AJAX/JSON | Lógica de envío |
| `apps/landing/webhooks.py` | Envío del lead a n8n (stdlib `urllib`, hilo aparte) | Integración n8n |
| `apps/landing/admin.py` | Tabla de leads + acción "Reenviar a n8n" | Panel `/admin/` |
| `apps/landing/templates/landing/home.html` | La landing entera (175 líneas) | Estructura de secciones |
| `templates/base.html` | Molde: `<head>`, nonce, variables CSS del tema | Rara vez |
| `static/css/main.css` | Todo el estilo (839 líneas, usa `var(--…)`) | Solo en tareas de diseño |
| `static/js/*.js` | `lead-form` (AJAX), `reveal`, `cards-3d`, `confetti`, `timeline` | Solo en tareas de diseño |
| `apps/accounts/` | `User` custom (`AbstractUser`) + login. Solo staff, sin registro público | Casi nunca |
| `config/settings/{base,development,production}.py` | Configuración por entorno | Nueva variable de entorno |
| `n8n/lead-webhook.workflow.json` | Workflow importable en n8n | Cambia el payload del webhook |

**URLs**: `/` → landing · `/accounts/login/` · admin en `settings.ADMIN_URL` (secreto en prod).

---

## Invariantes que se rompen fácil

- **Tema → CSS**: `content.THEME` se inyecta como variables CSS en `base.html`; `main.css`
  las consume con `var(--color-primary, #fallback)`. Cambiar un color = editar `content.py`.
- **Servicios**: `content.service_choices()` alimenta el `<select>` del formulario. Añadir
  un servicio en `SERVICES` actualiza la web y el formulario **sin migración**.
- **Formulario, tres capas de defensa**: honeypot `website` (finge éxito), throttle por IP
  respaldado en BD (`LEAD_THROTTLE_*`, funciona con varios workers) y CSRF.
- **AJAX con degradación**: `lead-form.js` envía por `fetch` con `X-Requested-With`; la
  vista responde JSON. Sin JS, POST clásico + Post/Redirect/Get. **Mantén ambos caminos.**
- **Webhook**: se dispara en `transaction.on_commit` y en un hilo daemon. El lead se guarda
  **siempre** primero; si n8n falla, se loguea y se reintenta desde el admin. Nunca bloquear
  la respuesta al visitante.
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
| [docs/integraciones.md](docs/integraciones.md) | Webhook n8n: payload, variables, Airtable/Telegram |
| [docs/despliegue.md](docs/despliegue.md) | Easypanel, Docker, variables de entorno, checklist de deploy |
| [docs/convenciones.md](docs/convenciones.md) | Estilo de código y patrones Django aplicables aquí |

`notas-aprendizaje.md` (gitignored) son apuntes personales del dueño del repo: sirve de
contexto histórico, **no lo edites** salvo que te lo pidan.
