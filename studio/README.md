---
tipo: readme
estado: activo
---
# studio/ — Dotfiles Studio, la ventana opcional del gestor (QML + Kirigami sobre `gui-comun` 2.x)

Un espacio de trabajo al estilo de Dolphin o Kate para lo que `main.sh` hace: **los paquetes del repo y sus enlaces
en `$HOME`**, la operación que se simula y se aplica sobre ellos, **los cambios del repo** con su diff entero y la
confirmación por ruta, y **la guía** (los documentos del repo). Es opcional: sin ella, `../main.sh` hace todo.
Diseño en `../docs/rediseno.md` (2026-11-02), el aprobado para la familia de studios con el piloto Git Studio. Sin
nombre ni logotipo dentro de la ventana; sin colores propios: el esquema, las fuentes y los iconos son los del
escritorio.

![Dotfiles Studio en Lliphi Oscuro](../docs/figuras/dotfiles-studio-oscuro.png)

| región | qué hay |
|---|---|
| menú | Archivo · Editar · Ver · Acción · Repositorio · Herramientas · Ajustes · Ayuda: todas las órdenes con sus atajos |
| barra | Ejecutar (F5: simula la operación marcada · relee git · relee el documento) · Aplicar (Ctrl+Intro: la operación tras confirmar · confirmar el archivo) · Escanear credenciales · filtro (Ctrl+F) · paneles (F9 · F11 · F4) |
| navegación (F9) | Paquetes (Todos · Piden atención · Activos, con contador) · Repositorio (Cambios sin confirmar) · Guía (Uso, Paquetes, Arquitectura, Atajos de KDE, Decisiones); Ctrl+1 · Ctrl+2 · Ctrl+3 cambian de vista |
| centro | Paquetes: el árbol paquete › archivo (Estado con color semántico y emblema; Detalle con la explicación) · Cambios: la tabla de `git status` (Archivo, Paquete, Estado, Nota) ordenable y filtrable · Guía: el documento en Markdown |
| detalles (F11) | Paquetes: Selección (el paquete o el archivo: rutas, estado, destino del enlace, híbrido) y Operación (Instalar · Adoptar · Eliminar, «Detallado», «Reemplazar los archivos reales», la orden exacta) · Cambios: Diferencia (el diff con resaltado y el mensaje del commit al pie) y Repositorio (rama, commits, subir) · Guía: Documento |
| panel inferior (F4) | Salida (lo que `main.sh` y `git` escriben, íntegro) · Registro (los eventos de la sesión) |
| barra de estado | paquetes · activos · piden atención · enlaces; tarea en curso con progreso y cancelar; rama · cambios sin confirmar · commits sin subir |
| paleta (Ctrl+Alt+I · Ctrl+K) | cualquier orden, «Paquete: <nombre>» (lo selecciona en el árbol) o «Guía: <documento>» |

Regla de todo lo que escribe: **F5 simula (`--dry-run`, al panel inferior) y Ctrl+Intro aplica tras un diálogo que
dice sobre qué paquetes, qué hace y que antes se respalda en `.backups/`**; confirmar un archivo exige su diff a la
vista y un mensaje, y corre el escáner antes (`git add -- ruta`, `git commit -- ruta`; nunca `git add .`); no hay
`sync-push`. Las operaciones de Herramientas (fuentes de usuario, dependencias, respaldo) ofrecen Simular y Aplicar en
el mismo diálogo. Lo que `main.sh` pregunta por la terminal (adoptar con un archivo en los dos lados) o pide `sudo`
(`instalar-deps`) se abre en una terminal (konsole, configurable en Ajustes).

## Uso

```bash
/usr/bin/python3 studio/main.py            # desde ~/.dotfiles; --smoke la abre y la cierra
./main.sh instalar-studio                  # el acceso directo en el menú de aplicaciones (-n simula)
/usr/bin/python3 studio/main.py --quitar-lanzador
studio/tests/run.sh                        # pruebas (sin pantalla, repo y HOME falsos)
/usr/bin/python3 studio/capturar.py salida.png --fila 2 --pestana 1 --simular   # una captura real para la documentación
```

