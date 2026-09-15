---
tipo: doc
titulo: "Estándar de metadata del vault (Properties)"
estado: activo
---
# Estándar de metadata (Properties)

**Una sola fuente de verdad:** `meta/core/scripts/frontmatter.js`. Todas las
plantillas lo llaman; si quieres cambiar el esquema, cámbialo SOLO ahí y
todas las notas futuras lo heredan.

> **Este estándar es una instancia de `meta/NORMATIVA_ARCHIVOS.md`** (§1 claves,
> §2.1 estados, §4 nombres, §6.2 «nota del vault», §10 Obsidian). La fase **M3
> (2026-09-15)** lo aplicó a las 110 notas existentes de `01 notes`, `05 tasks`,
> `06 archives` y `07 diary` con `meta/organization/normalizar_notas.py`
> (registro en `meta/reparaciones/M3_vault_obsidian_*`).

## Esquema base (todas las notas)

```yaml
---
id: 20260706134501        # instante de creación = identificador. No se edita.
tipo: idea                # qué es la nota (catálogo abajo)
titulo: Sistema de tareas # título humano (el nombre de archivo es kebab)
estado: bandeja           # ciclo de vida universal (NORMATIVA_ARCHIVOS §2.1)
creado: 2026-07-06        # fecha de creación (la hora está en `id`). No se edita.
tags: [idea]              # la PRIMERA es el tipo; las demás, tema/<slug> o proyecto/<id>
aliases: []               # nombres alternativos (al renombrar, el nombre anterior)
AutoNoteMover: disable    # ninguna nota de plantilla se mueve sola
---
```

Las claves propias son `snake_case`, ASCII, en español (`anio`, `sueno_horas`,
`clave_bibtex`, `fecha_limite`). Las de un esquema ajeno se respetan tal cual:
`tags`, `aliases`, `cssclasses` (Obsidian), `kanban-plugin` (Kanban),
`AutoNoteMover`.

## Ciclo de vida (`estado`) — NORMATIVA_ARCHIVOS §2.1

```
bandeja → borrador → activo → hecho → archivado
                        ↕
                     en_espera                retirado (nunca vuelve)
```

| Estado | Significado |
| --- | --- |
| `bandeja` | Capturado, sin procesar. Aparece en el tablero [[bandeja]]. |
| `borrador` | En preparación, no publicable (también la sesión importada sin revisar). |
| `activo` | Vigente, en uso o en curso (proyectos, referencias, hábitos, planes y revisiones abiertos). |
| `en_espera` | Bloqueado por algo externo. Campo `esperando:` dice por qué. |
| `hecho` | Terminado. |
| `archivado` | Cerrado y conservado. No aparece en tableros. |
| `retirado` | Reemplazado o abandonado; se conserva por historia. |

Extensiones, las únicas admitidas: `tipo: tarea` puede usar `siguiente` (lista
para ejecutar, exportable a Super Productivity) y `tipo: idea|tarea` puede usar
`algun_dia` (incubando; solo reaparece en la revisión mensual). Los valores
antiguos migraron así: `espera → en_espera`, `algun-dia → algun_dia`,
`en-curso → activo`, `migrada → borrador`.

## Catálogo de tipos y sus campos extra

| `tipo` | Campos extra | Destino sugerido por `archivar.js` |
| --- | --- | --- |
| `capturas` | — | diario de capturas del día (`Alt+C`); nace en la bandeja |
| `tareas` | — | diario de tareas del día (`Alt+T`); nace en `05 tasks` |
| `idea`, `nota` | — | se quedan en la bandeja, por diseño. La plantilla `algun-dia` crea una `idea` con `estado: algun_dia` |
| `hipotesis` | — | 02 analysis |
| `investigacion` | `pregunta`, `proyecto` | 01 notes/10-investigacion |
| `proyecto` | `objetivo`, `fecha_limite`, `esperando` | 05 tasks |
| `tarea` | `proyecto`, `fecha_limite`, `sp_est` | 05 tasks |
| `persona` | `relacion`, `contacto` | 04 index |
| `libro` | `autor`, `anio`, `estado_lectura` | 01 notes/70-recursos |
| `articulo` | `autor`, `url` | 01 notes/70-recursos |
| `paper` | `autor`, `anio`, `doi`, `clave_bibtex` | 01 notes/70-recursos |
| `video` | `canal`, `url` | 01 notes/70-recursos |
| `lectura` | `calibre_id`, `zotero_key`, `clave_bibtex`, `tipo_zotero`, `autor`, `publicacion`, `publicado` | nota de Zotero Integration (`Ctrl+R`, plantilla `meta/integrations/zotero/research note.md`); nace en `01 notes` |
| `apunte` | `curso`, `institucion`, `numero`, `fecha_inicio`, `fecha_fin` | apuntes de cursos seguidos (`01 notes/40-cursos-y-formacion`, `50-examenes-y-practicas`) |
| `original` | `origen`, `convertidor`, `convertido`, `autor`, `modificado` | documento convertido por docflow (`.odt/.docx/.pdf → .md`); se queda junto a su origen |
| `clase` | `curso`, `fecha_clase` | 01 notes/20-universidad |
| `reunion` | `con`, `fecha_reunion` | 01 notes/30-trabajo-y-negocios |
| `sueno`, `reflexion` | — | 07 diary |
| `decision` | `fecha_limite` | 02 analysis |
| `problema`, `error`, `bitacora` | `proyecto` | 02 analysis |
| `experimento` | `hipotesis`, `inicio`, `fin` | 02 analysis |
| `aprendizaje` | `fuente` | 02 analysis |
| `objetivo` | `plazo`, `metrica` | 05 tasks |
| `rutina` | `horario` | 05 tasks |
| `habito` | `disparador`, `recompensa` | 05 tasks |
| `checklist` | — | 05 tasks |
| `referencia` | `url`, `fuente`; si viene de Web Clipper: `url`, `autor`, `publicado`, `descripcion` | 01 notes/60-guias-y-referencias |
| `plan-diario` | `fecha`, `dia`, `energia_*`, `sueno_horas` | 07 diary |
| `revision-*` | `semana` / `mes` / `trimestre` / `anio` | 07 diary |
| `tablero` | — (o `kanban-plugin: board` si es un Kanban) | meta/tablero y 05 tasks |

