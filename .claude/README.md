# Carpeta `.claude/` — tus comandos y skills

Aquí guardas instrucciones reutilizables para Claude Code. Todo lo de esta carpeta se
commitea al repo (menos `settings.local.json`), así que viaja contigo.

```
.claude/
├── commands/          # Comandos que TÚ invocas escribiendo /nombre
├── skills/            # Skills que Claude activa SOLO cuando detecta que hacen falta
└── settings.json      # Permisos y configuración del proyecto
```

> Claude Code lee estas rutas exactas. Una carpeta `.commands` en la raíz **no la lee
> nadie** — tiene que estar en `.claude/commands/`.

---

## ¿Comando o skill? La diferencia importa

| | **Comando** (`/nombre`) | **Skill** |
|---|---|---|
| Quién lo lanza | Tú, escribiendo `/nombre` | Claude solo, si la tarea encaja |
| Dónde vive | `.claude/commands/loquesea.md` | `.claude/skills/nombre/SKILL.md` |
| Para qué | Una tarea concreta que repites | Conocimiento que Claude debe aplicar cuando toque |
| Ejemplo | `/deploy-check` | "Cómo escribir copy para esta marca" |

**Regla práctica**: si sabes *cuándo* lo quieres, haz un comando. Si quieres que Claude
lo aplique sin que tengas que acordarte, haz una skill.

---

## Comandos que ya tienes

| Comando | Qué hace |
|---|---|
| `/deploy-check` | Tests + migraciones + `check --deploy` + repo limpio, con veredicto |
| `/nuevo-servicio` | Añade un servicio a `content.py` (web + formulario, sin migración) |
| `/nueva-seccion` | Añade una sección a la landing siguiendo el patrón de 5 pasos |
| `/revisar-diseno` | Verifica que un cambio de backend no tocó estilo, CSP ni `data-*` |

---

## Crear un comando

Crea `.claude/commands/mi-comando.md`. El nombre del archivo es el nombre del comando.

```markdown
---
description: Una línea que aparece en el listado de /
argument-hint: [qué se le puede pasar]
allowed-tools: Bash(git status:*), Read, Grep
---

Aquí escribes las instrucciones, como si le hablaras a Claude.

Lo que el usuario escriba tras el comando llega en $ARGUMENTS
(o $1, $2… si quieres los argumentos por separado).
```

Todo el frontmatter es opcional salvo que quieras control fino:

- **`description`** — recomendable siempre; es lo que ves al escribir `/`.
- **`argument-hint`** — pista de qué argumentos acepta.
- **`allowed-tools`** — limita qué puede hacer el comando sin pedirte permiso. Útil para
  comandos de solo lectura; omítelo si el comando necesita editar archivos.
- **`model`** — fuerza un modelo concreto (`opus`, `sonnet`, `haiku`) para ese comando.

Puedes agrupar comandos en subcarpetas: `.claude/commands/db/backup.md` → `/db:backup`.

### Consejos para que salgan bien

- Sé **específico y ordenado**: pasos numerados funcionan mejor que un párrafo.
- Di también **lo que NO debe hacer** ("no toques el CSS", "no generes migraciones sin
  permiso"). Es lo que más evita sorpresas.
- Termina pidiendo un **resumen o veredicto**: así la respuesta es accionable.
- Referencia documentación en vez de repetirla: `lee docs/despliegue.md` gasta menos
  tokens que copiar el contenido dentro del comando.

---

## Crear una skill

Una skill es una carpeta con un `SKILL.md` dentro:

```
.claude/skills/mi-skill/SKILL.md
```

```markdown
---
name: mi-skill
description: Qué hace y CUÁNDO debe usarse. Esta línea es lo único que Claude
  lee para decidir si la activa, así que sé explícito con los disparadores.
---

# Mi skill

Las instrucciones completas, que solo se cargan cuando la skill se activa.
```

La clave está en `description`: es lo único que Claude ve de entrada. Compara:

- ❌ `description: Ayuda con textos` — demasiado vago, nunca se activará bien.
- ✅ `description: Escribe o revisa copy de la landing de IAbits. Úsala cuando se pida
  redactar, reescribir o mejorar textos comerciales, titulares, descripciones de
  servicios o llamadas a la acción.`

Si la skill necesita archivos de apoyo (plantillas, ejemplos, scripts), mételos en la
misma carpeta y referéncialos desde el `SKILL.md` — se cargan solo si hacen falta.

---

## Por qué esto ahorra tokens

- **`CLAUDE.md` es corto y específico**: se carga en cada sesión, así que solo contiene
  el mapa del proyecto y las reglas que no se negocian.
- **`docs/` se lee bajo demanda**: el detalle de despliegue no ocupa contexto cuando
  estás cambiando un color.
- **Comandos y skills cargan solo al usarse**: instrucciones largas sin coste permanente.
- **`settings.json` con permisos**: menos interrupciones para aprobar comandos que
  siempre apruebas.
