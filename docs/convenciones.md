# Convenciones de código

Reglas de Django y estilo **aplicables a este proyecto**. Se han podado las que no
tienen sentido aquí (DRF, django-guardian, S3, Celery): si algún día hacen falta, se
añaden entonces.

---

## Estilo general

- **PEP 8**, comillas simples, líneas ≲ 100 caracteres.
- Orden de imports: stdlib → Django → terceros → apps locales, separados por línea en blanco.
- Sin imports ni código muerto.
- Type hints solo donde aporten (`def is_enabled() -> bool:`), no por sistema.
- **Comentarios**: solo para lo no evidente — una restricción, un porqué, una trampa.
  Nunca para repetir lo que el código ya dice. Mira el estilo de `views.py` y
  `webhooks.py`: comentarios cortos que explican *por qué*, no *qué*.
- Todo en español: comentarios, docstrings, mensajes de error y de commit.

---

## Modelos

- `__str__` en todos.
- `Meta` con `ordering`, `verbose_name` y `verbose_name_plural` en español.
- `verbose_name` del campo como primer argumento posicional (`models.CharField('nombre', …)`),
  que es el estilo ya usado en `Lead`.
- `UUIDField` como pk en modelos de cara al público.
- `on_delete=models.PROTECT` por defecto; `CASCADE` solo si el borrado en cascada es
  intencionado.
- `select_related()` para FK/OneToOne y `prefetch_related()` para M2M — evita N+1.
- `makemigrations` tras cada cambio, y la migración se commitea con el modelo.
  No editar migraciones a mano salvo para resolver conflictos.

## Vistas

- CBV para CRUD estándar (`LandingView` es una `CreateView`); FBV solo para lógica
  puntual que no encaje.
- `get_object_or_404()`, nunca `Model.objects.get()` pelado.
- `LoginRequiredMixin` / `@login_required` en lo protegido.
- Códigos HTTP correctos: 400 en formulario inválido por AJAX, 429 en throttle, etc.

## Formularios

- Siempre `Form` o `ModelForm`; nunca HTML a mano ni leer `request.POST` directamente.
- Validación por campo en `clean_<campo>()`.
- `{% csrf_token %}` en todo POST.

## Plantillas

- Heredan de `templates/base.html`.
- Sin lógica: la plantilla pinta, no calcula. Si necesitas computar algo, hazlo en la
  vista o en `content.py`.
- Nunca `|safe` sobre datos de usuario.
- Recuerda: `{# … #}` comenta **una línea**; para bloques, `{% comment %}`.

## Admin

- Siempre subclase de `ModelAdmin` con `@admin.register(...)`, nunca
  `admin.site.register(Model)` pelado.
- Configurar `list_display`, `search_fields`, `list_filter` y `readonly_fields`.
- Campos derivados con `@admin.display(description='…')`.

## Seguridad

- Secretos por variables de entorno, jamás en el repo (ni en repos privados: el
  historial de Git es para siempre).
- Validar toda entrada con Forms.
- Nada de SQL con interpolación de cadenas; el ORM parametriza solo.
- Respetar la CSP: sin inline ni recursos externos (ver [arquitectura.md](arquitectura.md)).

---

## Tests

- Cada modelo, formulario y vista con tests. `TestCase` con BD, `SimpleTestCase` sin ella.
- Probar GET y POST, y en este proyecto **los dos caminos del formulario**: POST clásico
  y POST AJAX.
- Los textos se comparan contra `content.*`, nunca contra literales copiados — así un
  cambio de copy no rompe los tests.
- `override_settings` para variar configuración; `captureOnCommitCallbacks(execute=True)`
  para lo que dependa de `transaction.on_commit`.
- Fábricas en `apps/landing/tests/factories.py`.

```bash
python manage.py test apps
```

---

## Git

- `master` siempre desplegable.
- Ramas: `feature/<nombre>`, `fix/<nombre>`.
- Mensajes de commit en español, imperativo y concretos ("Añade webhook de leads a n8n",
  no "cambios varios").
- Nunca commitear `.env`, `db.sqlite3`, `__pycache__/`, `staticfiles/`, `media/`
  ni `notas-aprendizaje.md`.

---

## Dependencias

La stack es pequeña a propósito (Django, decouple, whitenoise, gunicorn, psycopg2,
dj-database-url). Antes de añadir una:

1. ¿Se puede con la stdlib? El webhook a n8n usa `urllib` en vez de `requests` justo
   por esto.
2. Si hace falta de verdad, va al `requirements/*.txt` correcto: `base.txt` si es común,
   `development.txt` si es de test, `production.txt` si solo del servidor.
