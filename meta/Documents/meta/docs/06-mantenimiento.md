# Mantener y ampliar el sistema

> El sistema está diseñado para que ampliarlo sea barato y romperlo sea
> difícil. Antes de añadir algo, pregúntate: **¿esto quita una decisión o
> la añade?** Si la añade, no entra.

## Cómo añadir un nuevo TIPO de nota (3 pasos, ~2 minutos)

1. Añade el tipo a `meta/plantillas/tipos/_generador.py` (diccionarios
   `TIPOS` y `ETIQUETAS`) y ejecútalo (`python3 _generador.py`) — así TODAS
   las plantillas siguen saliendo del mismo molde. Para un experimento
   rápido también puedes copiar una plantilla a mano:

   ```
   <%*
   const titulo = await tp.user.titular(tp, "Receta");
   tR += tp.user.frontmatter(tp, { tipo: "receta", estado: "activo", tags: ["receta"], extra: { porciones: "" } });
   -%>
   # 🍲 <% titulo %>

   ## Ingredientes
   -
   ```

2. Documenta el tipo en la tabla de [[02-metadata]].
3. Añade el destino sugerido en `meta/core/config/config.json → destinos`
   (lo usa `archivar.js` al preguntar dónde guardar). Si además quieres que
   el tag mueva notas sueltas de la bandeja, añade la regla tag→carpeta en
   Auto Note Mover (solo actúa sobre la bandeja).

Ya aparece en `Alt+N`. No hay paso 4.

## Cómo añadir un TABLERO o una vista

- **Tablero:** nueva nota en `meta/tablero/` con frontmatter `tipo: tablero`
  y consultas Dataview. Enlázala desde `inicio.md`.
- **Vista reutilizable:** nuevo `.js` en el módulo cuya responsabilidad
  cubre (`capture/`, `tasks/`, `organization/`, `search/`, `review/`…) con
  el encabezado de comentario estándar (qué hace, parámetros, quién la usa).
  Se invoca con `await dv.view("meta/<modulo>/<nombre>", {...})`.
- **Regla:** la lógica va en el `.js` del módulo (reutilizable y con un
  solo dueño); los tableros solo la invocan. No copies código entre tableros.

## Cómo añadir una CAPTURA con atajo propio

1. Ajustes → QuickAdd → Manage Macros → nueva macro → añade el user script
   `meta/capture/captura_diaria.js` y configura sus ajustes
   (Carpeta/Nombre/Tipo/Estado/Checklist/Asistente/Arrastre).
2. Crea un choice tipo Macro que la lance y actívale el icono de rayo
   (command) para poder asignarle hotkey.
3. Ajustes → Hotkeys → busca el choice → asigna tecla.

## Cambios de esquema

- Campo nuevo en TODAS las notas → `meta/core/scripts/frontmatter.js` (una línea).
- Campo nuevo de UN tipo → su plantilla en `tipos/` (parámetro `extra`).
- Las notas viejas no se migran solas: el tablero [[mantenimiento]] las
  irá mostrando cuando les falte algo. Migra solo lo que uses.

## Mantenimiento programado (esto es TODO)

| Frecuencia | Tarea | Tiempo |
| --- | --- | --- |
| Semanal (en la revisión) | Bandeja a cero + ojear [[mantenimiento]] | 10 min |
| Mensual | Nada extra (la revisión mensual ya revisa `algun-dia`) | — |
| Anual | Checklist de limpieza de la revisión anual | 30 min |

## Si algo se rompe

0. **Error "Exported object … must contain only functions"** → hay un
   script de QuickAdd (exporta `{entry, settings}`) dentro de
   `meta/core/scripts/`, la carpeta de user-scripts de Templater. Muévelo a
   `meta/capture/` y corrige su ruta en Ajustes → QuickAdd. Este error
   rompe TODAS las plantillas mientras exista (fue la causa del fallo
   general del 2026-07-06).
1. **Un atajo no responde** → Ajustes → Hotkeys: ¿sigue asignado? ¿Obsidian
   se reinició tras el último cambio de configuración?
2. **La captura no crea notas** → Ajustes → QuickAdd → el choice existe y
   su user script apunta a `meta/core/scripts/qa_captura.js`.
3. **La nota diaria sale vacía** → Ajustes → Templater: *Trigger on new
   file creation* activado y folder template `07 diary` →
   `meta/plantillas/planes/plan-diario.md`.
4. **Un tablero muestra error** → el mensaje de Dataview dice qué vista
   falló; ábrela en `meta/search/` (cada una es pequeña y tiene
   su propósito comentado arriba).
5. **Las notas no se mueven solas** → Ajustes → Auto Note Mover: trigger
   "Automatic" y reglas tag→carpeta intactas.
6. **Revertir configuración** → restaurar el `.bak-metaos` correspondiente
   (ver [[04-automatizaciones]]) y reiniciar Obsidian.

## Buenas prácticas (las que mantienen el sistema vivo)

- Un archivo = una responsabilidad; el nombre dice qué hace.
- Todo script empieza con un comentario: qué hace, quién lo usa, si su
  nombre es fijo.
- Nada de rutas o valores mágicos repartidos: el esquema vive en
  `frontmatter.js`, las reglas de carpetas en Auto Note Mover.
- Cambios de estructura: UNO por semana como máximo (el "system tweak" de
  la revisión semanal). Rediseños grandes solo en la trimestral.
- Lo reemplazado no se borra: va a `meta/archivo/` con nota de por qué.
