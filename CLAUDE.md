# CLAUDE.md — Django Web Development Rules

Reference: https://docs.djangoproject.com/en/stable/ | https://github.com/django/django

---

## Stack

- **Framework**: Django 5.x (Python 3.12+)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Template engine**: Django Templates (DTL) — Jinja2 only if explicitly requested
- **Static files**: WhiteNoise for production serving
- **Environment vars**: `python-decouple` or `django-environ`
- **Testing**: Django's built-in `TestCase` + `pytest-django`

---

## Project Structure

```
project_root/
├── manage.py
├── config/                  # Project package (rename from default mysite/)
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Local overrides
│   │   └── production.py    # Production overrides
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                    # All Django apps live here
│   ├── accounts/
│   ├── core/
│   └── <feature>/
├── static/
├── templates/               # Project-level templates
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── .env
```

Each app follows the standard Django layout:
```
apps/<name>/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_forms.py
├── urls.py
├── views.py
├── templates/<name>/
└── migrations/
```

---

## Settings

- **Never** hardcode secrets. Use environment variables:
  ```python
  # config/settings/base.py
  from decouple import config

  SECRET_KEY = config('SECRET_KEY')
  DEBUG = config('DEBUG', default=False, cast=bool)
  ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
  ```
- Split settings into `base.py`, `development.py`, `production.py`. Load with `DJANGO_SETTINGS_MODULE`.
- `DEBUG = False` is mandatory in production.
- Set `LANGUAGE_CODE`, `TIME_ZONE`, `USE_I18N`, `USE_TZ = True` explicitly.
- Configure `STATIC_ROOT`, `STATICFILES_DIRS`, `MEDIA_ROOT`, `MEDIA_URL`.

---

## Models

- Always extend `models.Model`. Use explicit `verbose_name` and `verbose_name_plural` in `Meta`.
- Add `__str__` to every model.
- Use `get_absolute_url()` when the model has a detail page.
- Prefer `UUIDField` as primary key for public-facing resources:
  ```python
  import uuid
  from django.db import models

  class Article(models.Model):
      id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
      title = models.CharField(max_length=255)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      class Meta:
          ordering = ['-created_at']
          verbose_name = 'article'
          verbose_name_plural = 'articles'

      def __str__(self):
          return self.title
  ```
- Use `select_related()` for ForeignKey/OneToOne and `prefetch_related()` for ManyToMany to avoid N+1 queries.
- Add database indexes with `db_index=True` or `Meta.indexes`.
- Never use raw SQL unless ORM cannot express the query. When needed, use `connection.execute()` with parameterized queries only.
- Run `makemigrations` after every model change. Never edit migration files manually unless fixing a conflict.
- Use `on_delete=models.PROTECT` by default for ForeignKey; use `CASCADE` only when cascading deletion is intentional.

---

## Views

- Prefer **Class-Based Views (CBVs)** for standard CRUD; use **Function-Based Views (FBVs)** for complex or one-off logic.
- Use `LoginRequiredMixin` (CBV) or `@login_required` (FBV) for protected views.
- Always use `get_object_or_404()` — never bare `Model.objects.get()` in views.
- Return proper HTTP status codes (`Http404`, `HttpResponseForbidden`, etc.).

```python
# CBV example
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .models import Article

class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'articles/detail.html'
    context_object_name = 'article'
```

```python
# FBV example
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'articles/detail.html', {'article': article})
```

---

## URLs

- Each app must have its own `urls.py`. Include it from `config/urls.py` with a namespace:
  ```python
  # config/urls.py
  from django.urls import path, include

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('accounts/', include('apps.accounts.urls', namespace='accounts')),
      path('articles/', include('apps.articles.urls', namespace='articles')),
  ]
  ```
- Use `app_name` in each app's `urls.py` to enable namespacing.
- Name every URL pattern. Reference them with `reverse()` or `{% url %}` — never hardcode paths.

---

## Templates

- Use template inheritance: one `base.html` with `{% block %}` tags; apps extend it.
- Keep logic out of templates. Templates render data, not compute it.
- Use `{% include %}` for reusable partials.
- Always escape user data. Django auto-escapes in DTL — never use `| safe` on user-generated content.
- Organize per-app templates under `templates/<app_name>/`.

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}Site{% endblock %}</title>
</head>
<body>
  {% block content %}{% endblock %}
