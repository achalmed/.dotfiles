---
tipo: estado
estado: activo
actualizado: 2026-11-02
---
# estado.md — dotfiles (repo público `achalmed/.dotfiles`)

Lo primero que se lee y lo último que se escribe en cada sesión (regla 10 de la guía raíz del espacio de trabajo).
Lo pendiente, aquí, en §Por hacer, con fecha y dueño; las decisiones abiertas del autor anteriores a esta fase siguen
en `docs/decisiones.md` §Pendientes. Nada aquí lleva rutas de máquina: el repo es público.

## Hecho

| fecha | qué | dónde se ve |
|---|---|---|
| 2026-11-02 | **Reingeniería de Dotfiles Studio** (rama `wip/2026-11-02-reingenieria`, carril A, sin fusionar ni empujar). Ahora es un gestor de paquetes de configuración al estilo de Discover sobre `gui-comun` 3.0: portada de tarjetas y página por paquete con la comparación repo ⟷ HOME, el plan por archivo y la orden exacta antes de instalar, adoptar, actualizar o quitar enlaces. Aplicar confirma con consecuencias y estado de operación, y verifica después; `actualizar` se bloquea si borraría sin respaldo. Hay estado «local». Cambios va lado a lado, con los híbridos y el filtro `clean` explicados. El escáner tiene 16 patrones con nombre más los `.env`, informa archivo, línea y tipo, nunca el valor. Sistema muestra las dependencias. `--dry-run` ya no crea carpetas (`lib/stow_ops.sh`, commit propio). 53 pruebas | `docs/reingenieria.md`; `docs/figuras/`; `studio/README.md`; `git log` |
| 2026-11-02 | El autor dio por buena la fase 5 (P3): `wip/2026-11-02-qml` fusionada en `main` y retirada; `docs/rediseno.md` a `hecho` | `git log` |
| 2026-11-02 | **Fase 5, Dotfiles Studio en QML + Kirigami** sobre `gui-comun` 2.1 (rama `wip/2026-11-02-qml`): `docs/rediseno.md` (auditoría de la GUI de Widgets, las ocho preguntas, la arquitectura de información, decisiones D1–D8; en `borrador` hasta la P3); `studio/` reescrito como un espacio de trabajo con tres vistas (Paquetes: árbol paquete › archivo con filtros y la operación instalar · adoptar · eliminar que F5 simula y Ctrl+Intro aplica tras confirmar; Cambios: la tabla de git con el diff entero, confirmar por ruta tras el escáner y subir; Guía: los documentos del repo), `main.py` sin lógica, `aplicacion.py` con el registro de acciones, cinco controladores más `ajustes`, modelos puros, `estado.py` intacto más seis consultas; corre con `/usr/bin/python3` (`main.py`, `main.sh instalar-studio`, el `.desktop`), `gui-comun` por pip con versión fija o `GUI_COMUN_DIR`; 38 pruebas (`studio/tests/run.sh`: 37 en verde y 1 `xfail` estricta que documenta un defecto del gestor); capturas reales en Lliphi Oscuro, Claro y con la paleta (`docs/figuras/`); `CLAUDE.md`, `README.md`, `studio/README.md`, `docs/arquitectura.md` y `docs/decisiones.md` al día; nace este `estado.md`. `gui-comun` no necesitó nada (la vista de texto con resaltado queda anotada allí como candidata a 2.2) | `docs/rediseno.md`; `docs/figuras/dotfiles-studio-{oscuro,claro,paleta}.png`; `studio/README.md`; `/usr/bin/python3 studio/main.py` |
| 2026-11-01 | Dotfiles Studio 1.0, la ventana opcional del gestor sobre `gui-comun` 1.x (Widgets): Inicio, Paquetes, Cambios, Seguridad, Sistema y Guía | `git log c79c0ee` |

## En curso

nada en curso

## Por hacer

- 2026-11-02 · dueño: el autor · probar Dotfiles Studio 3.0 en la sesión real (Wayland) y, si sirve, fusionar `wip/2026-11-02-reingenieria`. Antes hay que subir la etiqueta `v3.0.0` de `gui-comun`, a la que apunta la instalación por pip. Al ser una fusión, instalar de nuevo el lanzador.
- 2026-11-02 · dueño: director · lo que quedó fuera de la ventana:
  - `sync-pull` y `sync-push` no se ofrecen, por diseño;
  - elegir la versión de un conflicto archivo por archivo desde la ventana necesitaría que `main.sh` aceptara la elección por argumento (hoy pregunta por la terminal);
  - el icono `security-high` no aparece con el tema de iconos Colloid oscuro (sí con Breeze y Colloid claro: es del tema);
  - no hay progreso por archivo.
- 2026-11-02 · dueño: director · para promover a `gui-comun`: `VistaDiferencia` (ya la segunda copia, de Git Studio) y la vista de texto con resaltado (`VistaTexto.qml`, la tercera copia en la familia); `EtiquetaEstado` (la etiqueta de estado semántica).

## Futuro

nada por ahora
