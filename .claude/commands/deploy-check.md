---
description: Verificación completa antes de desplegar a producción
allowed-tools: Bash(python manage.py:*), Bash(.venv/Scripts/python.exe:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Read, Grep
---

Comprueba que el proyecto está listo para desplegar a Easypanel. Ejecuta **todo** lo
siguiente y luego da un veredicto claro.

## 1. Estado del repositorio

- `git status --short` — qué hay sin commitear
- `git log --oneline -5` — últimos commits
- Comprueba que no aparezca ningún archivo sensible (`.env`, `db.sqlite3`, credenciales).
  Si ves algo dudoso, **abre el archivo y míralo antes de dar el visto bueno**.

## 2. Tests

```
.venv/Scripts/python.exe manage.py test apps
```

## 3. Migraciones pendientes de generar

```
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
```

Si detecta cambios sin migrar, dilo y ofrece generarlos — no los generes sin permiso.

## 4. Checks de producción

```
.venv/Scripts/python.exe manage.py check --deploy
```

Recuerda que el `Dockerfile` corre `check --deploy --fail-level ERROR` al arrancar:
**cualquier ERROR impide que el contenedor levante**. Los WARNING que dependen de
variables de entorno que solo existen en Easypanel no son bloqueantes — distínguelos.

## 5. Variables de entorno

Compara `.env.example` con `config/settings/base.py` y `production.py`: si alguna
variable nueva se lee en settings pero no está documentada en `.env.example`, avísalo,
porque habrá que darla de alta en Easypanel → Environment.

## Veredicto

Termina con un resumen corto:

- ✅ / ❌ por cada bloque
- La lista de acciones manuales pendientes en Easypanel (variables nuevas, etc.)
- Si todo está en verde, ofrece preparar el commit — mostrando antes el mensaje propuesto.
