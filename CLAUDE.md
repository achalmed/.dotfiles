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
- **Dónde va cada cosa nueva.** En la raíz solo `README.md`, `CLAUDE.md`, `AGENTS.md`, `main.sh`,
  `config.sh`, `.gitignore` y, cuando el autor la decida, `LICENSE`. **Nunca un `.md` dentro de un
  directorio de paquete**: `stow <paquete>` lo enlazaría a `$HOME`.

  | lo que apareció | va a | nunca a |
  |---|---|---|
  | cómo se instala o se usa | `README.md` §Uso | un `GUIA_RAPIDA.md` |
  | qué cubre un paquete, una exclusión, cómo se añade uno | `docs/paquetes.md` | un README dentro del paquete |
  | cómo funciona el gestor, quién consume el repo | `docs/arquitectura.md` | un `ARQUITECTURA_NUEVA.md` |
  | atajos de KDE | `docs/atajos-kde.md` | `kde/` |
  | por qué se decidió algo | `docs/decisiones.md` | un `DECISION_<fecha>.md` |
  | un pendiente | `docs/decisiones.md` §Pendientes, con fecha y dueño | un `TODO.md` |
  | una regla para el asistente | este archivo, si es transversal y estable | un segundo archivo de instrucciones |

  Lo que hiciste en esta sesión va al mensaje de commit, no a un archivo. Si nada encaja,
  pregunta antes de crear un documento.

## Cómo se verifica un cambio

```bash
bash -n main.sh config.sh lib/*.sh                 # sintaxis de cada script tocado
./main.sh instalar --dry-run -p <paquete>          # el mapa describe el disco (no escribe enlaces)
./main.sh seguridad                                # credenciales en lo versionado
python3 ~/Documents/core/archivos.py validar ~/.dotfiles   # normativa documental del ecosistema
python3 ~/Documents/core/docs.py indice ~/.dotfiles --aplicar   # índice de docs/ tras tocar un docs/*.md
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

## Dónde está cada cosa

| pregunta | documento |
|---|---|
| comandos, opciones y problemas frecuentes | `README.md` §Uso |
| paquetes, criterio, exclusiones, añadir un paquete | `docs/paquetes.md` |
| módulos, enlaces, escáner, respaldos, fuentes, consumidores | `docs/arquitectura.md` |
| atajos de KDE | `docs/atajos-kde.md` |
| decisiones y pendientes | `docs/decisiones.md` |
| la lista exacta de archivos de cada paquete | `config.sh` (`PACKAGE_FILES`) |
