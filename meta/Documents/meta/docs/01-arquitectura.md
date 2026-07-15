# Arquitectura del sistema META (v4: por responsabilidad)

> Principio de diseño: **si el usuario tiene que tomar una decisión
> innecesaria, el sistema falló.** Cada pieza existe para quitar una
> decisión, no para añadir estructura.
>
> Principio arquitectónico (v4, SRP): **cada módulo responde a UNA
> pregunta — "¿qué problema resuelve?" — nunca "¿con qué plugin está
> hecho?"**. La tecnología es un detalle interno de cada módulo.
> Historia completa de la migración: [[07-arquitectura-v4]].

## Mapa de módulos

```
meta/
├── readme.md            ← empieza aquí (manual de uso diario)
├── core/                ← lo ÚNICO de lo que pueden depender los demás módulos
│   ├── config/          ← config.json: toda la configuración editable
│   └── scripts/         ← servicios compartidos (user-scripts de Templater;
│                           cada .js exporta UNA función)
├── capture/             ← capturar (macro Alt+C/Alt+T + vista bandeja)
├── tasks/               ← tareas: agrupación sugerida, proyectos/siguiente acción
├── organization/        ← salud del estándar (el motor de movimiento es el
│                           plugin Auto Note Mover + core/scripts/archivar.js)
├── search/              ← buscador y notas de búsqueda
├── review/              ← revisión: resurrección de notas antiguas
├── plantillas/          ← TODAS las plantillas (única carpeta que Templater admite)
│   ├── tipos/           ← 27 tipos de nota + _generador.py (los regenera)
│   ├── planes/          ← plan-diario (se aplica solo al crear la nota diaria)
│   ├── revisiones/      ← semanal, mensual, trimestral, anual
│   └── extract *.md     ← extracción Zotero/tareas (nombres fijos, con hotkey)
├── tablero/             ← dashboards (inicio, bandeja, …) + abrir_nota.js
├── workspaces/          ← cambio de espacios de trabajo
├── integrations/        ← zotero/, longform/, super-productivity/
├── docs/                ← esta documentación (01–07)
├── attachments/         ← imágenes y adjuntos
├── templates/           ← (vacía; el plugin core Templates apunta aquí)
└── archivo/             ← código y plantillas reemplazados; nunca se ejecuta
```

**Regla de dependencias:** los módulos solo pueden depender de `core/`
(leer `core/config/config.json`, llamar servicios `tp.user.*` de
`core/scripts/`). Nunca de otro módulo al mismo nivel. Los tableros
*invocan* vistas de otros módulos con `dv.view(...)` — eso es composición
de UI, no dependencia de código.

**Regla técnica crítica (restricción de Templater):** Templater tiene UNA
carpeta de user-scripts (`core/scripts/`) y carga todos sus `.js`
exigiendo que cada uno exporte una función; y UNA carpeta de plantillas
(`plantillas/`) para el selector de `Alt+N`. Por eso los servicios y las
plantillas se agrupan ahí aunque sirvan a varios módulos. Las macros de
QuickAdd (exportan objetos `{entry, settings}`) viven en su módulo de
responsabilidad — **jamás en `core/scripts/`**: una macro ahí rompe TODAS
las plantillas ("must contain only functions").

## Una responsabilidad por archivo

| Archivo | Responsabilidad | Usado por |
| --- | --- | --- |
| `core/config/config.json` | **Única configuración editable** (destinos, tareas, arrastre, agrupación). | archivar, captura_diaria, agrupar |
| `core/scripts/frontmatter.js` | **Única fuente de verdad del esquema de metadata.** | todas las plantillas |
| `core/scripts/titular.js` | Pedir título, aplicar el estándar de nombres, renombrar. Nunca "Untitled". | plantillas de `tipos/` |
| `core/scripts/archivar.js` | Sugerir carpeta destino por tipo y **preguntar antes de mover**. | plantillas de `tipos/` |
| `core/scripts/encabezado.js` | Copiar encabezado al extraer anotación Zotero. | `Ctrl+Z` |
| `core/scripts/etiqueta_proyecto.js` | Heredar tags #project al extraer tarea. | `Ctrl+T` |
| `capture/captura_diaria.js` | Capturas/tareas al diario del día (+ asistente y arrastre). | `Alt+C`, `Alt+T` |
| `capture/bandeja.js` | Qué hay sin procesar y hace cuánto. | tableros, plan diario |
| `tasks/agrupar.js` | Sugerir agrupación de tareas por tema (nunca actúa sola). | tablero bandeja |
| `tasks/proyectos.js` | Proyectos + siguiente acción + alertas WIP/detenidos. | tableros, revisiones |
| `organization/salud.js` | Detectar notas que rompen el estándar. | mantenimiento |
| `search/buscar.js` | Buscador unificado de notas. | notas de `search/` |
| `review/aleatoria.js` | Resucitar notas antiguas al azar. | ideas |
| `integrations/super-productivity/exportar-sp.js` | Tareas → sintaxis de Super Productivity. | plan diario, semana |
| `tablero/abrir_nota.js` | Abrir una nota por ruta (macro QuickAdd). | `Alt+I`, `Alt+B` |
| `workspaces/*.js` | Cambiar de workspace. | `Ctrl+N/S/L` |
| `integrations/longform/re-index-footnotes.js` | Paso de compilación de Longform. | Longform |