</body>
</html>
```

---

## Forms

- Always use Django Forms or ModelForms — never build HTML forms manually.
- Validate with `form.is_valid()` before accessing `form.cleaned_data`.
- Use `ModelForm` for model-bound forms. Override `clean_<field>()` for per-field validation.
- Use `{% csrf_token %}` in every POST form — Django enforces this by default.

```python
from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters.')
        return title
```

---

## Authentication & Authorization

- Use Django's built-in `django.contrib.auth` system. Extend `AbstractUser` for custom user fields — do this before the first migration:
  ```python
  # apps/accounts/models.py
  from django.contrib.auth.models import AbstractUser

  class User(AbstractUser):
      bio = models.TextField(blank=True)

  # config/settings/base.py
  AUTH_USER_MODEL = 'accounts.User'
  ```
- Use `PermissionRequiredMixin` or `@permission_required` for object-level restrictions.
- Use `django-guardian` only when row-level permissions are needed.
- Passwords are hashed automatically. Never store plain-text passwords.
- Set `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True` in production.

---

## Admin

- Register all models in `admin.py` of each app.
- Customize `list_display`, `search_fields`, `list_filter`, and `readonly_fields`.
- Use `ModelAdmin` subclasses — avoid the bare `admin.site.register(Model)` pattern.

```python
from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
```

---

## Security

Follow the [Django security checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/):

- `DEBUG = False` in production.
- `SECRET_KEY` from environment, never committed.
- Set `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT = True`, `X_FRAME_OPTIONS = 'DENY'`.
- Enable `SECURE_CONTENT_TYPE_NOSNIFF = True`. (`SECURE_BROWSER_XSS_FILTER` no longer exists in Django ≥5.1.)
- Validate all user input via Forms — never trust raw `request.POST` or `request.GET`.
- Parameterize all ORM queries; never use `RawSQL` with string interpolation.
- Use `django.middleware.security.SecurityMiddleware` (included by default).

---

## Testing

- Every model, view, and form must have tests.
- Use `TestCase` for DB tests, `SimpleTestCase` for no-DB tests.
- Use `Client` for view testing — test both GET and POST flows.
- Use `Factory Boy` or `mixer` for test fixtures instead of raw model creation.
- Aim for ≥ 80% coverage. Run with:
  ```bash
  python manage.py test
  # or with pytest
  pytest --cov=apps --cov-report=term-missing
  ```

```python
from django.test import TestCase, Client
from django.urls import reverse
from .models import Article

class ArticleViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_detail_view_returns_200(self):
        article = Article.objects.create(title='Test Article', content='Body')
        url = reverse('articles:detail', kwargs={'pk': article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
```

---

## API (if needed)

- Use **Django REST Framework (DRF)** for REST APIs.
- Define `serializers.py` per app. Use `ModelSerializer` for model-bound endpoints.
- Apply `IsAuthenticated` as the default permission class in `REST_FRAMEWORK` settings.
- Version APIs via URL prefix: `/api/v1/`.

---

## Deployment

- Use `gunicorn` as the WSGI server behind nginx.
- Collect static files with `python manage.py collectstatic`.
- Run `python manage.py check --deploy` and fix all warnings before going live.
- Use `django-storages` + S3 (or equivalent) for media files in production.
- Use `DATABASE_URL` with `dj-database-url` for database configuration.
- Run migrations on deploy: `python manage.py migrate --run-syncdb`.
- Set up `CONN_MAX_AGE` for persistent DB connections.

---

## Code Style

- Follow **PEP 8**. Use `ruff` for linting and formatting.
- Imports order: stdlib → Django → third-party → local apps.
- No unused imports. Remove dead code immediately.
- Use type hints on function signatures where complexity warrants it.
- Do not add comments that restate what the code already says. Comment only non-obvious constraints or workarounds.

---

## Git Workflow

- `main` is production-ready at all times.
- Feature branches: `feature/<name>`, bugfixes: `fix/<name>`.
- Commit migrations alongside the model changes that require them.
- Never commit `.env`, `*.pyc`, `__pycache__/`, `db.sqlite3`, or `staticfiles/`.

`.gitignore` essentials:
```
.env
*.pyc
__pycache__/
db.sqlite3
staticfiles/
media/
.venv/
```

---

## Quick Commands

```bash
# Create project
django-admin startproject config .

# Create app
python manage.py startapp <name>

# Migrations
python manage.py makemigrations
python manage.py migrate

# Superuser
python manage.py createsuperuser

# Shell
python manage.py shell

# Run dev server
python manage.py runserver

# Security check
python manage.py check --deploy

# Collect static
python manage.py collectstatic --noinput
```
