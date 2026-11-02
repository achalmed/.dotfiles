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
| 2026-11-02 | **Fase 5, Dotfiles Studio en QML + Kirigami** sobre `gui-comun` 2.1 (rama `wip/2026-11-02-qml`, sin fusionar): `docs/rediseno.md` (auditoría de la GUI de Widgets, las ocho preguntas, la arquitectura de información, decisiones D1–D8); `studio/` reescrito como un espacio de trabajo con tres vistas (Paquetes: árbol paquete › archivo con filtros y la operación instalar · adoptar · eliminar que F5 simula y Ctrl+Intro aplica tras confirmar; Cambios: la tabla de git con el diff entero, confirmar por ruta tras el escáner y subir; Guía: los documentos del repo), `main.py` sin lógica, `aplicacion.py` con el registro de acciones, cinco controladores, modelos puros, `estado.py` intacto más consultas; corre con `/usr/bin/python3` (`main.py`, `main.sh instalar-studio`, el `.desktop`); `studio/tests/run.sh` | `studio/README.md`; `/usr/bin/python3 studio/main.py` |
| 2026-11-01 | Dotfiles Studio 1.0, la ventana opcional del gestor sobre `gui-comun` 1.x (Widgets): Inicio, Paquetes, Cambios, Seguridad, Sistema y Guía | `git log c79c0ee` |

## En curso

- 2026-11-02 · director: la fase 5 de Dotfiles Studio (pruebas, capturas, documentos) en la rama `wip/2026-11-02-qml`.

## Por hacer

- 2026-11-02 · dueño: **el autor** · P3, validar el studio en la sesión real (`/usr/bin/python3 studio/main.py` desde la raíz del repo, o el lanzador tras `./main.sh instalar-studio`): teclado, Wayland, una simulación y una aplicación reales, confirmar un archivo; después fusionar `wip/2026-11-02-qml` en `main`.
- 2026-11-02 · dueño: el autor · `lib/stow_ops.sh`: `_create_symlink` hace `mkdir -p` de la carpeta padre en HOME antes de mirar `DRY_RUN`, así que `--dry-run` deja carpetas vacías (`studio/tests/test_estado.py` lo marca `xfail`). Tocar `lib/` es del gestor, no de la ventana.

## Futuro

nada por ahora
