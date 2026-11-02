---
tipo: guia_ia
estado: activo
---
# CLAUDE.md — dotfiles

Guía para el asistente. En español, como todo el ecosistema. `AGENTS.md` es un enlace a este archivo.
Léase antes: `README.md` (uso), `docs/README.md` (índice) y `config.sh` (el manifiesto: paquetes y mapa de archivos).

## Reglas que no se negocian

- **Repo público.** Nada de rutas `/home/<usuario>`, nombres de carpetas privadas del espacio de
  trabajo, datos de clientes o de alumnos, ni secretos, ni en documentos ni en lo que se confirma.
  Antes de confirmar un archivo de un paquete, se lee su diff entero: el escáner solo ve
  credenciales `clave=valor`, no rutas ni nombres en una lista de recientes.
- **Mínima captura.** Solo personalización hecha a mano; nunca caché, historial, recientes,
  geometría, estado de sesión, bases de datos, identificadores de máquina ni credenciales
  (criterio en `docs/paquetes.md`). Un archivo excluido deliberadamente no se vuelve a adoptar.
- **El mapa es explícito.** `STOW_PACKAGES` y `PACKAGE_FILES` en `config.sh` deciden qué se
  enlaza; un cambio de layout en `$HOME` se refleja ahí en el mismo commit.
- **Sin stow obligatorio.** Los enlaces se crean con `ln -sfn` según el mapa; el layout sigue
  compatible con stow. No reintroducir la dependencia.
- **No depender de `~/Documents`.** El repo se instala antes que el espacio de trabajo; no se
  importa nada de allí (el registro y los respaldos de `lib/` son duplicados deliberados).
- **No usar `sync-push` con diferencias retenidas**: confirma con `git add .`. Se confirma por
  ruta (`git add -- <ruta>`), por paquete, con mensaje en español.
- **No ejecutar** `instalar`, `adoptar`, `eliminar` ni `sync-*` sin que el autor lo pida; para
  comprobar, `--dry-run`.
- **Dónde va cada cosa nueva.** En la raíz solo `README.md`, `CLAUDE.md`, `AGENTS.md`, `estado.md`, `main.sh`,
  `config.sh`, `.gitignore` y `LICENSE`. **Nunca un `.md` dentro de un
  directorio de paquete**: `stow <paquete>` lo enlazaría a `$HOME`.

  | lo que apareció | va a | nunca a |
  |---|---|---|
  | cómo se instala o se usa | `README.md` §Uso | un `GUIA_RAPIDA.md` |
  | qué cubre un paquete, una exclusión, cómo se añade uno | `docs/paquetes.md` | un README dentro del paquete |
  | cómo funciona el gestor, quién consume el repo | `docs/arquitectura.md` | un `ARQUITECTURA_NUEVA.md` |
  | atajos de KDE | `docs/atajos-kde.md` | `kde/` |
  | por qué se decidió algo | `docs/decisiones.md` | un `DECISION_<fecha>.md` |
  | un pendiente | `estado.md` §Por hacer, con fecha y dueño (las decisiones abiertas del autor anteriores a 2026-11-02 siguen en `docs/decisiones.md` §Pendientes) | un `TODO.md` |
  | el diseño de la ventana | `docs/rediseno.md` | un `DISENO.md` |
  | una regla para el asistente | este archivo, si es transversal y estable | un segundo archivo de instrucciones |

  Lo que hiciste en esta sesión va al mensaje de commit, no a un archivo. Si nada encaja,
  pregunta antes de crear un documento. `estado.md` es lo primero que se lee y lo último que se escribe.
- **La ventana (`studio/`) es opcional y no conoce `~/Documents`.** Corre con el Python del sistema
  (`/usr/bin/python3`: su Qt es el que trae Kirigami) y encuentra `gui-comun` instalado con pip (versión fija en
  `studio/dotfiles_app/__init__.py`) o por la variable explícita `GUI_COMUN_DIR`; nunca subiendo carpetas. No
  escribe por su cuenta: toda orden es `main.sh` o `git`; F5 simula, Ctrl+Intro aplica tras confirmar; confirmar es
  por ruta. Diseño en `docs/rediseno.md`; nada de `gui_comun.widgets` (congelado), QtWidgets, colores propios ni
  nombre o logotipo dentro de la ventana.

