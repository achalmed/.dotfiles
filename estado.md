---
tipo: estado
estado: activo
actualizado: 2026-11-18
---
# estado.md — dotfiles (repo público `achalmed/.dotfiles`)

Lo primero que se lee y lo último que se escribe en cada sesión (regla 10 de la guía raíz del espacio de trabajo).
Lo pendiente, aquí, en §Por hacer, con fecha y dueño; las decisiones abiertas del autor anteriores a esta fase siguen
en `docs/decisiones.md` §Pendientes. Nada aquí lleva rutas de máquina: el repo es público.

## Hecho

| fecha | qué | dónde se ve |
|---|---|---|
| 2026-11-19 | **Dotfiles Studio con el acabado de la familia (gui-comun 4.2)**: la página del paquete ordena sus cinco franjas en una tarjeta (la operación en un pozo con Simular y Aplicar como acción principal, qué hace, la orden como código con su botón de copiar y el plan con sus etiquetas); la pregunta del conflicto al adoptar es una fila con su elección en un pozo y las notas de la comparación, líneas tenues (no tres avisos de color); Comparación · Simulación · Detalles en un `SelectorSegmentado`; la barra lateral, los archivos del paquete y la guía con la fila elegida teñida y su marca (`FondoFila`, hasta que la base la ofrezca) y los iconos de acción del color del texto (antes, círculos de estado a todo color); el estado de cada tarjeta como `EtiquetaNivel`; la simulación de la portada plegada a una línea hasta que hay salida; Seguridad con un candado monocromo; Sistema con Simular y Aplicar del mismo ancho; **la terminal de Simulación oculta los secretos como la Comparación** (`catalogo._linea_segura`); 61 pruebas | `docs/figuras/dotfiles-studio-acabado.png`; `studio/dotfiles_app/qml/`; `studio/tests/test_modelos_controladores.py` |
| 2026-11-18 | **La terminal de simulación sobre gui-comun 4.1**: `TerminalSimulacion` pasa a ser la `TerminalSalida` de la base (que nació de ella) con las reglas de main.sh (archivo real en HOME en negativo; «[dry-run]» y las secciones en el color del texto; lo demás tenue), en el orden de antes. Sin cambio a la vista. Pide gui-comun 4.1 (`VERSION_GUI_COMUN = v4.1.0`): antes de publicar este repo, la etiqueta v4.1.0 de gui-comun tiene que estar en su remoto. 59 pruebas (1 nueva) | `studio/dotfiles_app/qml/componentes/TerminalSimulacion.qml` |
| 2026-11-18 | **Dotfiles Studio con su forma propia** (rediseño visual aprobado por el autor): cada tarjeta de paquete lleva el icono de su aplicación, el número de archivos y el estado de stow como un punto de color de estado (un conflicto, en negativo, aunque el paquete esté a medias); bajo las tarjetas, la terminal con la simulación de lo que se ve (`main.sh instalar --dry-run`, que nunca escribe; Ctrl+Mayús+Intro); en la barra lateral, los recuentos que piden algo con su color de estado. `TerminalSimulacion` sirve también a la pestaña Simulación. `ortografia` y `panel` con su aplicación e icono. Cero colores propios; los avisos sin decisión van a las notificaciones de KDE. 58 pruebas (4 nuevas; arreglada la búsqueda que «autostart» de `panel` rompía) | `docs/decisiones.md` §La ventana; `docs/reingenieria.md` §7; `docs/figuras/dotfiles-studio-oscuro.png` |
| 2026-11-15 | **`mimeapps.list` al día y sin aplicaciones desinstaladas**: KDE y Muyu habían reemplazado el enlace por un archivo real (Muyu como predeterminada de casi todo); se readoptó y se quitaron 17 referencias a 8 aplicaciones que ya no existen (Chrome, Thunderbird, GitKraken, Manuskript, Ghostwriter, Apostrophe y dos manejadores de URL); Obsidian y Claude apuntan a sus nombres actuales (`md.obsidian.Obsidian`, `com.anthropic.Claude`). `http`, `https` y `mailto` → Zen | `kde/.config/mimeapps.list`; `docs/paquetes.md` §Aplicaciones que rompen el enlace |
| 2026-11-15 | **Lanzador de DeepSeek Harness** en el paquete `kde` (`deepseek-harness.desktop` y su icono, el `favicon.svg` del propio paquete npm, MIT): abre una terminal que corre `dsh web`. En `shell`, la función `dsh` lo corre con el Node 24 más reciente de nvm (exige ≥ 24.9; el predeterminado es otro). Enlazado en esta laptop | `config.sh` (`kde`); `docs/paquetes.md` |
| 2026-11-11 | **Paquete `panel`**: la barra superior de Plasma en cada monitor. `panel-en-cada-pantalla` copia la de la pantalla principal (sus 10 widgets y su configuración, menos la nota y la bandeja interna) a cada pantalla sin barra; simula por defecto. Aplicado en esta sesión: la segunda pantalla ya tiene la barra, idéntica, y se mantiene al pasar a claro y volver a oscuro (comprobado con capturas). Enlazado por el autor el mismo día (`instalar -p panel`); la vigilancia arranca con la sesión. La barra la trae el tema de Lliphi (decisiones 5.51 de Lliphi) | `docs/paquetes.md`; `config.sh` (`panel`) |
| 2026-11-11 | **Paquete `ortografia`**: corrección en español (es-PE/es-419 con inglés) y la interfaz sigue en inglés. `Sonnet.conf` enlazado para KDE; `corrector-espanol` para Chromium, Electron y Firefox (simula, `--aplicar` con la aplicación cerrada, copia `.antes-corrector-<fecha>`); `hunspell-es` en `instalar-deps`. Aplicado en Chrome y Firefox (Snap) | `docs/paquetes.md`; `docs/decisiones.md` §Qué se versiona |
| 2026-11-03 | **Pendientes de la reingeniería** (carril A): la versión de cada conflicto al **adoptar se elige en la ventana** (sobre la comparación: la de HOME, la del repo o saltar) y `main.sh adoptar --elecciones ARCHIVO` lo hace sin terminal (opción nueva del gestor; simular dice qué se usaría); la ventana usa `VistaComparacion`, `VistaTexto` y `EtiquetaNivel` de `gui-comun` 3.1 (retiradas cuatro copias y `servicios/diferencias.py`); requiere `gui-comun` ≥ 3.1 (`v4.0.0`); 55 pruebas | `docs/reingenieria.md` §6; `tests/test_servicios.py` |
| 2026-11-02 | **Reingeniería de Dotfiles Studio** (rama `wip/2026-11-02-reingenieria`, carril A, sin fusionar ni empujar). Ahora es un gestor de paquetes de configuración al estilo de Discover sobre `gui-comun` 3.0: portada de tarjetas y página por paquete con la comparación repo ⟷ HOME, el plan por archivo y la orden exacta antes de instalar, adoptar, actualizar o quitar enlaces. Aplicar confirma con consecuencias y estado de operación, y verifica después; `actualizar` se bloquea si borraría sin respaldo. Hay estado «local». Cambios va lado a lado, con los híbridos y el filtro `clean` explicados. El escáner tiene 16 patrones con nombre más los `.env`, informa archivo, línea y tipo, nunca el valor. Sistema muestra las dependencias. `--dry-run` ya no crea carpetas (`lib/stow_ops.sh`, commit propio). 53 pruebas | `docs/reingenieria.md`; `docs/figuras/`; `studio/README.md`; `git log` |
| 2026-11-02 | El autor dio por buena la fase 5 (P3): `wip/2026-11-02-qml` fusionada en `main` y retirada; `docs/rediseno.md` a `hecho` | `git log` |
| 2026-11-02 | **Fase 5, Dotfiles Studio en QML + Kirigami** sobre `gui-comun` 2.1 (rama `wip/2026-11-02-qml`): `docs/rediseno.md` (auditoría de la GUI de Widgets, las ocho preguntas, la arquitectura de información, decisiones D1–D8; en `borrador` hasta la P3); `studio/` reescrito como un espacio de trabajo con tres vistas (Paquetes: árbol paquete › archivo con filtros y la operación instalar · adoptar · eliminar que F5 simula y Ctrl+Intro aplica tras confirmar; Cambios: la tabla de git con el diff entero, confirmar por ruta tras el escáner y subir; Guía: los documentos del repo), `main.py` sin lógica, `aplicacion.py` con el registro de acciones, cinco controladores más `ajustes`, modelos puros, `estado.py` intacto más seis consultas; corre con `/usr/bin/python3` (`main.py`, `main.sh instalar-studio`, el `.desktop`), `gui-comun` por pip con versión fija o `GUI_COMUN_DIR`; 38 pruebas (`studio/tests/run.sh`: 37 en verde y 1 `xfail` estricta que documenta un defecto del gestor); capturas reales en Lliphi Oscuro, Claro y con la paleta (`docs/figuras/`); `CLAUDE.md`, `README.md`, `studio/README.md`, `docs/arquitectura.md` y `docs/decisiones.md` al día; nace este `estado.md`. `gui-comun` no necesitó nada (la vista de texto con resaltado queda anotada allí como candidata a 2.2) | `docs/rediseno.md`; `docs/figuras/dotfiles-studio-{oscuro,claro,paleta}.png`; `studio/README.md`; `/usr/bin/python3 studio/main.py` |
| 2026-11-01 | Dotfiles Studio 1.0, la ventana opcional del gestor sobre `gui-comun` 1.x (Widgets): Inicio, Paquetes, Cambios, Seguridad, Sistema y Guía | `git log c79c0ee` |

