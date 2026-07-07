# Integración con Super Productivity

**División de trabajo:** Obsidian piensa (capturar, clarificar, decidir);
Super Productivity ejecuta (una tarea visible, temporizador, registro).
Nunca al revés: no ejecutes desde Obsidian ni pienses en SP.

## El flujo de exportación (copiar y pegar, sin configurar fechas)

1. `Alt+D` → plan de hoy → escribe las 3 prioridades como checkboxes.
2. El bloque **📤 Exportar a Super Productivity** del propio plan las
   convierte automáticamente en líneas de sintaxis corta de SP.
3. Botón 📋 del bloque de código → pegar en la barra *Add task* de SP,
   una línea por tarea (Enter entre cada una).

Para el resto de lo accionable, el mismo exportador vive en el tablero
[[semana]] y reúne: (a) las casillas pendientes de los **diarios de
tareas** (`05 tasks/AAAA-MM-DD Tareas.md`, creados con `Alt+T`) y (b) las
notas `tipo: tarea` con `estado: siguiente/activo`, usando sus campos:
`proyecto` → `+proyecto`, `sp_est` → estimación, `fecha_limite` → `@fecha`.

## Formato generado (estable, apto para regex)

```
<texto de la tarea> +<proyecto> #<tag> <estimado> @<AAAA-MM-DD>
```

Ejemplos:

```
Preparar clase de microeconomía +docencia 45m @2026-07-08
Leer paper de Acemoglu #lectura 30m
Corregir exámenes +universidad 1h
```

Reglas del formato (por si quieres procesarlo con regex o scripts):

- Una línea = una tarea. Sin viñetas, sin checkbox.
- Los `[[enlaces]]` se convierten a texto plano.
- Campos opcionales siempre en el mismo orden: `+proyecto`, tags `#x`
  (van dentro del texto si los escribiste), estimado (`30m`, `1h`),
  `@fecha` al final.
- Los espacios del nombre de proyecto se convierten a guiones.

## Qué interpreta Super Productivity al pegar

En la barra *Add task* de SP: `#etiqueta` crea/asigna tag, `+proyecto`
asigna proyecto, `30m`/`1h` fija la estimación y `@...` agenda la tarea.
Así "exportar" = pegar; las fechas ya van escritas.

## Piezas relacionadas

- `05 tasks/` guarda datos vivos de SP (`sync-data.json`, `__meta_`):
  **no tocar, no mover** (regla heredada, sigue vigente).
- El plugin `super-productivity-provider` está instalado pero desactivado.
  Si algún día quieres sincronización bidireccional automática (en vez de
  copiar/pegar), actívalo en Ajustes → Community plugins; ya tiene puerto
  (27124) y API key configurados. El flujo de copiar/pegar no lo necesita.
- Las notas con tag `task` se archivan solas en `05 tasks` (Auto Note
  Mover), así todo lo accionable queda en un solo lugar.