## Cómo se verifica un cambio

```bash
bash -n main.sh config.sh lib/*.sh                 # sintaxis de cada script tocado
./main.sh instalar --dry-run -p <paquete>          # el mapa describe el disco (no escribe enlaces)
./main.sh seguridad                                # credenciales en lo versionado
python3 ~/Documents/core/archivos.py validar ~/.dotfiles   # normativa documental del ecosistema
python3 ~/Documents/core/docs.py indice ~/.dotfiles --aplicar   # índice de docs/ tras tocar un docs/*.md
studio/tests/run.sh                                # la ventana: servicio, modelos, controladores, cada QML y --smoke (repo y HOME falsos)
/usr/bin/python3 -m py_compile studio/main.py studio/dotfiles_app/*.py studio/dotfiles_app/*/*.py
QT_QPA_PLATFORM=offscreen /usr/bin/python3 studio/main.py --smoke   # abre y cierra la ventana sin pantalla
```

Los avisos A01/A07 sobre archivos de los paquetes son de formato ajeno (los fija la
aplicación) y no se corrigen.

## Detalles que cuesta redescubrir

- Los scripts usan `set -euo pipefail` y anotaciones de shellcheck (`# shellcheck source=…`);
  mantener ambas. Hace falta bash 4 (arrays asociativos).
- No hacer `source /etc/os-release`: sus variables chocan con las constantes `readonly` del
  repo; `config.sh` lee solo el campo `ID`.
- Los híbridos (`kdeglobals`, `kwinrc`, `konsolerc`, `texstudio.ini`) cambian tras usar las
  aplicaciones; `texstudio.ini` guarda además recientes y está pendiente de decisión
  (`docs/decisiones.md` §Pendientes): su diff no se confirma sin leerlo.
- calibre y KOReader escriben de forma atómica y sustituyen el enlace por un archivo real; se
  repone con `adoptar -p <paquete>`.
- Los plugins de Obsidian son enlaces de directorio; `main.js`, `styles.css` y `*.bak-*`
  quedan fuera por `.gitignore`.
- La configuración de KDE en Wayland la posee KWin: editar `kglobalshortcutsrc` a mano no
  recarga; se cambia desde Preferencias del Sistema o por DBus.
- `.backups/` y `.logs/` los gestiona el gestor; no se editan ni se confirman.
- starship está versionado pero inactivo: el `.zshrc` usa Oh My Zsh y no lo inicializa.
- Las fuentes de `USER_FONTS` las consume otro proyecto (`docs/arquitectura.md` §Consumidores):
  cambiar familia o versión obliga a avisar.
- `main.sh` pregunta por `/dev/tty` al adoptar un archivo que existe en los dos lados y lee la entrada estándar en
  `confirm_action` (eliminar): sin terminal, lo primero se salta y lo segundo no responde. La ventana pasa `--force`
  a eliminar y abre en una terminal adoptar con conflictos e `instalar-deps` (`sudo`).
- `--dry-run` de `instalar` crea las carpetas padre en `HOME` (`_create_symlink` hace `mkdir -p` antes de mirar
  `DRY_RUN`): la prueba `xfail` de `studio/tests/test_estado.py` lo documenta; es un pendiente del autor en `estado.md`.
- Las capturas de `docs/figuras/` se hacen con `studio/capturar.py` mostrando el Registro, no la Salida ni la vista
  Cambios: el repo es público y la salida de `main.sh` y los diffs llevan rutas de `HOME`.

## Dónde está cada cosa

| pregunta | documento |
|---|---|
| comandos, opciones y problemas frecuentes | `README.md` §Uso |
| paquetes, criterio, exclusiones, añadir un paquete | `docs/paquetes.md` |
| módulos, enlaces, escáner, respaldos, fuentes, consumidores | `docs/arquitectura.md` |
| atajos de KDE | `docs/atajos-kde.md` |
| decisiones | `docs/decisiones.md` |
| qué está hecho, en curso y pendiente | `estado.md` |
| la ventana: auditoría, arquitectura de información, componentes, decisiones | `docs/rediseno.md` y `studio/README.md` |
| la lista exacta de archivos de cada paquete | `config.sh` (`PACKAGE_FILES`) |