## En curso

nada en curso

## Por hacer

- 2026-11-18 · dueño: el autor · ver la portada nueva de Dotfiles Studio en la sesión real y el cambio de claro a
  oscuro con la ventana abierta (probado aislado, con muestra y bus propio; las pestañas y los campos que pinta Kvantum
  no siguen el cambio en vivo, es del entorno).
- 2026-11-18 · dueño: director · el gestor imprime «/dev/tty: No such device or address» en cada conflicto cuando corre
  sin terminal de control (la ventana, una simulación): `_read_choice` (`lib/stow_ops.sh`) prueba `-r /dev/tty`, que
  es cierto aunque no haya terminal. Propuesta: comprobar con `{ : </dev/tty; } 2>/dev/null` antes de leer; la salida
  se ve hoy en la terminal de la portada, tenue.
- 2026-11-18 · dueño: director · las figuras de `docs/figuras/` salvo la portada (`dotfiles-studio-oscuro.png`) son
  anteriores al rediseño; la página del paquete no cambió de forma, la pestaña Simulación sí (se regeneran con
  `studio/capturar.py --muestra` cuando el autor dé el rediseño por bueno).

- 2026-11-11 · dueño: el autor · terminar la corrección en español (`hunspell-es` ya instalado): cerrar Zen y la app
  de Claude, correr `corrector-espanol --aplicar` en Konsole y volver a abrirlos; comprobar en cada uno, y en Kate,
  que «errorr» sale en rojo y «corrección» no.

- 2026-11-02 · dueño: el autor · probar Dotfiles Studio en la sesión real (Wayland) con su HOME, también elegir la versión de un conflicto al adoptar. La instalación por pip apunta a la etiqueta `v4.0.0` de `gui-comun` (la empuja el director con el resto); tras la fusión, `./main.sh instalar-studio` para el lanzador.
- 2026-11-02 · dueño: director · lo que quedó fuera de la ventana (`docs/reingenieria.md` §5): `sync-pull` y `sync-push`
  no se ofrecen, por diseño; el progreso archivo por archivo (`main.sh` no lo anuncia de forma estable); el icono
  `security-high` falta en el tema Colloid oscuro (es del tema).

## Futuro

nada por ahora
