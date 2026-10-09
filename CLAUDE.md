# CLAUDE.md — IAbits Studio

Website for **IAbits Studio** (AI automation agency), live at `https://iabits.tech`.
Two independent sites with no links between them:

- `/` — company home (intro, products, support plans, tech, team). Its product buttons
  and the support "Solicitar información" button lead to `/contacto/?producto=<slug>`, a
  contact page with its own form (`ContactForm`). The slug sets the `<h1>` and a hidden,
  server-validated `product` field (`content.contact_requests()`: `PRODUCTS` + `INFO_REQUEST`,
  the fallback when the slug is missing or unknown).
- `/landing/` — lead-capture landing: form → DB → n8n webhook, plus an optional AI chat widget.

Both forms save a `Lead`; `Lead.source` (`landing` / `contacto`) tells them apart.

**Django 6.0 · Python 3.13 · SQLite (dev) / Postgres (prod) · WhiteNoise · Gunicorn · Docker on Easypanel (auto-deploys from `master`)**

> **Language**: user-facing content, code comments, docstrings and commit messages are
> written in **Spanish**.

---

## Non-negotiable rules

1. **Don't touch design or styling unless explicitly asked.** On backend tasks,
   `main.css`, `static/js/*` and the template structure stay as they are.
2. **`content.py` is the single source** of copy, colours, services and contact data.
   `apps/landing/content.py` owns the shared `BRAND`, `THEME` and `CONTACT`;
   `apps/home/content.py` holds the home copy and imports those. Never hardcode text in
   a template or a colour in CSS.
3. **Strict CSP** (`SECURE_CSP` in `config/settings/base.py`): no inline JS, no
   `onclick=`, no inline CSS, no external resources (CDNs, Google Fonts). The only inline
   allowed is the theme `<style>`, which carries a nonce.
4. **No secrets in the repo.** Everything goes through env vars via `python-decouple`
   (template: `.env.example`).
5. **Tests with every logic change**: `python manage.py test apps` (145 passing, Oct 2026).
6. No new dependencies without a real need — the stack is deliberately small.

---

## Code map

| Path | What it is | Touch it when |
|---|---|---|
| `apps/landing/content.py` | Landing copy, `SERVICES`, `CHAT`, plus shared `BRAND`/`THEME`/`CONTACT` | Changing landing copy or any colour |
| `apps/home/content.py` | Home copy: `PRODUCTS`, `SUPPORT_PLANS`, `TECH_ITEMS`, `TEAM`… · contact page: `CONTACT_SITE`, `CONTACT_FORM`, `CONTACT_PREFERENCES`, `INFO_REQUEST`, `contact_requests()`, `product_choices()` | Changing home copy |
| `apps/landing/models.py` | `Lead` (UUID pk, `source`), `ChatConversation`, `ChatMessage` | New field → migration |
| `apps/landing/forms.py` | `BaseLeadForm` (`website` honeypot + message length) → `LeadForm` (landing) and `ContactForm` (`/contacto/`) | Form fields |
| `apps/landing/views.py` | `LeadSubmitMixin` (honeypot, shared per-IP throttle, AJAX/JSON, sets `source`) · `LandingView` · `ChatView` (`POST /landing/chat/`) | Submit and chat logic |
| `apps/landing/webhooks.py` | Sends the lead to n8n (stdlib `urllib`, background thread) | n8n lead integration |
| `apps/landing/chat.py` | Synchronous call to the n8n AI agent | Chat integration |
| `apps/landing/admin.py` | Leads table + "Reenviar a n8n" action · read-only chat conversations | `/admin/` panel |
| `apps/landing/templates/landing/` | `landing.html` + `partials/chat-widget.html` (only included when chat is enabled) | Section structure |
| `apps/home/` | `HomeView` (TemplateView) + `home/home.html` · `ContactView` (`LeadSubmitMixin` + CreateView) + `home/contact.html`. No models of its own | Company presentation, contact page |
| `apps/accounts/` | Custom `User`, `LoginAttempt`, `ThrottledLoginView`. Staff only, no sign-up | Rarely |
| `apps/common/http.py` | `get_client_ip()`: spoof-proof visitor IP | Anything IP-based |
| `apps/common/{seo,views,sitemaps,context_processors}.py` | Canonical URL, HTML-safe `json_ld()`, `robots.txt`, `sitemap.xml`, `/favicon.ico` redirect | New indexable page → add it to `StaticViewSitemap` |
| `apps/{landing,home}/seo.py` | Per-page JSON-LD (schema.org), built in Python | Organization or offer data changes |
| `templates/base.html` | Layout: `<head>`, nonce, theme CSS variables | Rarely |
| `templates/partials/seo-meta.html` | Meta description, Open Graph, Twitter Card, JSON-LD | Rarely |
| `static/css/main.css` | All styling (uses `var(--…)`) | Design tasks only |
| `static/js/*.js` | `lead-form` (AJAX), `chat`, `reveal`, `cards-3d`, `confetti`, `timeline` — landing; `lead-form` + `confetti` also on `/contacto/` | Design tasks only |
| `config/settings/{base,development,production}.py` | Per-environment settings | New env var |
| `requirements/{base,development,production}.txt` | Dependencies (`factory-boy` dev-only; `gunicorn`, `psycopg2`, `dj-database-url` prod-only) | New dependency |
| `n8n/*.workflow.json` | Importable n8n workflows: lead webhook and chat agent (system prompt included) | Payload or agent behaviour changes |

