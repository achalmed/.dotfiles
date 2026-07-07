# El flujo: capturar → procesar → ejecutar → revisar → archivar

> Obsidian es donde se PIENSA. Super Productivity es donde se EJECUTA.
> El día bueno es el que pasa más tiempo en Super Productivity.

## 1 · Capturar (todo el día, < 10 segundos)

`Alt+C` desde cualquier lugar → escribes → `Ctrl+Enter`. Ya está.

La captura se AÑADE (con su hora, `## 09:13`) al **diario de capturas del
día**: `01 notes/00-bandeja/AAAA-MM-DD Capturas.md`. Un archivo por día,
orden cronológico, nunca sobrescribe, nunca cientos de notas sueltas.
Al día siguiente el archivo nuevo se crea solo.

- Sin elegir carpeta, sin título, sin metadata (todo automático).
- Sin clasificar: **prohibido clasificar durante la captura.**

Si ya sabes que es una tarea: `Alt+T` — cada línea que escribas se añade
como casilla `- [ ]` bajo su hora en `05 tasks/AAAA-MM-DD Tareas.md`
(el diario de tareas del día).

**La regla anti-dispersión:** una idea que interrumpe tu trabajo se captura
y se abandona. Vuelves a lo que estabas haciendo. La idea te espera en la
bandeja; tu foco no vuelve solo.

## 2 · Procesar (2 momentos fijos, nunca "cuando surja")

- **20:20 diario** (bloque "Procesar bandeja", `Alt+B`) — pasada rápida.
- **Domingo 18:00** (revisión semanal) — bandeja a CERO obligatorio.

Procesar = recorrer el diario de capturas sección por sección (`## hora`)
y tomar UNA decisión por entrada (las salidas están escritas en el propio
tablero [[bandeja]]): hacer ya · `Alt+T` tarea · `Alt+N` nota propia ·
algún-día · **borrar la sección**. Si dudas más de 30 segundos, la
respuesta es `algun-dia` o borrar. Diario vacío → `estado: hecho`.

## 3 · Clarificar y organizar (los hace el sistema)

- Cambias `tipo`/`estado`/tags en Properties → Auto Note Mover archiva la
  nota en su carpeta. Tú no mueves archivos.
- Un proyecto sin "siguiente acción" definida es un proyecto bloqueado:
  el tablero [[proyectos]] lo marca 🚫 automáticamente.

## 4 · Ejecutar (Super Productivity)

1. Por la mañana: `Alt+D` abre el plan de hoy (se crea solo con plantilla).
2. Escribes las **3 prioridades** (checkboxes).
3. El bloque "📤 Exportar" del plan las convierte a sintaxis de Super
   Productivity → copiar → pegar en *Add task*. Sin configurar fechas a mano.
4. Cierras Obsidian (o lo minimizas) y trabajas desde Super Productivity,
   **una tarea visible a la vez**.

## 5 · Revisar (calendario fijo, duración con tope)

| Ritual | Cuándo | Tope | Plantilla |
| --- | --- | --- | --- |
| Cierre del día | 21:00 | 10 min | dentro del plan diario |
| Revisión semanal (incluye plan de la semana) | Dom 18:00 | 40 min | `revisiones/revision-semanal` |
| Revisión mensual (incluye plan del mes) | último domingo | 45 min | `revisiones/revision-mensual` |
| Revisión trimestral | fin de trimestre | una tarde | `revisiones/revision-trimestral` |
| Revisión anual (incluye plan del año) | última semana de dic. | un día | `revisiones/revision-anual` |

Plan y revisión son UN ritual, no dos documentos: cada revisión termina
eligiendo el foco del período siguiente.

## 6 · Archivar

`estado: archivado` (y tag `archive` si quieres que se mueva a
`06 archives`). Nada se borra del historial, pero nada muerto aparece en
los tableros.

## Mecanismos anti-procrastinación (dónde están)

| Problema | Mecanismo | Dónde |
| --- | --- | --- |
| Sobre-planificar | Topes de tiempo escritos en cada plantilla; el plan diario son 3 checkboxes | planes/revisiones |
| No saber qué hacer | "Siguiente acción por proyecto" es lo PRIMERO del tablero | [[inicio]] |
| Parálisis para empezar | "Tareas rápidas" (≤ 15 min) listadas para arrancar | [[inicio]] |
| Demasiados frentes | Alerta WIP si hay > 3 proyectos activos | [[proyectos]] |
| Proyectos zombis | Marca 😴 a los 14 días sin tocar; 🚫 sin siguiente acción | [[proyectos]] |
| Ideas que interrumpen | Captura `Alt+C` y regreso inmediato al trabajo | QuickAdd |
| Organizar como refugio | Nada que organizar: carpetas automáticas, metadata automática | todo el sistema |
| Ideas que se pudren | Bandeja con edad en rojo + resurrección aleatoria | [[bandeja]], [[ideas]] |
