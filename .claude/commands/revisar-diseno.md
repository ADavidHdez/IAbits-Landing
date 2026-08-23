---
description: Verifica que los cambios pendientes no alteran el diseño ni el estilo
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(.venv/Scripts/python.exe:*), Read, Grep
---

Comprueba que los cambios sin commitear **no tocan el diseño ni el estilo** de la web.
Es la verificación que se hace tras una tarea de backend.

## 1. Qué archivos cambiaron

```
git status --short
```

Marca en **rojo** cualquier cambio en:
- `static/css/main.css`
- `static/js/*.js`
- `templates/base.html`
- `apps/landing/templates/landing/home.html`
- La clave `THEME` de `apps/landing/content.py`

## 2. Si alguno cambió, mira el diff

```
git diff -- static/ templates/ apps/landing/templates/ apps/landing/content.py
```

Para cada cambio, decide si era **necesario** para la tarea o es un efecto colateral.
Los cambios de copy en `content.py` (fuera de `THEME`) no son diseño: son contenido.

## 3. Violaciones de CSP

Busca en las plantillas cosas que la política de seguridad bloquearía:

- `<script>` con código dentro (en vez de `src` con `{% static %}`)
- atributos `on*=` (`onclick`, `onload`…)
- atributos `style="…"`
- URLs externas (`http://`, `https://`, `//cdn…`) en `src` o `href` de recursos

La única excepción permitida es el `<style>` del tema, que lleva nonce.

## 4. Atributos `data-*` intactos

Si se tocó `home.html`, verifica que siguen presentes los atributos que consume el JS:
`data-lead-form`, `data-field`, `data-form-errors`, `data-form-feedback`,
`data-sending-text`, `data-reveal`, `data-reveal-group`, `data-timeline`,
`data-timeline-item`, `data-timeline-icon`, `data-card-3d`.

## 5. Tests

```
.venv/Scripts/python.exe manage.py test apps
```

## Veredicto

Una línea clara: **el diseño está intacto** o **el diseño cambió en X, Y** — y en ese
caso, si fue intencionado o hay que revertirlo.