Las cinco plantillas ajenas (NORMATIVA §10.5): Zotero Integration emite este
esquema desde M3; **Web Clipper no está instalado** (es una extensión del
navegador, sin plantilla en el vault): cuando se instale, su plantilla debe
emitir `tipo: referencia` con `url`, `autor`, `publicado`, `descripcion`;
docflow (`scripts_document_studio`) sigue emitiendo `source/converter/converted`
y `normalizar_notas.py` lo migra a `origen/convertidor/convertido`; el
`index.html.md` de Quarto no se valida; el Kanban conserva `kanban-plugin`.

## Etiquetas (`tags`)

Solo en el régimen del vault. La primera es el `tipo` y la pone
`frontmatter.js`; las demás son `tema/<slug>` o `proyecto/<id>`. Nada de
etiquetas en línea de texto (`#task` en la primera línea): M3 las llevó al
frontmatter. Las de las notas antiguas (`idea`, `zotero`, `archive/moma`…) se
conservaron tal cual detrás del tipo; renombrarlas a `tema/…` es trabajo del
autor con Tag Wrangler.

## Estándar único de nombres de archivo — NORMATIVA_ARCHIVOS §4

Lo aplica `meta/core/scripts/titular.js` (notas tipadas) y
`meta/capture/captura_diaria.js` (diarios). Nunca se escribe a mano:

| Qué | Patrón | Ejemplo |
| --- | --- | --- |
| Diario de capturas | `AAAA-MM-DD-capturas` | `2026-07-06-capturas` |
| Diario de tareas | `AAAA-MM-DD-tareas` | `2026-07-06-tareas` |
| Nota tipada con título | `AAAA-MM-DD-<titulo-kebab>` | `2026-07-06-acemoglu-instituciones` |
| Nota tipada sin título | `AAAA-MM-DD-<tipo>-HHmm` | `2026-07-06-idea-0913` |
| Plan diario | `AAAA-MM-DD` | `2026-07-06` |
| Revisiones | `AAAA-Www`, `AAAA-MM`, `AAAA-Qn`, `AAAA` | `2026-W28`, `2026-07`, `2026-Q3`, `2026` |
| Nota sin fecha | `<titulo-kebab>` | `proyecto-backup-studio` |

Kebab, ASCII, minúsculas, sin espacios; el tipo va en `tipo:`, no en el nombre;
el título humano en `titulo:`. Al renombrar, el nombre anterior queda en
`aliases` y los wikilinks se reescriben (lo hace `normalizar_notas.py`).

## Reglas

1. **Nunca escribas frontmatter a mano** en una nota nueva: usa `Alt+C`
   (captura) o `Alt+N` (plantilla). El sistema lo genera.
2. **Los campos de fecha van en `AAAA-MM-DD`**; los instantes (`convertido`,
   `modificado`) solo cuando los escribe una herramienta.
3. **Un campo nuevo para un tipo** se añade en su plantilla (`extra: {...}`)
   y en `.obsidian/types.json`, no improvisado en notas sueltas.
4. **Un campo nuevo para TODAS las notas** se añade en `frontmatter.js`.
5. El tablero [[mantenimiento]] (`meta/organization/salud.js`) detecta las
   notas recientes sin `tipo`, `estado`, `id` o `creado`.
6. Fuera de Obsidian, `python3 core/archivos.py validar "01 notes"` (y las
   otras tres carpetas) es el validador; `normalizar_notas.py --aplicar`
   la herramienta de migración.
