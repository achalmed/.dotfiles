# Automatizaciones: qué está cableado y dónde

Todo lo automático del sistema, con el archivo de configuración exacto que
lo controla. Si algo deja de funcionar, esta tabla dice dónde mirar.

## Atajos de teclado (`.obsidian/hotkeys.json`)

| Atajo | Acción | Mecanismo |
| --- | --- | --- |
| `Alt+C` | 📥 Captura → diario `AAAA-MM-DD Capturas.md` (bandeja) | QuickAdd → macro `quickadd/captura_diaria.js` |
| `Alt+T` | ✅ Tarea(s) → diario `05 tasks/AAAA-MM-DD Tareas.md` | QuickAdd → misma macro, ajustes con Checklist |
| `Alt+N` | Nueva nota tipada (elige plantilla de `tipos/`) | Templater: *Create new note from template* |
| `Alt+D` | Plan de hoy (se crea solo si no existe) | Daily notes + plantilla de carpeta |
| `Alt+I` | Abrir tablero [[inicio]] | QuickAdd → macro `abrir_nota.js` |
| `Alt+B` | Abrir tablero [[bandeja]] | QuickAdd → macro `abrir_nota.js` |
| `Ctrl+R` | Crear nota de investigación desde Zotero | Zotero Integration |
| `Ctrl+Z` | Extraer anotación Zotero a nota nueva | Templater (plantilla extract) |
| `Ctrl+T` | Extraer tarea bibliográfica de la selección | Templater (plantilla extract) |
| `Ctrl+N` / `Ctrl+S` / `Ctrl+L` | Workspaces: notas / búsqueda / escritura | QuickAdd + Advanced URI |

## Cadena de automatismos por evento

**Al capturar (`Alt+C` / `Alt+T`):** `captura_diaria.js` añade la entrada
con su hora (`## HH:mm`) al final del diario del día (`… Capturas.md` en
la bandeja / `… Tareas.md` en 05 tasks). Si es la primera del día, crea el
archivo con frontmatter completo. Nunca sobrescribe; siempre añade.
Con Checklist activado (Alt+T), cada línea se vuelve `- [ ]`. Cero preguntas.

**Al crear cualquier nota nueva** (Ctrl+clic en enlace, comando "New note"):
nace en `01 notes/00-bandeja` (`app.json → newFileFolderPath`). Nada de
elegir carpeta.

**Al crear la nota diaria** (`Alt+D`): el plugin Daily notes la crea en
`07 diary/AÑO/AAAA-MM-DD.md` (`daily-notes.json → format: YYYY/YYYY-MM-DD`)
y Templater le aplica sola la plantilla `planes/plan-diario.md`
(`templater data.json → folder_templates: "07 diary"` +
`trigger_on_file_creation: true`). La fecha se lee del nombre del archivo.

**Al etiquetar una nota** (procesándola en Properties): Auto Note Mover la
lleva a su carpeta según el tag (`auto-note-mover/data.json`). `meta/` está
excluida con la regla regex `^meta`.

**Al abrir un tablero:** las vistas de `meta/dataview/vistas/` recalculan
todo (bandeja, proyectos, salud, exportación SP). No hay nada que refrescar.

## Choices de QuickAdd (`.obsidian/plugins/quickadd/data.json`)

| Choice | Script | Ajustes |
| --- | --- | --- |
| 📥 Captura rápida | `meta/quickadd/captura_diaria.js` | Carpeta `01 notes/00-bandeja`, Nombre `Capturas`, estado `bandeja` |
| ✅ Captura tarea | `meta/quickadd/captura_diaria.js` | Carpeta `05 tasks`, Nombre `Tareas`, Checklist ✔, estado `activo` |
| 🏠 Abrir inicio | `meta/quickadd/abrir_nota.js` | Ruta `meta/tablero/inicio.md` |
| 📥 Abrir bandeja | `meta/quickadd/abrir_nota.js` | Ruta `meta/tablero/bandeja.md` |
| Work with notes / Search research notes / Write with Longform | `meta/quickadd/workspace-load-*.js` | — |

⚠️ Los scripts de QuickAdd viven en `meta/quickadd/`, NUNCA en
`meta/javascript/` (carpeta de user-scripts de Templater, que exige que
todo exporte funciones). Ver [[01-arquitectura]].

## URI útiles (para lanzadores externos, Super Productivity, etc.)

Con Advanced URI puedes disparar el sistema desde FUERA de Obsidian:

- Captura global: `obsidian://advanced-uri?vault=Documents&commandid=quickadd%3Achoice%3A8a53bac6-0166-4b88-94cf-c5b499943ecf`
- Plan de hoy: `obsidian://advanced-uri?vault=Documents&daily=true`
- Tablero inicio: `obsidian://advanced-uri?vault=Documents&filepath=meta%2Ftablero%2Finicio.md`

(Asócialos a un atajo global de KDE en Preferencias → Accesos rápidos →
Comando: `xdg-open "<uri>"` para capturar sin tener Obsidian en primer plano.)

## Copias de seguridad de la configuración

Cada archivo de `.obsidian/` modificado el 2026-07-06 tiene un respaldo
`*.bak-metaos` al lado (app.json, daily-notes.json, hotkeys.json y los
data.json de Templater, QuickAdd y Auto Note Mover). Para revertir un
cambio: reemplaza el archivo por su `.bak-metaos` y reinicia Obsidian.
