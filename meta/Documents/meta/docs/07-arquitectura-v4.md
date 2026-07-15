# Arquitectura v4: migración a organización por responsabilidad

Documento de la migración ejecutada el 2026-07-15. La v1–v3 organizaba
`meta/` por **tecnología** (`javascript/`, `quickadd/`, `dataview/`,
`templater/`); la v4 organiza por **responsabilidad** (SRP): cada carpeta
responde "¿qué problema resuelve?", y el plugin que lo implementa es un
detalle interno del módulo.

## 1. Mapa de responsabilidades (antes → después)

| Archivo (v3) | Responsabilidad | Veredicto | Destino (v4) |
| --- | --- | --- | --- |
| `javascript/frontmatter.js` | Generar metadata (servicio) | mover | `core/scripts/` |
| `javascript/titular.js` | Nombrar notas (servicio) | mover | `core/scripts/` |
| `javascript/archivar.js` | Archivado confirmado (servicio) | mover | `core/scripts/` |
| `javascript/encabezado.js` | Ayudante extracción Zotero (servicio Templater) | mover | `core/scripts/` |
| `javascript/etiqueta_proyecto.js` | Heredar tags al extraer (servicio Templater) | mover | `core/scripts/` |
| `sistema/config.json` | Configuración central | mover | `core/config/config.json` |
| `quickadd/captura_diaria.js` | Capturar | mover | `capture/` |
| `dataview/vistas/bandeja.js` | Mostrar lo capturado sin procesar | mover | `capture/` |
| `dataview/vistas/agrupar.js` | Agrupar tareas (sugerencia) | mover | `tasks/` |
| `dataview/vistas/proyectos.js` | Proyectos/siguiente acción | mover | `tasks/` |
| `dataview/vistas/salud.js` | Salud del estándar | mover | `organization/` |
| `dataview/vistas/aleatoria.js` | Resurrección de notas (revisión) | mover | `review/` |
| `dataview/buscar.js` + 6 notas | Buscar | mover | `search/` |
| `dataview/vistas/exportar-sp.js` | Exportar a Super Productivity | mover | `integrations/super-productivity/` |
| `quickadd/abrir_nota.js` | Abrir tableros | mover | `tablero/` |
| `quickadd/workspace-load-*.js`, `load-current-note.js` | Cambiar workspace | mover | `workspaces/` |
| `zotero/`, `longform/` | Integraciones externas | mover | `integrations/` |
| `templater/` (tipos/planes/revisiones/extract) | Plantillas | renombrar | `plantillas/` (ya estaba organizada por responsabilidad por dentro) |
| `sistema/*.md` | Documentación | renombrar | `docs/` |
| `tablero/`, `attachments/`, `templates/`, `archivo/` | (ya por responsabilidad) | permanecer | igual |

Ningún archivo necesitó **dividirse** (cada uno ya tenía una
responsabilidad tras la v3) ni **fusionarse**. `captura_diaria.js`
concentra captura + asistente + arrastre deliberadamente: es UNA macro de
QuickAdd configurada por choice; separar el arrastre implicaría dos
macros encadenadas en QuickAdd, más frágil que un módulo con settings.

## 2. Dependencias entre módulos

```
plantillas ─┐
capture ────┤──→ core (config + servicios tp.user.*)
tasks ──────┤
(resto) ────┘        tableros ──dv.view()──→ vistas de los módulos (composición de UI)
```

- `core/` no depende de nadie. Ningún módulo depende de otro módulo.
- Los tableros invocan vistas por ruta (`dv.view("meta/tasks/agrupar")`):
  composición declarativa, no import de código.
- No existen dependencias circulares (verificado: ningún `.js` lee
  archivos de otro módulo salvo `core/config/config.json`).

## 3. Violaciones del SRP detectadas (estado pre-v4)

1. **Organización por plugin, no por problema** — la carpeta `javascript/`
   mezclaba naming, metadata, archivado y ayudantes Zotero solo porque
   todos eran "Templater". Corregido: son *servicios* de `core/`.
2. **`dataview/vistas/` mezclaba 6 responsabilidades** (captura, tareas,
   salud, revisión, búsqueda, integración SP). Corregido: cada vista vive
   en su módulo.
3. **`quickadd/` mezclaba capturar, navegar y cambiar workspaces.**
   Corregido: `capture/`, `tablero/`, `workspaces/`.