**URLs**: `/` · `/contacto/` · `/landing/` · `/landing/chat/` (POST JSON) · `/accounts/login/` · `/robots.txt` ·
`/sitemap.xml` · `/favicon.ico` · admin at `settings.ADMIN_URL` (secret in prod; **never**
in `robots.txt`).

---

## Easy-to-break invariants

- **Theme → CSS**: `THEME` is injected as CSS variables in `base.html`; `main.css` reads
  them as `var(--color-primary, #fallback)`. Changing a colour = editing `content.py`.
- **Services**: `content.service_choices()` feeds the form `<select>`. Adding to
  `SERVICES` updates page and form **without a migration**.
- **Lead form, three defence layers**: `website` honeypot (fakes success), DB-backed
  per-IP throttle (`LEAD_THROTTLE_*`, safe across workers) and CSRF.
- **Visitor IP**: always via `apps.common.http.get_client_ip()` — it takes the entry
  added by our proxy (`TRUSTED_PROXY_DEPTH`) and validates it. Reading
  `X-Forwarded-For` by hand reopens a throttle bypass.
- **Login**: `/accounts/login/` returns 429 after `LOGIN_THROTTLE_MAX` failures per IP,
  recorded in `LoginAttempt` by the `user_login_failed` signal.
- **AJAX with graceful degradation**: `lead-form.js` posts via `fetch` with
  `X-Requested-With` and gets JSON; without JS it's a classic POST + Post/Redirect/Get.
  **Keep both paths.**
- **Lead webhook**: fired on `transaction.on_commit` in a daemon thread. The lead is
  **always** saved first; if n8n fails it's logged and can be resent from the admin.
  Never block the visitor's response.
- **Chat**: rendered only if `N8N_CHAT_WEBHOOK_URL` is valid, and ships `hidden` (no JS,
  no chat). The n8n call is **synchronous** (`N8N_CHAT_TIMEOUT` < gunicorn's 60 s), hence
  gunicorn's `--threads`. Conversation memory is the DB: Django sends the full history on
  each request. Throttle (`CHAT_THROTTLE_*`) counts the sender's IP per message. Agent
  replies are rendered with `textContent`, never `innerHTML`.
- **SEO**: each page's `title` / `meta_description` live in its `SITE` dict (≤ 60 / ≤ 158
  chars, enforced by a test) and feed `<title>`, meta, Open Graph and JSON-LD. `BRAND`
  reaches every template through `apps.landing.context_processors.brand`. No absolute
  URL hardcodes a domain: everything is built from the request.
- **Production boot**: the Dockerfile `CMD` runs `migrate` → `collectstatic` →
  `check --deploy --fail-level ERROR` → gunicorn. **An ERROR-level check blocks startup.**

---

## Commands

```bash
pip install -r requirements/development.txt
python manage.py runserver                     # dev (config.settings.development)
python manage.py test apps                     # full suite
python manage.py makemigrations landing
python manage.py makemigrations --check --dry-run
python manage.py check --deploy                # before deploying
```

On Windows the venv interpreter is `.venv/Scripts/python.exe`.

**Claude Code tooling** (`.claude/`): commands `/deploy-check`, `/nuevo-servicio`,
`/nueva-seccion`, `/revisar-diseno`; skills `copy-iabits` (landing copy) and `seo-audit`.
`settings.json` pre-approves read-only git, `test`, `check` and `makemigrations --check`.

---

## Topic docs — read only when the task needs them

| File | Open it for |
|---|---|
| [docs/arquitectura.md](docs/arquitectura.md) | Full request flow, design decisions and their rationale |
| [docs/contenido-y-estilo.md](docs/contenido-y-estilo.md) | Editing copy, colours, sections or animations |
| [docs/integraciones.md](docs/integraciones.md) | n8n webhook (payload, env vars, Airtable/Telegram) · AI chat agent |
| [docs/despliegue.md](docs/despliegue.md) | Easypanel, Docker, env vars, deploy checklist |
| [docs/convenciones.md](docs/convenciones.md) | Code style and Django patterns used here |

`notas-aprendizaje.md` (gitignored) holds the repo owner's personal notes: historical
context only — **don't edit it** unless asked.