Requisitos: el Python y el Qt del sistema (Kubuntu 26.04 o equivalente): `python3-pyside6.qtquick`,
`python3-pyside6.qtquickcontrols2`, `qml6-module-org-kde-kirigami`, `qml6-module-org-kde-kirigamiaddons-formcard`,
`qml6-module-org-kde-desktop`, `qml6-module-org-kde-syntaxhighlighting`; y `gui-comun` 2.1 o superior, **como paquete
de pip** desde su repo público con la versión fija de `dotfiles_app/__init__.py`
(`/usr/bin/python3 -m pip install --user --break-system-packages "gui-comun @ git+https://github.com/achalmed/gui-comun@v2.1.0"`)
o señalado con `GUI_COMUN_DIR=<carpeta del repo gui-comun>` para desarrollar contra una copia local. El repo no conoce
ningún espacio de trabajo: nunca busca `gui-comun` subiendo carpetas. El PySide6 de pip o de Anaconda no carga Kirigami.
Sin lo necesario, `main.py` dice qué instalar y sale con 3.

## Estructura

| carpeta / archivo | qué es |
|---|---|
| `main.py` | entrada, sin lógica; `/usr/bin/python3`; `--smoke`, `--instalar-lanzador`, `--quitar-lanzador` |
| `capturar.py` | una captura real para la documentación (esquema de color, vista, fila, pestaña, simulación, paleta) sin tocar las preferencias ni el escritorio; muestra el Registro y no la Salida (rutas de `HOME`) |
| `dotfiles_app/__init__.py` | localiza `gui_comun` (instalado o `GUI_COMUN_DIR`) y dice qué falta (`INSTALAR`) |
| `dotfiles_app/aplicacion.py` | arma la aplicación: controladores, el registro de acciones (menú, barra, menú contextual, paleta, atajos; Ejecutar y Aplicar cambian con la vista y la operación) y carga `qml/Main.qml` |
| `dotfiles_app/estado.py` | el servicio, sin Qt (lo mismo que leía la ventana de 1.x): el mapa de `config.sh` por Bash, el estado de cada archivo con la leyenda de `main.sh estado`, git, el diff entero, confirmar por ruta; y las consultas nuevas (destino del enlace, las órdenes de `main.sh`, cuándo hace falta una terminal, los documentos) |
| `dotfiles_app/controladores/` | `espacio` (vista activa, repo, barra de estado, Dolphin, terminal, portapapeles, la terminal para lo que pregunta), `paquetes` (árbol, filtros, selección, operación, simular y aplicar), `cambios` (tabla, diff, confirmar, subir), `guia`, `sistema` (escáner, fuentes, dependencias, respaldo), `ajustes`: los QObject que QML ve como `studio.<nombre>` |
| `dotfiles_app/modelos/` | funciones puras: los nodos del árbol (`paquetes.py`) y las filas de la tabla (`cambios.py`) para `ModeloArbol` y `ModeloTabla` de `gui-comun` |
| `dotfiles_app/qml/Main.qml` · `componentes/` | la ventana (`GuiComun.VentanaStudio`) y sus ranuras; la selección y la operación del paquete, la diferencia, el resumen del repositorio, el documento, la vista de texto con resaltado, los diálogos de sistema y de ajustes |
| `dotfiles_app/recursos/marca.svg` | el icono del lanzador (lo único con el acento del studio) |
| `tests/` | `run.sh`, `conftest.py` (el repo y el `HOME` falsos), el servicio, los modelos y los controladores, cada QML y `--smoke` |

## Límite honesto

- **La ventana no escribe por su cuenta**: todo es `main.sh` o `git`; un comportamiento del gestor se cambia en `lib/`,
  no aquí. `main.sh actualizar`, `sync-pull` y `sync-push` no se ofrecen (los dos últimos por diseño: se confirma por ruta).
- **`main.sh` pregunta por la terminal**: adoptar un archivo que existe en `HOME` y en el repo, e `instalar-deps`
  (`sudo`), se abren en una terminal que queda abierta al terminar; sin terminal instalada, lo dice.
- **`--dry-run` crea carpetas vacías en `HOME`** (`_create_symlink` hace `mkdir -p` antes de mirar `DRY_RUN`): es
  del gestor y está anotado en `../estado.md` para el autor; la prueba `xfail` lo vigila.
- **El árbol no se ordena por cabecera** (la tabla de Cambios sí): `ArbolDatos` lo hará cuando un studio lo pida.
- **Las traducciones no existen**: la interfaz es en español; las de Qt y Kirigami se cargan del sistema.
- Solo probado en Linux (Kubuntu 26.04, Plasma 6.6, Wayland; depende de `xdg-open` y `konsole`).