4. **Configuración dispersa**: `sistema/config.json` (docs) + valores en
   `data.json` de plugins. Corregido a medias: lo editable propio vive en
   `core/config/`; lo que cada plugin exige en su `data.json` se queda ahí
   (restricción externa, documentada en el readme).

## 4. Nueva arquitectura

Ver el árbol completo y las reglas en [[01-arquitectura]]. Resumen:
`core/` (config + servicios) · `capture/` · `tasks/` · `organization/` ·
`search/` · `review/` · `plantillas/` · `tablero/` · `workspaces/` ·
`integrations/` · `docs/`.

**Compromisos impuestos por Obsidian** (donde la pureza cede ante la
realidad, documentados a propósito):

- Templater admite **una sola** carpeta de user-scripts → todos los
  servicios-función viven juntos en `core/scripts/` (encajan: son los
  servicios compartidos de los que todos dependen).
- Templater admite **una sola** carpeta de plantillas para el selector de
  `Alt+N` → `plantillas/` agrupa las plantillas de notas (tipos),
  planificación (planes), revisión (revisiones) e integración (extract),
  organizadas por responsabilidad en subcarpetas.
- La configuración YAML no es leíble por los plugins → `core/config/` usa
  JSON (mismo objetivo: un solo lugar, cero hardcodeo).

## 5. Plan de migración ejecutado (incremental)

- **Etapa A** — solo movimientos (`git mv`), cero cambios de contenido.
  El sistema queda "roto" únicamente entre A y B, con Obsidian cerrado.
- **Etapa B** — actualización de todas las rutas internas de `meta/`
  (dv.view, lecturas de config, generador, docs) con tabla de reemplazos
  ordenada (específico antes que genérico). Verificación automática: cero
  referencias viejas restantes.
- **Etapa C** — actualización de `.obsidian/` (Templater, QuickAdd,
  hotkeys, workspaces, Zotero, Longform) con respaldos `.bak-metaos4`,
  más notas ya generadas del vault que referenciaban rutas viejas.
- **Etapa D** — documentación (readme, 01-arquitectura, 06-mantenimiento,
  este documento).

## 6. Riesgos y estrategias aplicadas

| Riesgo | Estrategia |
| --- | --- |
| Templater deja de encontrar user-scripts/plantillas | `user_scripts_folder` y `templates_folder` actualizados en su `data.json` (+ respaldo `.bak-metaos4`) |
| Hotkeys de plantillas extract rotos (el id embebe la ruta) | ids reescritos en `hotkeys.json` |
| QuickAdd no encuentra las macros | 6 rutas reescritas en su `data.json` |
| Workspaces guardados apuntan a notas movidas | rutas reescritas en `workspaces.json` |
| Zotero/Longform pierden sus plantillas/pasos | rutas reescritas en sus `data.json` |
| Notas ya generadas con `dv.view` viejo | vault escaneado; 2 notas actualizadas |
| URIs externas (lanzadores KDE) | usan ids de choice (estables) y `meta/tablero/inicio.md` (no movido) — sin cambios |
| Symlinks de `~/Documents/meta` colgando | recreados módulo a módulo; verificado `find -xtype l` |
| Rollback | commits A/B/C separados en `~/.dotfiles` + `.bak-metaos4` en `.obsidian` |

## 7. Commits de la migración

1. `refactor(meta): v4 fase A — árbol por responsabilidad (solo movimientos)`
2. `refactor(meta): v4 fase B — rutas internas actualizadas al árbol nuevo`
3. `docs(meta): v4 fase C — documentación de la arquitectura por responsabilidad`
   (este documento + readme + 01-arquitectura + 06-mantenimiento;
   los cambios de `.obsidian/` no van en git: respaldos `.bak-metaos4`)

## Cómo ampliar sin romper la arquitectura

- ¿Nueva automatización? Pregunta primero **qué problema resuelve** y
  ponla en ese módulo (o crea uno). El plugin que la ejecute es lo de menos.
- ¿Función compartida por varias plantillas? → `core/scripts/` (debe
  exportar UNA función). ¿Macro de QuickAdd? → en su módulo, nunca en
  `core/scripts/`.
- ¿Nuevo valor ajustable? → `core/config/config.json`, jamás hardcodeado.
- Toda ruta nueva referenciada desde `.obsidian/` debe añadirse a la lista
  «Nombres que NO deben cambiarse» de [[01-arquitectura]].
