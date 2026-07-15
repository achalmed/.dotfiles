# META — Sistema Operativo Personal

`meta/` es el núcleo operativo del vault. Su único objetivo: **que tu
memoria de trabajo quede libre para el contenido y la ejecución.** El
sistema captura, titula, fecha, clasifica, archiva y revisa por ti; tú
solo escribes y ejecutas.

Construido el 2026-07-06; auditado y corregido tras las primeras pruebas
reales el mismo día (v2). Lo reemplazado está en `meta/archivo/`.
Auditoría integral de automatizaciones: 2026-07-15 (ver
[Auditoría de automatizaciones](#auditoría-de-automatizaciones-2026-07-15)).

## Uso diario (esto es todo lo que hay que recordar)

| Atajo   | Qué hace                                                                                |
| ------- | --------------------------------------------------------------------------------------- |
| `Alt+C` | 📥 **Capturar**: se añade con su hora al diario `AAAA-MM-DD Capturas.md` (bandeja)      |
| `Alt+T` | ✅ Capturar tarea(s): una casilla por línea en `05 tasks/AAAA-MM-DD Tareas.md`          |
| `Alt+D` | 📅 Plan de hoy (se crea solo, con tus bloques y prioridades)                            |
| `Alt+N` | 📝 Nota tipada (idea, proyecto, paper…): título, nombre, metadata y carpeta automáticos |
| `Alt+I` | 🏠 Tablero de inicio (siguiente acción, prioridades, bandeja)                           |
| `Alt+B` | 📥 Tablero bandeja (procesar lo capturado)                                              |

Ritmo: capturar todo el día (`Alt+C`/`Alt+T`) → procesar bandeja a las
20:20 → ejecutar en Super Productivity → revisión semanal el domingo 18:00.

**Regla de oro:** clasificar durante la captura está prohibido. Las capturas
van a UN diario por día (no cientos de archivos) y las notas tipadas se
nombran solas. La organización manual del resto del vault es tuya y el
sistema debe respetarla (ver auditoría más abajo: hoy esto no se cumple del
todo — la autoorganización actúa sobre todo el vault).

## Estándar único de nombres

| Qué              | Nombre                                                                               | Dónde                           |
| ---------------- | ------------------------------------------------------------------------------------ | ------------------------------- |
| Capturas del día | `2026-07-06 Capturas.md`                                                             | `01 notes/00-bandeja`           |
| Tareas del día   | `2026-07-06 Tareas.md`                                                               | `05 tasks`                      |
| Nota tipada      | `2026-07-06 Idea - Título.md`                                                        | carpeta según tipo (automático) |
| Plan diario      | `2026-07-06.md`                                                                      | `07 diary/2026`                 |
| Revisiones       | `2026-W28 Revisión semanal.md`, `2026-07 Revisión mensual.md`, `2026-Q3 …`, `2026 …` | donde se creen                  |

Todo empieza por la fecha (o el período): ordena solo, se busca solo.

## Estructura

| Carpeta        | Propósito                                                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `sistema/`     | Documentación: arquitectura, metadata, flujo, automatizaciones, SP, mantenimiento                                                   |
| `tablero/`     | Tableros automáticos: inicio, bandeja, proyectos, ideas, fuentes, semana, mantenimiento                                             |
| `templater/`   | Plantillas: `tipos/` (27 + `_generador.py`), `planes/`, `revisiones/`, extract Zotero                                               |
| `javascript/`  | **Solo scripts de Templater** (deben exportar una función): `frontmatter.js`, `titular.js`, `encabezado.js`, `etiqueta_proyecto.js` |
| `quickadd/`    | **Solo macros de QuickAdd** (pueden exportar objetos): `captura_diaria.js`, `abrir_nota.js`, workspaces                             |
| `dataview/`    | Buscador unificado (`buscar.js`), notas de búsqueda y `vistas/` reutilizables                                                       |
| `zotero/`      | Plantilla de importación de Zotero Integration                                                                                      |
| `longform/`    | Paso de compilación de Longform                                                                                                     |
| `attachments/` | Imágenes; Zotero exporta aquí                                                                                                       |
| `templates/`   | (vacía; reservada para el plugin core Templates)                                                                                    |
| `archivo/`     | Código y plantillas reemplazados — se conserva, no se ejecuta                                                                       |

⚠️ **La separación `javascript/` vs `quickadd/` no es cosmética:** Templater
carga todos los `.js` de su carpeta de user-scripts y exige que exporten
funciones. Un script de QuickAdd (que exporta `{entry, settings}`) colocado
en `javascript/` rompe TODAS las plantillas del vault con el error
"must contain only functions".

## Funcionalidades y configuración, en detalle

Cada automatismo, con el archivo exacto que lo controla. Si algo deja de
funcionar o quieres ajustarlo, esta sección dice dónde mirar.

### Captura rápida (`Alt+C`) y captura de tareas (`Alt+T`)

- **Código:** `meta/quickadd/captura_diaria.js` (una sola macro para ambos).
- **Configuración:** `.obsidian/plugins/quickadd/data.json` — dos *choices*
  con ajustes distintos:
  - «📥 Captura rápida»: Carpeta `01 notes/00-bandeja`, Nombre `Capturas`,
    estado `bandeja`, Checklist desactivado.
  - «✅ Captura tarea»: Carpeta `05 tasks`, Nombre `Tareas`, estado
    `activo`, Checklist activado (cada línea se vuelve `- [ ]`).
- **Comportamiento:** añade `## HH:mm` + el texto al final del diario del
  día; si es la primera captura del día, crea el archivo con el frontmatter
  estándar. Nunca sobrescribe, nunca mueve, nunca pregunta nada.

### Nota tipada (`Alt+N`)

- **Plantillas:** `meta/templater/tipos/` — 27 tipos. No se editan una a
  una: se regeneran con `meta/templater/tipos/_generador.py` (editar la
  especificación ahí).
- **Scripts de usuario (Templater):**
  - `meta/javascript/titular.js` — pide el título y renombra la nota al
    estándar `AAAA-MM-DD Tipo - Título.md` (nunca queda "Untitled"; si el
    nombre choca, añade la hora). Renombra SOLO la nota recién creada.
  - `meta/javascript/frontmatter.js` — única fuente de verdad del esquema
    de metadata (`id`, `tipo`, `estado`, `creado`, `tags`, `aliases`).
- **El archivado posterior NO lo hace Templater**: lo hace Auto Note Mover
  al detectar el tag (ver más abajo).

### Plan diario (`Alt+D`)

- **Plugin Daily notes:** `.obsidian/daily-notes.json` → carpeta
  `07 diary`, formato `YYYY/YYYY-MM-DD`.
- **Plantilla automática:** `.obsidian/plugins/templater-obsidian/data.json`
  → `folder_templates: 07 diary → meta/templater/planes/plan-diario.md`,
  con `trigger_on_file_creation: true`. Ojo: cualquier archivo nuevo creado
  en `07 diary` recibe esa plantilla, no solo el del día.

### Ubicación de notas nuevas

- `.obsidian/app.json` → `newFileFolderPath: "01 notes/00-bandeja"`. Toda
  nota creada por enlace o comando nace en la bandeja. No mueve nada; solo
  decide dónde nace.

### Autoorganización (Auto Note Mover) — cómo clasifica exactamente

- **Plugin:** `.obsidian/plugins/auto-note-mover/` (v1.2.0 + parche local).
- **Configuración:** `.obsidian/plugins/auto-note-mover/data.json`.
- **Criterio de clasificación: únicamente TAGS.** No mira el nombre del
  archivo, ni el contenido, ni las propiedades `tipo:`/`estado:` del
  frontmatter. Toma todos los tags de la nota (los del frontmatter `tags:`
  **y** los `#inline` del cuerpo, vía `getAllTags`) y los compara contra 26
  reglas `tag → carpeta`. Con `use_regex_to_check_for_tags: true`, cada
  regla es una regex tipo `^#investigacion` — que también captura variantes
  como `#investigacion-x` o `#investigacionfoo`. (El plugin soporta además
  reglas por regex sobre el NOMBRE del archivo, pero ninguna está en uso:
  todas las reglas actuales tienen `pattern: ""`.)
- **Cuándo se dispara** (`main.js`, función `fileCheck`, con
  `trigger_auto_manual: "Automatic"`):
  1. al **crear** cualquier archivo (`vault.on("create")`) — incluye
     archivos generados por scripts externos dentro del vault;
  2. en **cada cambio de metadata** (`metadataCache.on("changed")`) — es
     decir, cada vez que editas y guardas una nota, se reevalúa;
  3. al **renombrar** (`vault.on("rename")`); mover un archivo sin
     cambiarle el nombre no dispara el chequeo en ese momento… pero la
     próxima edición sí (por eso una nota reubicada a mano "vuelve a
     moverse sola" horas o días después).
- **Ámbito: TODO el vault** (`~/Documents` completo — incluidos `pub_*`,
  `website-achalma`, proyectos, repos). Única exclusión configurada: la
  regex `^meta` en `excluded_folder`.
- **Mecanismos de escape integrados en el plugin:**
  - `AutoNoteMover: disable` en el frontmatter de una nota → esa nota no
    se mueve nunca.
  - `excluded_folder` (acepta regex) → carpetas enteras ignoradas.
  - `trigger_auto_manual: "Manual"` → solo mueve al invocar el comando
    *Move the note*.
- **Parche local** en `main.js` (`isFmDisable`: `if (!fileCache) return
  true;`): evita un TypeError cuando Obsidian aún no tiene cache de
  metadata del archivo (típico con archivos recién generados por procesos
  externos). **Se pierde si el plugin se actualiza** — reaplicar si
  reaparece el error.

### Tableros y vistas (Dataview)

- `meta/tablero/*` + `meta/dataview/vistas/*.js` (`bandeja`, `proyectos`,
  `salud`, `exportar-sp`, `aleatoria`) y el buscador `dataview/buscar.js`.
- **Solo lectura:** calculan y muestran; no modifican, mueven ni renombran
  ningún archivo.

### Zotero, extracciones y workspaces

- `Ctrl+R` nota de investigación (Zotero Integration, plantilla
  `meta/zotero/`); `Ctrl+Z` extraer anotación (Templater +
  `encabezado.js`); `Ctrl+T` extraer tarea bibliográfica (Templater +
  `etiqueta_proyecto.js`); `Ctrl+N/S/L` workspaces (QuickAdd +
  `workspace-load-*.js`). Crean o abren notas; no mueven las existentes.

### Revisiones periódicas

- `meta/templater/revisiones/*.md`: al insertarlas se **renombra la nota
  actual** al período (`2026-W28 Revisión semanal`, etc.) con
  `tp.file.rename`. Acción única, sobre la nota en la que las invocas.

## Auditoría de automatizaciones (2026-07-15)

Inventario completo de todo lo que actúa solo, con su nivel de riesgo para
la integridad de la organización manual del vault.

| Automatización | Archivo responsable | Función/mecanismo | Cuándo se ejecuta | Qué modifica | Riesgo |
| --- | --- | --- | --- | --- | --- |
| **Autoorganización** | `.obsidian/plugins/auto-note-mover/main.js` + `data.json` | `fileCheck()` → `fileMove()` | Al crear archivos, en cada cambio de metadata y al renombrar, en todo el vault salvo `^meta` | **MUEVE archivos** de carpeta (renameFile) | 🔴 **ALTO** |
| Renombrado de nota tipada | `meta/javascript/titular.js` | `tp.file.rename` | Solo al crear la nota con `Alt+N` | Renombra la nota recién creada | 🟢 Bajo |
| Renombrado de revisiones | `meta/templater/revisiones/*.md` | `tp.file.rename` | Solo al insertar la plantilla | Renombra la nota actual | 🟢 Bajo |
| Captura diaria | `meta/quickadd/captura_diaria.js` | `entry()` | `Alt+C` / `Alt+T` | Crea el diario del día o añade al final; nunca sobrescribe ni mueve | 🟢 Bajo |
| Plantilla de carpeta del diario | Templater `data.json` (`folder_templates`) | `trigger_on_file_creation` | Al crear CUALQUIER archivo en `07 diary` | Inserta la plantilla plan-diario en el archivo nuevo | 🟡 Medio-bajo |
| Ubicación de notas nuevas | `.obsidian/app.json` | `newFileFolderPath` | Al crear nota por enlace/comando | Solo decide dónde nace la nota | 🟢 Nulo |
| Tableros/vistas Dataview | `meta/dataview/`, `meta/tablero/` | `dv.view(...)` | Al abrir un tablero | Nada (solo lectura) | 🟢 Nulo |
| Abrir notas / workspaces | `meta/quickadd/abrir_nota.js`, `workspace-load-*.js` | macros QuickAdd | `Alt+I/B`, `Ctrl+N/S/L` | Nada (solo navegación) | 🟢 Nulo |
| Parche local del mover | `auto-note-mover/main.js` (`isFmDisable`) | guard `!fileCache` | — | — | 🟡 Mantenimiento: se pierde al actualizar el plugin |

### Diagnóstico del riesgo ALTO (autoorganización)

La única automatización peligrosa es Auto Note Mover, por la combinación de
cuatro factores de su configuración actual:

1. **Reevalúa en cada edición** (`metadataCache.on("changed")`): una nota
   que archivaste a mano en una carpeta permanente vuelve a moverse la
   próxima vez que la editas, si conserva un tag que coincide con alguna
   regla. La organización manual pierde siempre.
2. **Ámbito = todo el vault**: `~/Documents` entero es el vault, así que
   las reglas alcanzan `pub_*`, `website-achalma`, proyectos y repos. Un
   `.md` de una publicación con `tags: [investigacion]` es arrancado de su
   repo y llevado a `01 notes/10-investigacion`, rompiendo el repositorio.
3. **Archivos generados**: procesos externos (Quarto, scripts) crean `.md`
   dentro del vault; `vault.on("create")` los evalúa al instante. De ahí
   los errores («A file with the same name exists», «destination folder
   does not exist») y el TypeError de cache nula que obligó al parche.
4. **Regex abiertas**: `^#investigacion` también matchea
   `#investigacion-de-mercado`, etc. — movimientos "inexplicables".

**Mitigaciones disponibles sin tocar código** (las usa el rediseño):
`excluded_folder` con regex (lista de carpetas protegidas o whitelist por
regex negativa), `AutoNoteMover: disable` por nota, y modo `Manual`.

## Documentación

1. [[01-arquitectura]] — mapa de módulos, nombres fijos, quién mueve qué.
2. [[02-metadata]] — esquema único de Properties, catálogo de tipos, estándar de nombres.
3. [[03-flujo-gtd]] — capturar → procesar → ejecutar → revisar → archivar,
   y dónde vive cada mecanismo anti-procrastinación.
4. [[04-automatizaciones]] — cada atajo/automatismo y su archivo de config.
5. [[05-super-productivity]] — exportar tareas: copiar y pegar, sin fechas a mano.
6. [[06-mantenimiento]] — cómo ampliar el sistema sin romperlo.

## Copias de seguridad de la configuración

Cada archivo de `.obsidian/` modificado el 2026-07-06 tiene un respaldo
`*.bak-metaos` al lado (app.json, daily-notes.json, hotkeys.json y los
data.json de Templater, QuickAdd y Auto Note Mover). Para revertir un
cambio: reemplazar el archivo por su `.bak-metaos` y reiniciar Obsidian.

## Principios de diseño

> Cada vez que el usuario tiene que tomar una decisión innecesaria, el
> sistema falló. La mejor interfaz es aquella donde solo se escribe el
> contenido; todo lo demás lo hace el sistema.

Y, con el mismo peso desde la auditoría 2026-07-15:

1. **La organización manual siempre tiene prioridad** sobre cualquier
   automatización.
2. Las automatizaciones **sugieren, no imponen**.
3. Nunca mover archivos fuera de las carpetas de captura sin confirmación
   explícita o una regla claramente configurada.
4. Toda automatización se ajusta desde **archivos de configuración**, no
   editando código.
5. Reducir la carga cognitiva en la captura; aumentar la capacidad de
   revisión, planificación y ejecución después.
