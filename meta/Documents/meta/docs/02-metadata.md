# Estándar de metadata (Properties)

**Una sola fuente de verdad:** `meta/javascript/frontmatter.js`. Todas las
plantillas lo llaman; si quieres cambiar el esquema, cámbialo SOLO ahí y
todas las notas futuras lo heredan.

## Esquema base (todas las notas)

```yaml
---
id: 20260706134501        # timestamp de creación = UUID legible. No se edita.
tipo: idea                # qué es la nota (catálogo abajo)
estado: bandeja           # dónde está en el flujo (ciclo de vida abajo)
creado: 2026-07-06T13:45  # fecha y hora de creación. No se edita.
tags: [idea]              # etiquetas; algunas disparan Auto Note Mover
aliases: []               # nombres alternativos para enlazar
---
```

## Ciclo de vida (`estado`)

```
bandeja → siguiente/activo → espera → hecho → archivado
              ↘ algun-dia ↗
```

| Estado | Significado |
| --- | --- |
| `bandeja` | Capturado, sin procesar. Aparece en el tablero [[bandeja]]. |
| `siguiente` | Tarea lista para ejecutarse (exportable a Super Productivity). |
| `activo` | En curso / vigente (proyectos, referencias, hábitos…). |
| `espera` | Bloqueado por algo externo. Campo `esperando:` dice por qué. |
| `algun-dia` | Incubando. Solo reaparece en la revisión mensual. |
| `en-curso` | Exclusivo de planes/revisiones abiertos. |
| `hecho` | Terminado. |
| `archivado` | Muerto o cerrado. Se conserva, no aparece en tableros. |

## Catálogo de tipos y sus campos extra

| `tipo` | Campos extra | Tag inicial (→ movida por ANM a) |
| --- | --- | --- |
| `capturas` | — | diario de capturas del día (`Alt+C`); nace en la bandeja, sin tags |
| `tareas` | — | diario de tareas del día (`Alt+T`); nace en `05 tasks`, sin tags |
| `idea`, `nota`, `algun-dia` | — | tipo homónimo (se quedan en la bandeja, por diseño) |
| `hipotesis` | — | `hipotesis` (→ 02 analysis) |
| `investigacion` | `pregunta`, `proyecto` | `investigacion` (→ 01 notes/10-investigacion) |
| `proyecto` | `objetivo`, `fecha_limite`, `esperando` | `project` (→ 05 tasks) |
| `tarea` | `proyecto`, `fecha_limite`, `sp_est` | `task` (→ 05 tasks) |
| `persona` | `relacion`, `contacto` | `person` (→ 04 index) |
| `libro` | `autor`, `año`, `estado_lectura` | `source` (→ 01 notes) |
| `articulo` | `autor`, `url` | `source` (→ 01 notes) |
| `paper` | `autor`, `año`, `doi`, `citekey` | `source` (→ 01 notes) |
| `video` | `canal`, `url` | `source` (→ 01 notes) |
| `clase` | `curso`, `fecha_clase` | `clase` (→ 01 notes/20-universidad) |
| `reunion` | `con`, `fecha_reunion` | `reunion` (→ 01 notes/30-trabajo-y-negocios) |
| `sueno`, `reflexion` | — | `diary` (→ 07 diary) |
| `decision` | `fecha_limite` | `decision` (→ 02 analysis) |
| `problema`, `error`, `bitacora` | `proyecto` | tipo homónimo (→ 02 analysis) |
| `experimento` | `hipotesis`, `inicio`, `fin` | `experimento` (→ 02 analysis) |
| `aprendizaje` | `fuente` | `aprendizaje` (→ 02 analysis) |
| `objetivo` | `plazo`, `metrica` | `objetivo` (→ 05 tasks) |
| `rutina` | `horario` | `rutina` (→ 05 tasks) |
| `habito` | `disparador`, `recompensa` | `habito` (→ 05 tasks) |
| `checklist` | — | `checklist` (→ 05 tasks) |
| `referencia` | `url`, `fuente` | `referencia` (→ 01 notes/60-guias-y-referencias) |
| `plan-diario` | `fecha`, `dia`, `energia_*`, `sueño_horas` | `plan` |
| `revision-*` | `semana`/`mes`/`trimestre`/`año` | `revision` |
| `tablero` | — | `tablero` (solo en meta/tablero) |

## Estándar único de nombres de archivo

Lo aplica `meta/javascript/titular.js` (notas tipadas) y
`meta/quickadd/captura_diaria.js` (diarios). Nunca se escribe a mano:

| Qué | Patrón | Ejemplo |
| --- | --- | --- |
| Diario de capturas | `AAAA-MM-DD Capturas` | `2026-07-06 Capturas` |
| Diario de tareas | `AAAA-MM-DD Tareas` | `2026-07-06 Tareas` |
| Nota tipada con título | `AAAA-MM-DD <Tipo> - <Título>` | `2026-07-06 Paper - Acemoglu instituciones` |
| Nota tipada sin título | `AAAA-MM-DD <Tipo> HHmm` | `2026-07-06 Idea 0913` |
| Plan diario | `AAAA-MM-DD` | `2026-07-06` |
| Revisiones | `<período> Revisión <alcance>` | `2026-W28 Revisión semanal`, `2026-07 Revisión mensual` |

Todo empieza por la fecha o el período: el explorador ordena solo y las
búsquedas por fecha funcionan sin metadata.

## Reglas

1. **Nunca escribas frontmatter a mano** en una nota nueva: usa `Alt+C`
   (captura) o `Alt+N` (plantilla). El sistema lo genera.
2. **Los campos de fecha van en `YYYY-MM-DD`** — Dataview los entiende así.
3. **Un campo nuevo para un tipo** se añade en su plantilla (`extra: {...}`),
   no improvisado en notas sueltas.
4. **Un campo nuevo para TODAS las notas** se añade en `frontmatter.js`.
5. El tablero [[mantenimiento]] detecta automáticamente las notas que
   rompen este estándar.
