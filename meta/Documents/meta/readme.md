# META — Sistema Operativo Personal

`meta/` es el núcleo operativo del vault. Su único objetivo: **que tu
memoria de trabajo quede libre para el contenido y la ejecución.** El
sistema captura, titula, fecha, clasifica, archiva y revisa por ti; tú
solo escribes y ejecutas.

Construido el 2026-07-06; auditado y corregido tras las primeras pruebas
reales el mismo día (v2). Lo reemplazado está en `meta/archivo/`.

## Uso diario (esto es todo lo que hay que recordar)

| Atajo   | Qué hace                                                                                |
| ------- | --------------------------------------------------------------------------------------- |
| `Alt+C` | 📥 **Capturar**: se añade con su hora al diario `AAAA-MM-DD Capturas.md` (bandeja)      |
| `Alt+T` | ✅ Capturar tarea(s): una casilla por línea en `05 tasks/AAAA-MM-DD Tareas.md`          |
| `Alt+D` | 📅 Plan de hoy (se crea solo, con tus bloques y prioridades)                            |
| `Alt+N` | 📝 Nota tipada (idea, proyecto, paper…): título, nombre, metadata y carpeta automáticos |
| `Alt+I` | 🏠 Tablero de inicio (siguiente acción, prioridades, bandeja)                           |
| `Alt+B` | 📥 Tablero bandeja (procesar lo capturado)                                              |
|         |                                                                                         |

Ritmo: capturar todo el día (`Alt+C`/`Alt+T`) → procesar bandeja a las
20:20 → ejecutar en Super Productivity → revisión semanal el domingo 18:00.

**Regla de oro:** clasificar durante la captura está prohibido, y organizar
a mano no hace falta nunca: las capturas van a UN diario por día (no cientos
de archivos), y las notas tipadas se nombran y archivan solas.

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

## Documentación

1. [[01-arquitectura]] — mapa de módulos, nombres fijos, quién mueve qué.
2. [[02-metadata]] — esquema único de Properties, catálogo de tipos, estándar de nombres.
3. [[03-flujo-gtd]] — capturar → procesar → ejecutar → revisar → archivar,
   y dónde vive cada mecanismo anti-procrastinación.
4. [[04-automatizaciones]] — cada atajo/automatismo y su archivo de config.
5. [[05-super-productivity]] — exportar tareas: copiar y pegar, sin fechas a mano.
6. [[06-mantenimiento]] — cómo ampliar el sistema sin romperlo.

## Principio de diseño

> Cada vez que el usuario tiene que tomar una decisión innecesaria, el
> sistema falló. La mejor interfaz es aquella donde solo se escribe el
> contenido; todo lo demás lo hace el sistema.