## Nombres que NO deben cambiarse

Referenciados por ruta desde `.obsidian/` — renombrarlos rompe plugins:

- `capture/captura_diaria.js`, `tablero/abrir_nota.js`,
  `workspaces/*.js` → QuickAdd (`quickadd/data.json`).
- `core/scripts/` (carpeta) → Templater `user_scripts_folder`.
- `plantillas/` (carpeta) y `plantillas/extract *.md` → Templater
  (`templates_folder` + hotkeys con ruta embebida en `hotkeys.json`).
- `plantillas/planes/plan-diario.md` → plantilla de carpeta de `07 diary`.
- `integrations/zotero/research note.md` → Zotero Integration.
- Las notas de `search/` (`Search Research Notes.md`, etc.) →
  `workspaces.json`.
- `integrations/longform/` → Longform (`longform/data.json`).
- Las rutas invocadas con `dv.view(...)` desde plantillas y tableros
  (`meta/capture/bandeja`, `meta/tasks/*`, `meta/organization/salud`,
  `meta/review/aleatoria`, `meta/integrations/super-productivity/exportar-sp`).
- `meta/tablero/inicio.md` → URIs externas (lanzadores KDE).

## Dónde viven las notas (v3: sugerido por el sistema, confirmado por el usuario)

> Desde 2026-07-15 Auto Note Mover solo actúa sobre `01 notes/00-bandeja`
> (whitelist en su `excluded_folder`). Las notas tipadas se archivan al
> crearlas vía `archivar.js`, que usa estos mismos destinos como sugerencia
> (`meta/core/config/config.json → destinos`) y siempre pregunta.

| Contenido | Carpeta | Quién lo pone ahí |
| --- | --- | --- |
| Diario de capturas (`Alt+C`) y toda nota nueva | `01 notes/00-bandeja` | `captura_diaria.js` / Obsidian (ubicación por defecto) |
| Diario de tareas (`Alt+T`) y notas `task/project/objetivo/rutina/habito/checklist` | `05 tasks` | `captura_diaria.js` / archivar.js |
| Notas con tag `person/place/event/institution/work` | `04 index` | archivar.js / Auto Note Mover (solo bandeja) |
| Notas `libro/paper/articulo/video` | `01 notes/70-recursos` | archivar.js |
| `investigacion` / `clase` / `reunion` / `referencia` | `01 notes/10-investigacion` / `20-universidad` / `30-trabajo-y-negocios` / `60-guias-y-referencias` | archivar.js / Auto Note Mover (solo bandeja) |
| Notas de pensamiento (`decision`, `problema`, `hipotesis`, `experimento`, `aprendizaje`, `error`, `bitacora`) | `02 analysis` | archivar.js / Auto Note Mover (solo bandeja) |
| Notas con tag `diary` (sueño, reflexión) | `07 diary` | archivar.js / Auto Note Mover (solo bandeja) |
| Notas con tag `archive` | `06 archives` | Auto Note Mover (solo bandeja) |
| Plan diario | `07 diary/AÑO/` | plugin Daily notes (formato `YYYY/YYYY-MM-DD`) |
| `idea`, `nota`, `algun-dia` | se quedan en la bandeja | (por diseño: material sin procesar/incubando) |

`meta/` está excluida de Auto Note Mover (regla regex `^meta`) y, desde la
v3, también todo lo que no sea la bandeja (whitelist
`^(?!01 notes/00-bandeja$)`): nada ya organizado se mueve solo.
