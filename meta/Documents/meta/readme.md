# META — Sistema Operativo Personal

`meta/` es el núcleo operativo del vault. Su único objetivo: **que tu
memoria de trabajo quede libre para el contenido y la ejecución.** El
sistema captura, titula, fecha, clasifica, archiva y revisa por ti; tú
solo escribes y ejecutas.

Construido el 2026-07-06 (v2 tras las primeras pruebas reales).
**Rediseñado el 2026-07-15 (v3)** a partir de la auditoría integral (ver
[Auditoría](#auditoría-de-automatizaciones-2026-07-15)): la autoorganización
dejó de ser un clasificador global y pasó a ser un asistente que **solo
actúa sobre la bandeja, sugiere en vez de imponer y nunca toca lo que
organizaste a mano**. Lo reemplazado está en `meta/archivo/`.

## Principios de diseño (v3)

1. **La organización manual siempre tiene prioridad** sobre cualquier
   automatización.
2. Las automatizaciones **sugieren, no imponen**.
3. **Nunca mover archivos fuera de las carpetas de captura** sin
   confirmación explícita o una regla claramente configurada.
4. Toda automatización se ajusta desde **archivos de configuración**
   (`meta/core/config/config.json` y los `data.json` de `.obsidian/`), nunca
   editando código.
5. Reducir la carga cognitiva en la **captura**; aumentar la capacidad de
   **revisión, agrupación, priorización y ejecución** después.
6. Cada vez que el usuario tiene que tomar una decisión innecesaria, el
   sistema falló; cada vez que el sistema toma una decisión que era del
   usuario, falló también.

## Uso diario (esto es todo lo que hay que recordar)

| Atajo   | Qué hace                                                                                                                     |
| ------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `Alt+C` | 📥 **Capturar**: se añade con su hora al diario `AAAA-MM-DD Capturas.md` (bandeja). Cero preguntas.                            |
| `Alt+T` | ✅ Capturar tarea(s) → `05 tasks/AAAA-MM-DD Tareas.md` + asistente opcional (estado/prioridad/urgencia/tipo/relación; Esc = defecto) |
| `Alt+D` | 📅 Plan de hoy (se crea solo, con tus bloques y prioridades)                                                                   |
| `Alt+N` | 📝 Nota tipada: título, nombre y metadata automáticos + **destino confirmado** (sugiere carpeta y pregunta antes de mover)     |
| `Alt+I` | 🏠 Tablero de inicio (siguiente acción, prioridades, bandeja)                                                                  |
| `Alt+B` | 📥 Tablero bandeja (procesar lo capturado + sugerencias de agrupación)                                                         |

Ritmo (el ciclo papel bond, ahora digital): **capturar** suelto todo el día
(`Alt+C`/`Alt+T`) → **agrupar y relacionar** al procesar la bandeja a las
20:20 (`Alt+B`) → **priorizar** → **ejecutar** en Super Productivity →
revisión semanal el domingo 18:00.

**Regla de oro:** clasificar durante la captura está prohibido (el
asistente de `Alt+T` es opcional y Esc siempre significa "luego"). Y desde
la v3, la inversa también es ley: **lo que ya organizaste a mano es
intocable para el sistema.**

## Estándar único de nombres

| Qué              | Nombre                                                                               | Dónde                           |
| ---------------- | ------------------------------------------------------------------------------------ | ------------------------------- |
| Capturas del día | `2026-07-06 Capturas.md`                                                             | `01 notes/00-bandeja`           |
| Tareas del día   | `2026-07-06 Tareas.md`                                                               | `05 tasks`                      |
| Nota tipada      | `2026-07-06 Idea - Título.md`                                                        | carpeta confirmada al crearla   |
| Plan diario      | `2026-07-06.md`                                                                      | `07 diary/2026`                 |
| Revisiones       | `2026-W28 Revisión semanal.md`, `2026-07 Revisión mensual.md`, `2026-Q3 …`, `2026 …` | donde se creen                  |

Todo empieza por la fecha (o el período): ordena solo, se busca solo.

## Estructura

| Carpeta        | Propósito                                                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `sistema/`     | Documentación + **`config.json` (configuración central de v3)**                                                                     |
| `tablero/`     | Tableros automáticos: inicio, bandeja (+ agrupación), proyectos, ideas, fuentes, semana, mantenimiento                              |
| `templater/`   | Plantillas: `tipos/` (27 + `_generador.py`), `planes/`, `revisiones/`, extract Zotero                                               |
| `javascript/`  | **Solo scripts de Templater** (exportan una función): `frontmatter.js`, `titular.js`, `archivar.js`, `encabezado.js`, `etiqueta_proyecto.js` |
| `quickadd/`    | **Solo macros de QuickAdd** (pueden exportar objetos): `captura_diaria.js`, `abrir_nota.js`, workspaces                             |
| `dataview/`    | Buscador unificado (`buscar.js`), notas de búsqueda y `vistas/` (incluye `agrupar.js`)                                              |
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

## Configuración central

Cambiar el comportamiento del sistema = editar un archivo de configuración.
Nunca hay que tocar código.

| Qué configura | Archivo |
| --- | --- |
| Destinos sugeridos por tipo de nota, opciones del asistente de tareas (estados, prioridades, urgencias, tipos), arrastre de pendientes, agrupación (stopwords, umbrales) | `meta/core/config/config.json` |
| **Carpetas que la autoorganización debe ignorar** (`excluded_folder`, acepta regex) y las 26 reglas tag→carpeta | `.obsidian/plugins/auto-note-mover/data.json` |
| Ajustes de cada choice de captura (Carpeta, Nombre, Checklist, **Asistente**, **Arrastre**) | `.obsidian/plugins/quickadd/data.json` |
| Carpeta de notas nuevas, diario, hotkeys | `.obsidian/app.json`, `daily-notes.json`, `hotkeys.json` |

**Para proteger una carpeta nueva de la autoorganización:** añade
`{ "folder": "^ruta/de/la/carpeta" }` a `excluded_folder` en
`auto-note-mover/data.json`. Desde la v3 en realidad no hace falta: la
primera regla (`^(?!01 notes/00-bandeja$)`) es una **whitelist** que excluye
todo lo que no sea la bandeja; las 19 entradas siguientes (10-investigacion,
20-universidad, 30-trabajo-y-negocios, 40-cursos-y-formacion, `pub_*`,
repos, etc.) son defensa en profundidad por si algún día quitas la
whitelist.

## Funcionalidades y configuración, en detalle

### Captura rápida (`Alt+C`) y captura de tareas (`Alt+T`)

- **Código:** `meta/capture/captura_diaria.js` (una sola macro para ambos).
- **Configuración:** `.obsidian/plugins/quickadd/data.json` — dos *choices*:
  - «📥 Captura rápida»: Carpeta `01 notes/00-bandeja`, Nombre `Capturas`,
    estado `bandeja`. Sin asistente: escribir y listo.
  - «✅ Captura tarea»: Carpeta `05 tasks`, Nombre `Tareas`, estado
    `activo`, Checklist ✔, **Asistente ✔, Arrastre ✔**.
- **Comportamiento base:** añade `## HH:mm` + el texto al final del diario
  del día; si es la primera captura, crea el archivo con el frontmatter
  estándar (incluye `AutoNoteMover: disable`). Nunca sobrescribe ni mueve.
- **Asistente (solo `Alt+T`, opcional):** tras escribir aparecen selectores
  rápidos — Estado (por hacer/en progreso/en espera/bloqueada/completada),
  Prioridad (alta/media/baja), Urgencia y Tipo (idea, investigación,
  escritura, programación, universidad, trabajo, personal). **Esc en
  cualquiera = valor por defecto**: capturar nunca se vuelve lento. Se
  guardan como campos inline de Dataview: `[prioridad:: alta]`, etc.
  Opciones y valores editables en `config.json → tareas`.
- **¿Pertenece a una tarea existente?** El asistente lista las tareas
  abiertas de los últimos 14 días (`config.json → diasBusquedaRelacion`) y
  ofrece: 🆕 nueva · 📎 subtarea (se inserta sangrada bajo la elegida, en su
  archivo) · ➕ añadir detalle · 🔗 relacionar (`[rel:: …]`). Todo asistido,
  jamás se escribe un ID a mano.

### Persistencia de pendientes (arrastre)

- **Código:** dentro de `captura_diaria.js`; ajuste «Arrastre» +
  `config.json → arrastre`.
- Al crear el `Tareas.md` de un día nuevo, las `- [ ]` no completadas del
  diario anterior se copian bajo `## ⏭️ Arrastradas de <fecha>` conservando
  estado, prioridad, campos y sangría. En el archivo viejo quedan marcadas
  `- [>]` (arrastrada): **una tarea pendiente vive en un solo lugar**, sin
  duplicados en los tableros. Las completadas descansan en paz donde se
  hicieron.

### Nota tipada (`Alt+N`) con destino confirmado

- **Plantillas:** `meta/plantillas/tipos/` — 27 tipos, regeneradas con
  `_generador.py` (editar la especificación ahí, nunca una a una).
- **Scripts:** `titular.js` (título + nombre estándar), `frontmatter.js`
  (metadata única, ahora incluye `AutoNoteMover: disable` en toda nota de
  plantilla) y **`archivar.js` (nuevo, v3)**:
  1. Lee el destino sugerido del tipo en `config.json → destinos`.
  2. Pregunta: **✅ Guardar en `<sugerido>` (Enter/Esc) · 📁 Elegir otra
     carpeta… · 📥 Dejar en la bandeja**.
  3. Mueve solo con tu confirmación; y esa nota **no vuelve a moverse
     nunca** (frontmatter + whitelist).
- `idea`, `nota` y `algun-dia` sugieren quedarse en la bandeja (material
  sin procesar/incubando).

### Plan diario (`Alt+D`)

- **Plugin Daily notes:** `.obsidian/daily-notes.json` → carpeta
  `07 diary`, formato `YYYY/YYYY-MM-DD`.
- **Plantilla automática:** Templater `folder_templates: 07 diary →
  meta/plantillas/planes/plan-diario.md` con `trigger_on_file_creation:
  true`. Ojo: cualquier archivo nuevo creado en `07 diary` recibe esa
  plantilla, no solo el del día.

### Autoorganización (Auto Note Mover) — de clasificador a asistente

- **Plugin:** `.obsidian/plugins/auto-note-mover/` (v1.2.0 + parche local).
- **Criterio: únicamente TAGS** (frontmatter `tags:` + `#inline`, vía
  `getAllTags`), comparados por regex (`^#investigacion`, …) contra 26
  reglas tag→carpeta en su `data.json`. No mira nombre, contenido ni
  propiedades `tipo:`/`estado:`.
- **Disparadores:** crear archivo, cada cambio de metadata y renombrar.
- **Ámbito desde v3: SOLO `01 notes/00-bandeja`.** La whitelist
  `^(?!01 notes/00-bandeja$)` en `excluded_folder` excluye todo lo demás:
  jamás vuelve a tocar `10-investigacion`, `20-universidad`, proyectos,
  `pub_*`, repos ni nada que hayas organizado a mano. Su único trabajo
  restante: cuando proceses una nota suelta de la bandeja etiquetándola en
  Properties, llevarla a su carpeta. Eso es todo.
- **Escapes adicionales:** `AutoNoteMover: disable` por nota (toda nota
  creada por el sistema lo lleva de serie) y modo `Manual`.
- **Parche local** en `main.js` (`isFmDisable`: `if (!fileCache) return
  true;`): evita el TypeError con archivos recién generados por procesos
  externos. **Se pierde si el plugin se actualiza** — reaplicar si
  reaparece el error.
- Respaldos de su config: `data.json.bak-metaos` (original),
  `.bak-metaos2` (v2), `.bak-metaos3` (pre-v3).

### Agrupación sugerida de ideas (tablero bandeja)

- **Código:** `meta/tasks/agrupar.js`; config en
  `config.json → agrupacion`; visible en [[bandeja]].
- Analiza las tareas pendientes de los últimos 7 días, detecta palabras
  significativas compartidas (sin acentos, sin stopwords) y sugiere:
  *«Estas 4 tareas parecen del mismo tema: “latex” — ¿agruparlas?»* con
  botones **✅ Agrupar** (añade `[tema:: palabra]` a esas líneas — nada se
  mueve) · **🚫 No** (no vuelve a sugerir esa palabra) · **⏰ Más tarde**.
  **Solo sugiere; agrupar siempre es decisión tuya.**

### Tableros y vistas (Dataview)

- `meta/tablero/*` + `meta/search/*.js` (`bandeja`, `proyectos`,
  `salud`, `exportar-sp`, `aleatoria`, `agrupar`) y `buscar.js`. Solo
  lectura, salvo el botón «Agrupar» descrito arriba (acción explícita).

### Zotero, extracciones y workspaces

- `Ctrl+R` nota de investigación (Zotero Integration); `Ctrl+Z` extraer
  anotación (Templater + `encabezado.js`); `Ctrl+T` extraer tarea
  bibliográfica (`etiqueta_proyecto.js`); `Ctrl+N/S/L` workspaces
  (QuickAdd). Crean o abren notas; no mueven las existentes.

### Revisiones periódicas

- `meta/plantillas/revisiones/*.md`: al insertarlas renombran la nota
  actual al período (`2026-W28 Revisión semanal`, …). Acción única, sobre
  la nota en la que las invocas.

## Auditoría de automatizaciones (2026-07-15)

Inventario completo de todo lo que actúa solo. Columna «Riesgo»: antes →
después del rediseño v3.

| Automatización | Archivo responsable | Función/mecanismo | Cuándo se ejecuta | Qué modifica | Riesgo |
| --- | --- | --- | --- | --- | --- |
| **Autoorganización** | `auto-note-mover/main.js` + `data.json` | `fileCheck()` → `fileMove()` | Crear / cambio de metadata / renombrar | **MUEVE archivos** | 🔴 ALTO → 🟢 **contenido**: whitelist solo-bandeja + `disable` de serie |
| Archivado de nota tipada | `meta/core/scripts/archivar.js` (v3) | `tp.user.archivar` | Solo al crear con `Alt+N` | Mueve la nota recién creada **con confirmación** | 🟢 Bajo (pregunta siempre) |
| Renombrado de nota tipada | `meta/core/scripts/titular.js` | `tp.file.rename` | Solo al crear con `Alt+N` | Renombra la nota recién creada | 🟢 Bajo |
| Renombrado de revisiones | `meta/plantillas/revisiones/*.md` | `tp.file.rename` | Al insertar la plantilla | Renombra la nota actual | 🟢 Bajo |
| Captura diaria | `meta/capture/captura_diaria.js` | `entry()` | `Alt+C` / `Alt+T` | Crea/añade al diario del día; con relación asistida inserta bajo la tarea elegida | 🟢 Bajo |
| Arrastre de pendientes (v3) | `captura_diaria.js` (ajuste Arrastre) | al crear diario nuevo | Primera captura del día | Copia `- [ ]` al día nuevo y marca `- [>]` en el anterior | 🟡 Medio-bajo (solo diarios de tareas) |
| Agrupación sugerida (v3) | `meta/tasks/agrupar.js` | botón «Agrupar» | Solo clic del usuario | Añade `[tema:: …]` a líneas elegidas | 🟢 Bajo (acción explícita) |
| Plantilla de carpeta del diario | Templater `data.json` | `folder_templates` | Al crear CUALQUIER archivo en `07 diary` | Inserta plan-diario en el archivo nuevo | 🟡 Medio-bajo |
| Ubicación de notas nuevas | `.obsidian/app.json` | `newFileFolderPath` | Al crear nota por enlace/comando | Solo decide dónde nace | 🟢 Nulo |
| Tableros/vistas Dataview | `meta/search/`, `meta/tablero/` | `dv.view(...)` | Al abrir un tablero | Nada (solo lectura) | 🟢 Nulo |
| Abrir notas / workspaces | `abrir_nota.js`, `workspace-load-*.js` | macros QuickAdd | `Alt+I/B`, `Ctrl+N/S/L` | Nada | 🟢 Nulo |
| Parche local del mover | `auto-note-mover/main.js` (`isFmDisable`) | guard `!fileCache` | — | — | 🟡 Mantenimiento: se pierde al actualizar el plugin |

### Diagnóstico original (por qué era ALTO) y cómo quedó resuelto

1. **Reevaluaba en cada edición** → una nota archivada a mano volvía a
   moverse al editarla. *Resuelto:* fuera de la bandeja el plugin no puede
   actuar (whitelist), y toda nota del sistema lleva `AutoNoteMover:
   disable`.
2. **Ámbito = todo `~/Documents`** → arrancaba `.md` de `pub_*` y repos.
   *Resuelto:* whitelist + 19 carpetas protegidas explícitas.
3. **Archivos generados** (Quarto, scripts) disparaban movimientos y
   errores. *Resuelto:* sus carpetas están excluidas; el parche local cubre
   la cache nula.
4. **Regex abiertas** (`^#investigacion` matchea `#investigacion-x`).
   *Mitigado:* irrelevante fuera de la bandeja; dentro, sigue siendo el
   comportamiento deseado de procesamiento.

## Documentación

1. [[01-arquitectura]] — mapa de módulos, nombres fijos, quién mueve qué.
2. [[02-metadata]] — esquema único de Properties, catálogo de tipos, estándar de nombres.
3. [[03-flujo-gtd]] — capturar → procesar → ejecutar → revisar → archivar.
4. [[04-automatizaciones]] — cada atajo/automatismo y su archivo de config.
5. [[05-super-productivity]] — exportar tareas: copiar y pegar, sin fechas a mano.
6. [[06-mantenimiento]] — cómo ampliar el sistema sin romperlo.

## Copias de seguridad de la configuración

Cada archivo de `.obsidian/` modificado tiene respaldos al lado:
`*.bak-metaos` (original), `*.bak-metaos2` (v2) y `*.bak-metaos3`
(pre-v3: auto-note-mover y quickadd, 2026-07-15). Para revertir: reemplaza
el archivo por su respaldo y reinicia Obsidian. El código de `meta/` está
versionado en git (`~/.dotfiles`): `git log meta/` para el historial.
