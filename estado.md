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
| 2026-11-02 | **Fase 5, Dotfiles Studio en QML + Kirigami** sobre `gui-comun` 2.1 (rama `wip/2026-11-02-qml`, sin fusionar ni empujar: la valida el autor): `docs/rediseno.md` (auditoría de la GUI de Widgets, las ocho preguntas, la arquitectura de información, decisiones D1–D8; en `borrador` hasta la P3); `studio/` reescrito como un espacio de trabajo con tres vistas (Paquetes: árbol paquete › archivo con filtros y la operación instalar · adoptar · eliminar que F5 simula y Ctrl+Intro aplica tras confirmar; Cambios: la tabla de git con el diff entero, confirmar por ruta tras el escáner y subir; Guía: los documentos del repo), `main.py` sin lógica, `aplicacion.py` con el registro de acciones, cinco controladores más `ajustes`, modelos puros, `estado.py` intacto más seis consultas; corre con `/usr/bin/python3` (`main.py`, `main.sh instalar-studio`, el `.desktop`), `gui-comun` por pip con versión fija o `GUI_COMUN_DIR`; 38 pruebas (`studio/tests/run.sh`: 37 en verde y 1 `xfail` estricta que documenta un defecto del gestor); capturas reales en Lliphi Oscuro, Claro y con la paleta (`docs/figuras/`); `CLAUDE.md`, `README.md`, `studio/README.md`, `docs/arquitectura.md` y `docs/decisiones.md` al día; nace este `estado.md`. `gui-comun` no necesitó nada (la vista de texto con resaltado queda anotada allí como candidata a 2.2) | `docs/rediseno.md`; `docs/figuras/dotfiles-studio-{oscuro,claro,paleta}.png`; `studio/README.md`; `/usr/bin/python3 studio/main.py` |
| 2026-11-01 | Dotfiles Studio 1.0, la ventana opcional del gestor sobre `gui-comun` 1.x (Widgets): Inicio, Paquetes, Cambios, Seguridad, Sistema y Guía | `git log c79c0ee` |

## En curso

nada en curso

## Por hacer

- 2026-11-02 · dueño: **el autor** · **P3, validar el studio en la sesión real** (`/usr/bin/python3 studio/main.py` desde la raíz del repo, o el lanzador del menú, ya reinstalado con el Python del sistema): teclado (Tab entre paneles, ↑ ↓ en el árbol, Ctrl+1..3, F5, Ctrl+Intro), Wayland, una simulación y una instalación reales de un paquete, confirmar un archivo con su diff, el escáner, y una ventana estrecha (la navegación se pliega y los detalles se abren como hoja con F11); después fusionar `wip/2026-11-02-qml` en `main` y pasar `docs/rediseno.md` a `hecho`.
- 2026-11-02 · dueño: el autor · `lib/stow_ops.sh`: `_create_symlink` hace `mkdir -p` de la carpeta padre en HOME antes de mirar `DRY_RUN`, así que `--dry-run` deja carpetas vacías (`studio/tests/test_estado.py` lo marca `xfail` estricto). Tocar `lib/` es del gestor, no de la ventana.
- 2026-11-02 · dueño: director · lo que quedó fuera de la ventana: el árbol de Paquetes no se ordena por cabecera (`ArbolDatos` lo tendrá cuando un studio lo pida); `main.sh actualizar` y `sync-pull` no se ofrecen (tampoco en 1.0); «Configurar atajos de teclado…» y «Configurar barras de herramientas…» no existen (como en toda la familia); el icono `security-high` de la barra no aparece con el tema de iconos Colloid oscuro (sí con Breeze y Colloid claro: es del tema); el escáner y las operaciones de Herramientas corren en el panel inferior y lo que pide `sudo` se abre en una terminal, no hay progreso por archivo.
- 2026-11-02 · dueño: director · la fase 5 sigue con Huella Studio; la vista de texto con resaltado (`studio/dotfiles_app/qml/componentes/VistaTexto.qml`, la tercera copia en la familia) sube a `gui-comun` 2.2 con él.

## Futuro

nada por ahora
