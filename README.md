# dotfiles-manager

> Gestor de dotfiles para **Arch Linux** y **Kubuntu** con Git y layout
> compatible con GNU Stow. Versiona únicamente configuraciones realmente
> personalizadas para reproducir el entorno de trabajo en cualquier equipo.

---

## 📋 Tabla de Contenidos

- [Filosofía: principio de mínima captura](#-filosofía-principio-de-mínima-captura)
- [¿Por dónde empiezo?](#-por-dónde-empiezo)
- [Requisitos](#-requisitos)
- [Uso](#-uso)
- [Paquetes gestionados](#-paquetes-gestionados)
- [Exclusiones deliberadas](#-exclusiones-deliberadas)
- [El paquete `meta` (Documents/meta)](#-el-paquete-meta-documentsmeta)
- [Arquitectura](#-arquitectura)
- [Agregar un nuevo paquete](#-agregar-un-nuevo-paquete)
- [Seguridad](#-seguridad)
- [Solución de problemas](#-solución-de-problemas)
- [Notas y advertencias](#-notas-y-advertencias)

---

## 🎯 Filosofía: principio de mínima captura

Este repositorio **NO es un respaldo del sistema**. Cada archivo versionado
debe responder afirmativamente a esta pregunta:

> _"¿Este archivo representa una personalización que yo hice manualmente
> y que realmente quiero reproducir en otro equipo?"_

**Se versiona:**

- preferencias, apariencia, temas, atajos y keybindings
- snippets, plantillas y scripts propios
- configuración de editores, shell y herramientas
- configuración de plugins (JSON/Lua/TOML, nunca binarios)

**Se excluye siempre:**

- caché, logs, locks, bases de datos, índices
- historial, listas MRU ("archivos recientes"), posiciones de ventanas
- IDs de máquina, estado de sesión, datos dependientes del hardware
- credenciales y cualquier archivo regenerable

La selección es **positiva y explícita**: el mapa `PACKAGE_FILES` de
`config.sh` enumera exactamente qué archivos gestiona cada paquete.
Lo que no está en la lista, no se toca. El `.gitignore` actúa como segunda
línea de defensa.

---

## 🚀 ¿Por dónde empiezo?

### Escenario A — Máquina nueva, repo ya existe en GitHub

```bash
git clone https://github.com/achalmed/.dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./main.sh instalar
```

### Escenario B — Tengo configs en la laptop, quiero comenzar a versionar

```bash
./main.sh adoptar            # mueve los archivos al repo y crea symlinks
cd ~/.dotfiles && git diff   # revisar qué se adoptó
./main.sh sync-push          # subir a GitHub
```

### Escenario C — Configs en la laptop Y en el repo (posible conflicto)

```bash
./main.sh estado             # ver dónde están los conflictos
./main.sh backup             # backup de seguridad primero
# Si quieres la versión del REPO:    ./main.sh instalar --force
# Si quieres la de la LAPTOP:        ./main.sh adoptar
```

### Escenario D — Ya todo funciona, solo quiero actualizar

```bash
./main.sh sync-push          # subir cambios locales
./main.sh sync-pull          # bajar cambios de GitHub
```

**Alias recomendado** — agrégalo a tu `~/.zshrc`:

```zsh
alias dotfiles='~/.dotfiles/main.sh'
```

---

## ⚙️ Requisitos

### Sistema operativo

- Arch Linux / Archcraft / EndeavourOS / Manjaro
- Ubuntu 20.04+ / Kubuntu / Debian / Linux Mint / Pop!\_OS

### Dependencias

| Herramienta   | ¿Obligatoria? | Para qué                                                                                          |
| ------------- | ------------- | ------------------------------------------------------------------------------------------------- |
| `git`         | Sí            | Control de versiones y sincronización                                                             |
| `bash >= 4.0` | Sí            | Ejecución del gestor (arrays asociativos)                                                         |
| `zsh`         | No            | Shell configurado por el paquete `shell`                                                          |
| `stow`        | No            | El gestor crea symlinks directamente; el layout es compatible con stow si prefieres usarlo a mano |
| `starship`    | No            | Prompt; config disponible pero inactiva (ver notas)                                               |

```bash
./main.sh instalar-deps      # instalación automática según la distro
```

---

## 💻 Uso

```bash
./main.sh                    # menú interactivo
./main.sh <COMANDO> [OPCIONES]
```

### Comandos

| Comando         | Descripción                                             |
| --------------- | ------------------------------------------------------- |
| `instalar`      | Crea symlinks del repo hacia la laptop                  |
| `adoptar`       | Mueve configs de la laptop al repo y crea symlinks      |
| `actualizar`    | Re-aplica symlinks (útil al agregar archivos al repo)   |
| `eliminar`      | Elimina symlinks sin borrar el repo                     |
| `sync-push`     | Escanea datos sensibles, commitea y sube a GitHub       |
| `sync-pull`     | Descarga cambios de GitHub y actualiza symlinks         |
| `estado`        | Muestra estado de symlinks y Git                        |
| `backup`        | Crea backup de configs actuales                         |
| `seguridad`     | Escanea todos los archivos versionados por credenciales |
| `instalar-deps` | Instala dependencias según la distro detectada          |

### Opciones globales

| Opción                         | Descripción                            |
| ------------------------------ | -------------------------------------- |
| `-p, --packages git,shell,kde` | Operar solo sobre paquetes específicos |
| `-v, --verbose`                | Salida detallada de cada operación     |
| `-n, --dry-run`                | Simular sin hacer cambios reales       |
| `-f, --force`                  | Reemplazar sin preguntar (con backup)  |
| `--no-backup`                  | No crear backup automático             |
| `-h, --help`                   | Ver ayuda completa                     |
| `--version`                    | Ver versión y distro detectada         |

### Ejemplos

```bash
# Inicio
cd /home/achalmaedison/.dotfiles
./main.sh instalar -p git,shell,kde     # instalar solo esos paquetes
./main.sh adoptar -p meta               # adoptar solo el paquete meta
./main.sh adoptar -p zotero
./main.sh adoptar -p git
./main.sh adoptar -p calibre

./main.sh sync-pull --dry-run --verbose # simular un pull
./main.sh estado
./main.sh estado --verbose              # estado archivo por archivo

# Subir a GitHub con confirmación de datos sensibles
./main.sh sync-push
```

**Nota para uso no interactivo/scripts:** pasa siempre `-p` (sin TTY los
prompts usan la opción segura por defecto: saltar/no eliminar).

---

## 📦 Paquetes gestionados

| Paquete     | Contenido                                                                                                                                                 |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `git`       | `.gitconfig`                                                                                                                                              |
| `shell`     | `.zshrc`, `.config/starship.toml`                                                                                                                         |
| `kde`       | `kdeglobals`, `kglobalshortcutsrc`, `kwinrc`, `dolphinrc`, `plasmarc`, `plasma-localerc`, `mimeapps.list`                                                 |
| `konsole`   | `konsolerc` + **perfiles y esquemas de color** (`~/.local/share/konsole/`)                                                                                |
| `positron`  | `settings.json` del IDE Positron                                                                                                                          |
| `obsidian`  | Config del vault: `app.json`, `appearance.json`, `hotkeys.json`, `community-plugins.json`, `core-plugins.json`, `snippets/`, `data.json` de plugins clave |
| `meta`      | Recursos del vault en `~/Documents/meta` (ver sección propia)                                                                                             |
| `calibre`   | `global.py.json`, `tweak_book_gui.json`, `viewer-webengine.json`                                                                                          |
| `kate`      | `katerc`, `lspclient/settings.json`, `externaltools/`                                                                                                     |
| `texstudio` | `texstudio.ini` (híbrido, ver notas)                                                                                                                      |
| `okular`    | `okularpartrc` (solo preferencias de visualización)                                                                                                       |
| `rstudio`   | `rstudio-prefs.json`                                                                                                                                      |
| `xournalpp` | `settings.xml`                                                                                                                                            |
| `koreader`  | `defaults.custom.lua`, `gestures.lua`, `hotkeys.lua`, `directory_defaults.lua`                                                                            |

---

## 🚫 Exclusiones deliberadas

Archivos que **existían en versiones anteriores del repo** y fueron
excluidos tras la auditoría v3.0, porque el estado domina sobre la
configuración (generaban commits enormes e inútiles en cada uso):

| App         | Archivo                                         | Por qué se excluyó                                                                                            |
| ----------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| digiKam     | `digikamrc`                                     | Índices de sidebar, geometría, rutas de BD **y contraseña de BD**                                             |
| Krusader    | `krusaderrc`                                    | PopularUrls, historial de tabs, estado binario de toolbars                                                    |
| Zotero      | `prefs.js`                                      | Timestamps de sync, geometría; además la ruta del perfil (`0xh8512f.default`) no es portable entre máquinas   |
| Okular      | `okularrc`                                      | Dominado por "Recent Files" y geometría (las preferencias reales viven en `okularpartrc`, que sí se versiona) |
| LibreOffice | `registrymodifications.xcu`                     | Mezcla MRU, posiciones y rutas locales en un solo archivo que cambia en cada uso                              |
| KDE Plasma  | `plasma-org.kde.plasma.desktop-appletsrc`       | Layout de paneles dependiente de monitor/resolución                                                           |
| KDE Plasma  | `plasmashellrc`                                 | Estado del shell por pantalla                                                                                 |
| Konsole     | `konsolesshconfig`                              | Estado de plugin, sin personalización                                                                         |
| Obsidian    | `workspace.json`, `core-plugins-migration.json` | Estado de ventanas / migración regenerable                                                                    |
| calibre     | `gui.json`                                      | Geometría de ventanas y modelo/fabricante del monitor (hardware)                                              |
| calibre     | `gui.py.json`                                   | Historial de búsquedas (MRU)                                                                                  |
| KOReader    | `settings.reader.lua`                           | Último archivo abierto (MRU) y geometría; la app lo reescribe en cada uso                                     |
| VSCode      | paquete completo                                | Reemplazado por Positron; la app ya no está instalada                                                         |

Las configuraciones de esas apps **no se pierden**: al excluirlas del repo
se restauraron como archivos reales en `$HOME`. Simplemente ya no se
versionan. Para reproducir su configuración en otra máquina, configúralas
una vez a mano (o usa sus mecanismos propios, p. ej. el sync de Zotero).

---

## 🗂️ El paquete `meta` (Documents/meta)

`~/Documents` es el vault de Obsidian y `~/Documents/meta` concentra los
recursos reproducibles del sistema de trabajo:

```
meta/Documents/meta/
├── dataview/    # consultas y vistas JS de Dataview
├── javascript/  # scripts de soporte (frontmatter, encabezados…)
├── longform/    # scripts para Longform
├── quickadd/    # macros y capturas de QuickAdd
├── sistema/     # documentación del sistema GTD/PKM
├── tablero/     # dashboards (inicio, semana, proyectos…)
├── templater/   # plantillas Templater (tipos/, planes/, revisiones/)
├── zotero/      # plantillas de notas de investigación
└── readme.md
```

Se gestionan como **symlinks de directorio** (el contenido evoluciona por
dentro sin tocar `config.sh`). Quedaron fuera deliberadamente:

- `attachments/` — binarios (imágenes) que no son configuración
- `archivo/` — material archivado/obsoleto
- `templates/` — vacío actualmente
- `.claude/` — configuración local de Claude (permisos por máquina)

Separación de responsabilidades: `~/.config` = configuración del sistema y
apps (paquetes por app); `~/Documents/meta` = recursos de trabajo (paquete
`meta`). El paquete `obsidian` gestiona la config del vault (`.obsidian/`),
`meta` gestiona su contenido reproducible.

---

## 🔄 Flujos de trabajo completos

### Flujo 1: Configuración inicial en máquina nueva

```bash
# Paso 1: Clonar el repo
git clone https://github.com/achalmed/.dotfiles.git ~/.dotfiles

# Paso 2: Instalar dependencias
~/.dotfiles/main.sh instalar-deps

# Paso 3: Instalar todas las configuraciones
~/.dotfiles/main.sh instalar

# Paso 4: Agregar alias al .zshrc (ya estará linkeado)
echo "alias dotfiles='~/.dotfiles/main.sh'" >> ~/.zshrc
source ~/.zshrc
```

### Flujo 2: Modificar una configuración y guardarla

```bash
# Modificas normalmente tu config (ej: ~/.config/kate/katerc)
# Como es un symlink, el cambio ya está en el repo automáticamente

# Verificar qué cambió
dotfiles estado

# Subir a GitHub
dotfiles sync-push
```

### Flujo 3: Actualizar la laptop con cambios del repo

```bash
# Descargar cambios y aplicar
dotfiles sync-pull

# Verifica que todo quedó bien
dotfiles estado
```

### Flujo 4: Comenzar a versionar una config que aún no está en el repo

```bash
# Supón que quieres agregar la config de una app nueva

# Paso 1: Crear el directorio del paquete en el repo
mkdir -p ~/.dotfiles/miapp/.config/miapp/

# Paso 2: Adoptar (mueve el archivo al repo y crea el symlink)
dotfiles adoptar -p miapp

# Paso 3: Verificar que el symlink funciona
ls -la ~/.config/miapp/

# Paso 4: Subir a GitHub
dotfiles sync-push
```

### Flujo 5: Resolver conflicto (configs en laptop Y en repo)

```bash
# Ver dónde están los conflictos
dotfiles estado

# Opción A: Me quedo con la versión del REPO
dotfiles backup                    # backup de seguridad primero
dotfiles instalar --force          # sobrescribe con la del repo

# Opción B: Me quedo con la versión de la LAPTOP
dotfiles adoptar                   # mueve la de laptop al repo
cd ~/.dotfiles && git diff         # revisar qué cambió
dotfiles sync-push                 # subir la versión de laptop
```

---

## 🏗️ Arquitectura

```
~/.dotfiles/
├── main.sh              # Punto de entrada: carga módulos y hace dispatch
├── config.sh            # Constantes, distro, STOW_PACKAGES, PACKAGE_FILES
├── lib/
│   ├── logger.sh        # Logging a consola + .logs/dotfiles-YYYY-MM-DD.log
│   ├── validator.sh     # Pre-flight checks + escáner de datos sensibles
│   ├── cli.sh           # Parseo de argumentos, menú, confirmaciones
│   ├── stow_ops.sh      # adoptar/instalar/actualizar/eliminar symlinks
│   ├── git_ops.sh       # sync-push / sync-pull / estado git
│   └── tools.sh         # Backups quirúrgicos/completos, dependencias
├── .backups/            # Backups automáticos (ignorado por git)
├── .logs/               # Logs diarios (ignorado por git)
└── <paquetes>/          # git/ shell/ kde/ konsole/ … meta/
```

### Decisiones de diseño

1. **Selección explícita de archivos.** `PACKAGE_FILES["app"]="ruta1|ruta2"`
   (rutas relativas a `$HOME`) decide qué se gestiona. Nunca se adopta un
   directorio de configuración completo "a ciegas".

2. **Symlinks directos, layout compatible con Stow.** El gestor crea los
   enlaces con `ln -sfn` archivo por archivo — el binario de GNU Stow no es
   necesario. Cada paquete replica la estructura de `$HOME`, así que
   `stow <paquete>` también funcionaría (pero enlazaría todo el paquete,
   sin el control archivo-por-archivo).

3. **Fallar rápido y seguro.** `set -euo pipefail`, validaciones antes de
   operar, backups quirúrgicos automáticos antes de instalar/adoptar, y
   prompts con opción segura por defecto cuando no hay TTY.

4. **Portabilidad.** `DOTFILES_DIR` se deriva de `$HOME` (sobreescribible
   por variable de entorno). La detección de distro elige pacman o apt.

### Descripción de módulos

| Archivo            | Responsabilidad                                                  |
| ------------------ | ---------------------------------------------------------------- |
| `main.sh`          | Carga módulos, parsea args, hace dispatch al comando correcto    |
| `config.sh`        | Detecta distro, define rutas, paquetes stow, patrones sensibles  |
| `lib/logger.sh`    | Logging formateado a consola y archivo con niveles y colores     |
| `lib/validator.sh` | Verifica stow, git, internet, árbol limpio, datos sensibles      |
| `lib/cli.sh`       | Parseo de argumentos, menú interactivo, confirmaciones           |
| `lib/stow_ops.sh`  | Instalar, adoptar, actualizar y eliminar symlinks con stow       |
| `lib/git_ops.sh`   | Push con validación, pull con re-stow, estado del repo           |
| `lib/tools.sh`     | Backups comprimidos con limpieza automática, instalación de deps |

---

## ➕ Agregar un nuevo paquete

```bash
# 1. Agrega el paquete a STOW_PACKAGES en config.sh
# 2. Define sus archivos (SOLO personalización, nunca caché/estado):
#    PACKAGE_FILES["miapp"]=".config/miapp/config.yaml"
# 3. Adopta (mueve el archivo al repo y crea el symlink):
./main.sh adoptar -p miapp
# 4. Revisa y sube:
git diff && ./main.sh sync-push
```

Antes de agregar un archivo pregúntate: ¿lo configuré yo? ¿cambia solo con
el uso normal de la app? ¿contiene rutas absolutas de esta máquina,
historial o credenciales? Ante la duda, obsérvalo unos días con
`git diff` antes de versionarlo.

---

## 🔐 Seguridad

- `sync-push` ejecuta **siempre** el escáner de datos sensibles y aborta si
  hay hallazgos. El escáner recorre TODOS los archivos versionados (y los
  nuevos no ignorados) con patrones tipo `clave=valor` para minimizar
  falsos positivos: contraseñas, api keys, tokens (`ghp_…`, `sk-…`) y
  claves privadas PEM.
- Falsos positivos revisados se declaran en `SENSITIVE_SCAN_ALLOWLIST`
  (config.sh).
- Ejecución manual: `./main.sh seguridad`.
- El `.gitignore` bloquea además credenciales típicas (`*.pem`, `key4.db`,
  `logins.json`, `cookies.sqlite`).

> ⚠️ Nota histórica: versiones anteriores del repo versionaron `digikamrc`,
> que incluye una contraseña de BD codificada. El archivo ya no se versiona,
> pero permanece en el historial de Git. Si esa contraseña importa, rótala
> (o reescribe el historial con `git filter-repo` y fuerza el push).

---

## 🔧 Solución de problemas

### "Hay conflictos — archivo real existe en laptop"

Existe un archivo normal (no symlink) donde el gestor quiere crear el enlace.

```bash
./main.sh estado                      # ver dónde
./main.sh adoptar  -p <paquete>       # opción 1: laptop → repo
./main.sh instalar -p <paquete> -f    # opción 2: repo → laptop (con backup)
```

### "Falló git push"

```bash
cd ~/.dotfiles && git remote -v       # ¿remote configurado?
git remote add origin git@github.com:achalmed/.dotfiles.git
```

### "Datos sensibles detectados antes del push"

```bash
./main.sh seguridad                   # ver qué y dónde
# Edita el archivo y elimina la credencial, o si es falso positivo
# revisado, agrégalo a SENSITIVE_SCAN_ALLOWLIST en config.sh
```

### Los symlinks quedaron rotos

```bash
./main.sh actualizar                  # re-aplica todos los symlinks
```

### Un archivo versionado empieza a generar mucho churn

Señal de que la app le mete estado. Decide: ¿las preferencias dominan?
Si no: quítalo de `PACKAGE_FILES`, borra el symlink, mueve el archivo del
repo de vuelta a `$HOME` y `git rm --cached` la ruta.

---

## ⚠️ Notas y advertencias

**Archivos híbridos (churn menor esperado).** KDE y TeXstudio mezclan
preferencias y algo de estado en el mismo archivo. Se versionan porque las
preferencias dominan: `kdeglobals`, `kwinrc`, `konsolerc`, `texstudio.ini`.
Es normal ver diffs pequeños tras usar las apps; revísalos en `sync-push`.

**Obsidian vault.** El vault es `~/Documents` completo (con `.obsidian/`
dentro). Los paquetes `obsidian` y `meta` asumen esa ruta; si en otra
máquina el vault vive en otro lado, ajusta la estructura de ambos paquetes.

**Starship inactivo.** `shell/.config/starship.toml` está versionado en la
ruta XDG estándar, pero el `.zshrc` actual usa Oh My Zsh y no inicializa
starship. Para activarlo: `eval "$(starship init zsh)"` al final del
`.zshrc`.

**Perfil de Konsole.** El paquete `konsole` versiona el perfil
`achalmaedison.profile`; `konsolerc` lo referencia por nombre, así que
funciona igual en cualquier máquina.

**Apps que rompen symlinks (escritura atómica).** calibre y KOReader
guardan su configuración escribiendo un archivo nuevo y renombrándolo,
lo que reemplaza el symlink por un archivo real. Por eso sus archivos
más volátiles quedaron excluidos. Si `estado` muestra conflictos en esos
paquetes tras usar las apps, ejecuta `./main.sh adoptar -p <paquete>`
para re-sincronizar los archivos que sí se versionan.

**Backups.** Se guardan en `.backups/` (fuera de git) y se conservan los
últimos 15 automáticamente. Son backups de emergencia por archivo, no
reemplazan un respaldo completo del sistema.

**Kubuntu vs Arch.** `instalar-deps` detecta la distro por `/etc/os-release`
y usa pacman o apt. En otras distros, instala `git` (y opcionalmente `zsh`)
a mano; el resto del gestor funciona igual.
