# Arquitectura del sistema META

> Principio de diseño: **si el usuario tiene que tomar una decisión
> innecesaria, el sistema falló.** Cada pieza existe para quitar una
> decisión, no para añadir estructura.

## Mapa de módulos

```
meta/
├── readme.md          ← empieza aquí (manual de uso diario)
├── sistema/           ← esta documentación (cómo funciona y cómo ampliarlo)
├── tablero/           ← los 7 tableros automáticos (Dataview)
├── templater/         ← TODAS las plantillas
│   ├── tipos/         ← 27 tipos de nota + _generador.py (los regenera)
│   ├── planes/        ← plan-diario (se aplica solo al crear la nota diaria)
│   ├── revisiones/    ← semanal, mensual, trimestral, anual
│   └── extract *.md   ← extracción Zotero/tareas (nombres fijos, con hotkey)
├── javascript/        ← SOLO user-scripts de Templater (exportan una función)
├── quickadd/          ← SOLO macros de QuickAdd (pueden exportar objetos)
├── dataview/          ← buscador (buscar.js) y vistas reutilizables (vistas/)
├── zotero/            ← plantilla de importación de Zotero Integration
├── longform/          ← paso de compilación de Longform
├── attachments/       ← imágenes y adjuntos
├── templates/         ← (vacía; el plugin core Templates apunta aquí)
└── archivo/           ← código y plantillas reemplazados; nunca se ejecuta
```

**Regla arquitectónica crítica:** Templater carga TODOS los `.js` de
`meta/core/scripts` (incluidas subcarpetas) y exige que cada uno exporte una
función. Las macros de QuickAdd exportan objetos `{entry, settings}` —
por eso viven en `meta/capture`, fuera de su alcance. Mezclarlos produce
el error "Exported object … must contain only functions" y rompe todas
las plantillas del vault.

## Una responsabilidad por archivo (JavaScript)

| Script | Responsabilidad | Usado por |
| --- | --- | --- |
| `javascript/frontmatter.js` | **Única fuente de verdad del esquema de metadata.** | todas las plantillas |
| `javascript/titular.js` | Pedir título, aplicar el estándar de nombres, renombrar. Nunca "Untitled". | plantillas de `tipos/` |
| `javascript/archivar.js` | Sugerir carpeta destino por tipo (`sistema/config.json`) y **preguntar antes de mover**. | plantillas de `tipos/` |
| `javascript/encabezado.js` | Copiar encabezado al extraer anotación Zotero. | `Ctrl+Z` |
| `javascript/etiqueta_proyecto.js` | Heredar tags #project al extraer tarea. | `Ctrl+T` |
| `quickadd/captura_diaria.js` | Añadir capturas/tareas al diario del día (un archivo por día). | `Alt+C`, `Alt+T` |
| `quickadd/abrir_nota.js` | Abrir una nota por ruta (macro QuickAdd). | `Alt+I`, `Alt+B` |
| `quickadd/load-current-note.js`, `quickadd/workspace-load-*.js` | Cambiar de workspace. | `Ctrl+N/S/L` |
| `dataview/buscar.js` | Buscador unificado de notas. | notas de `dataview/` |
| `dataview/vistas/bandeja.js` | Qué hay sin procesar y hace cuánto. | tableros, plan diario |
| `dataview/vistas/proyectos.js` | Proyectos + siguiente acción + alertas WIP/detenidos. | tableros, revisiones |
| `dataview/vistas/salud.js` | Detectar notas que rompen el estándar. | mantenimiento |
| `dataview/vistas/exportar-sp.js` | Tareas → sintaxis de Super Productivity. | plan diario, semana |
| `dataview/vistas/aleatoria.js` | Resucitar notas antiguas al azar. | ideas |

## Nombres que NO deben cambiarse

Referenciados por ruta desde `.obsidian/` — renombrarlos rompe plugins:

- Todo `meta/capture/*.js` (`captura_diaria.js`, `abrir_nota.js`,
  `load-current-note.js`, `workspace-load-*.js`) → QuickAdd.
- `templater/extract research note from selection.md`,
  `templater/extract bibliography task from selection.md` → hotkeys de Templater.
- `templater/planes/plan-diario.md` → plantilla de carpeta de `07 diary`.
- `zotero/research note.md` → Zotero Integration.
- Las notas de `dataview/` (`Search Research Notes.md`, etc.) → workspaces.
- Las subcarpetas de `meta/` → configuración de Templater, Longform, Zotero.
- Las rutas `meta/search/*` y `meta/tablero/*` → invocadas con
  `dv.view(...)` y enlaces desde plantillas y tableros.

## Dónde viven las notas (v3: sugerido por el sistema, confirmado por el usuario)

> Desde 2026-07-15 Auto Note Mover solo actúa sobre `01 notes/00-bandeja`
> (whitelist en su `excluded_folder`). Las notas tipadas se archivan al
> crearlas vía `archivar.js`, que usa estos mismos destinos como sugerencia
> (`meta/core/config/config.json → destinos`) y siempre pregunta.

| Contenido | Carpeta | Quién lo pone ahí |
| --- | --- | --- |
| Diario de capturas (`Alt+C`) y toda nota nueva | `01 notes/00-bandeja` | `captura_diaria.js` / Obsidian (ubicación por defecto) |
| Diario de tareas (`Alt+T`) y notas `task/project/objetivo/rutina/habito/checklist` | `05 tasks` | `captura_diaria.js` / Auto Note Mover |
| Notas con tag `person/place/event/institution/work` | `04 index` | Auto Note Mover |
| Notas con tag `source` (libro, paper, artículo, video) | `01 notes` | Auto Note Mover |
| `investigacion` / `clase` / `reunion` / `referencia` | `01 notes/10-investigacion` / `20-universidad` / `30-trabajo-y-negocios` / `60-guias-y-referencias` | Auto Note Mover |
| Notas de pensamiento (`decision`, `problema`, `hipotesis`, `experimento`, `aprendizaje`, `error`, `bitacora`, tag `analysis`) | `02 analysis` | Auto Note Mover |
| Notas con tag `diary` (sueño, reflexión) | `07 diary` | Auto Note Mover |
| Notas con tag `archive` | `06 archives` | Auto Note Mover |
| Plan diario | `07 diary/AÑO/` | plugin Daily notes (formato `YYYY/YYYY-MM-DD`) |
| `idea`, `nota`, `algun-dia` | se quedan en la bandeja | (por diseño: son material sin procesar/incubando) |

`meta/` está excluida de Auto Note Mover (regla regex `^meta`) y, desde la
v3, también todo lo que no sea la bandeja (whitelist
`^(?!01 notes/00-bandeja$)`): nada ya organizado se mueve solo.
