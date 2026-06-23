# dotfiles-manager

> Gestor completo de dotfiles para **Arch Linux** y **Kubuntu** con GNU Stow y Git.
> Permite instalar, adoptar, sincronizar y respaldar configuraciones de forma segura
> desde un repositorio central en `/home/achalmaedison/.dotfiles`.

---

## 📋 Tabla de Contenidos

- [¿Por dónde empiezo?](#-por-dónde-empiezo)
- [Descripción](#-descripción)
- [Requisitos](#-requisitos)
- [Instalación del gestor](#-instalación-del-gestor)
- [Uso](#-uso)
- [Flujos de trabajo completos](#-flujos-de-trabajo-completos)
- [Arquitectura](#-arquitectura)
- [Bugs Corregidos](#-bugs-corregidos)
- [Solución de Problemas](#-solución-de-problemas)
- [Notas y Advertencias](#-notas-y-advertencias)

---

## 🚀 ¿Por dónde empiezo?

Dependiendo de tu situación, el primer paso es diferente:

### Escenario A — Máquina nueva, repo ya existe en GitHub

```bash
# 1. Clonar el repo
git clone https://github.com/achalmed/.dotfiles.git /home/achalmaedison/.dotfiles

# 2. Instalar stow
sudo pacman -S stow          # Arch
sudo apt install stow        # Kubuntu

# 3. Instalar todos los symlinks
cd /home/achalmaedison/.dotfiles
./main.sh instalar
```

### Escenario B — Tengo configs en la laptop, quiero comenzar a versionar

```bash
# 1. El repo ya está en ~/.dotfiles pero las configs están sueltas en ~/.config
# 2. Adoptar: mueve los archivos al repo y crea symlinks
./main.sh adoptar

# 3. Revisar qué se adoptó
cd /home/achalmaedison/.dotfiles && git diff

# 4. Subir a GitHub
./main.sh sync-push
```

### Escenario C — Tengo configs tanto en la laptop como en el repo (posible conflicto)

```bash
# 1. Ver el estado actual
./main.sh estado

# 2. Si hay conflictos, crear backup primero
./main.sh backup

# 3. Decidir: ¿la versión del repo o de la laptop es la correcta?
#    Si quieres la del REPO:    ./main.sh instalar --force
#    Si quieres la de LAPTOP:   ./main.sh adoptar
```

### Escenario D — Ya todo funciona, solo quiero actualizar

```bash
# Subir cambios locales a GitHub
./main.sh sync-push

# Bajar cambios de GitHub a la laptop
./main.sh sync-pull
```

---

## 📖 Descripción

`dotfiles-manager` es un gestor de configuraciones personales que resuelve el
problema de mantener en sincronía los dotfiles entre múltiples máquinas (Arch Linux
y Kubuntu) y un repositorio Git en GitHub.

**¿Qué hace exactamente?**

Usa **GNU Stow** para crear enlaces simbólicos desde el repositorio hacia los
directorios de configuración reales (`~/.config`, `~/.zshrc`, etc.). Esto significa
que los archivos "viven" en el repositorio, y las aplicaciones los ven en su
ubicación normal gracias a los symlinks.

**Ventajas de este enfoque:**

- Los cambios en cualquier app se reflejan automáticamente en el repo (vía symlink)
- Un solo `sync-push` sube todo a GitHub
- Una nueva máquina queda configurada con un solo comando
- El historial Git muestra exactamente qué cambió en cada config y cuándo

---

## ⚙️ Requisitos

### Sistema Operativo

- Arch Linux / Archcraft / EndeavourOS / Manjaro
- Ubuntu 20.04+ / Kubuntu / Debian / Linux Mint / Pop!\_OS

### Dependencias

| Herramienta   | Arch                 | Kubuntu            | Para qué             |
| ------------- | -------------------- | ------------------ | -------------------- |
| `stow`        | `pacman -S stow`     | `apt install stow` | Gestión de symlinks  |
| `git`         | `pacman -S git`      | `apt install git`  | Control de versiones |
| `zsh`         | `pacman -S zsh`      | `apt install zsh`  | Shell configurado    |
| `starship`    | `pacman -S starship` | Script oficial     | Prompt personalizado |
| `bash >= 4.0` | preinstalado         | preinstalado       | Ejecución del gestor |

### Instalación automática de dependencias

```bash
./main.sh instalar-deps
```

---

## 🔧 Instalación del gestor

El script debe vivir dentro del propio repositorio de dotfiles:

```bash
# Estructura esperada
/home/achalmaedison/.dotfiles/
├── main.sh          ← este script
├── config.sh
├── lib/
│   ├── logger.sh
│   ├── validator.sh
│   ├── cli.sh
│   ├── stow_ops.sh
│   ├── git_ops.sh
│   └── tools.sh
├── git/
├── shell/
├── kde/
└── ...              ← tus paquetes stow
```

```bash
# Dar permisos de ejecución
chmod +x /home/achalmaedison/.dotfiles/main.sh
chmod +x /home/achalmaedison/.dotfiles/lib/*.sh
```

**Alias recomendado** — agrégalo a tu `~/.zshrc`:

```zsh
alias dotfiles='/home/achalmaedison/.dotfiles/main.sh'
```

Así puedes usar `dotfiles instalar`, `dotfiles estado`, etc. desde cualquier lugar.

---

## 💻 Uso

### Menú interactivo (recomendado si estás aprendiendo)

```bash
./main.sh
# o con el alias:
dotfiles
```

### CLI directa

```
./main.sh <COMANDO> [OPCIONES]
```

### Comandos disponibles

| Comando         | Descripción                                           |
| --------------- | ----------------------------------------------------- |
| `instalar`      | Crea symlinks del repo hacia la laptop                |
| `adoptar`       | Mueve configs de la laptop al repo y crea symlinks    |
| `actualizar`    | Re-aplica symlinks (útil al agregar archivos al repo) |
| `eliminar`      | Elimina symlinks sin borrar el repo                   |
| `sync-push`     | Guarda cambios y los sube a GitHub                    |
| `sync-pull`     | Descarga cambios de GitHub y actualiza symlinks       |
| `estado`        | Muestra estado de symlinks y Git                      |
| `backup`        | Crea backup de configs actuales                       |
| `seguridad`     | Escanea archivos en busca de credenciales expuestas   |
| `instalar-deps` | Instala dependencias según la distro detectada        |

### Opciones globales

| Opción                         | Descripción                            |
| ------------------------------ | -------------------------------------- |
| `-p, --packages git,shell,kde` | Operar solo sobre paquetes específicos |
| `-v, --verbose`                | Salida detallada de cada operación     |
| `-n, --dry-run`                | Simular sin hacer cambios reales       |
| `-f, --force`                  | Forzar aunque haya conflictos          |
| `--no-backup`                  | No crear backup automático             |
| `-h, --help`                   | Ver ayuda completa                     |
| `--version`                    | Ver versión y distro detectada         |

### Ejemplos

```bash
# Inicio
cd /home/achalmaedison/.dotfiles

# Instalar todos los paquetes
./main.sh instalar

# Instalar solo git, shell y kde
./main.sh instalar -p git,shell,kde

# Adoptar solo zotero desde la laptop
./main.sh adoptar -p zotero
./main.sh adoptar -p git
./main.sh adoptar -p calibre


./main.sh adoptar -p git,shell,kde,terminal,digikam

# Simular un pull sin hacer cambios
./main.sh sync-pull --dry-run --verbose

# Ver todo el estado
./main.sh estado
./main.sh estado --verbose

# Subir a GitHub con confirmación de datos sensibles
./main.sh sync-push
```

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

## 🗂️ Arquitectura

```
/home/achalmaedison/.dotfiles/
├── main.sh              # Punto de entrada y orquestador
├── config.sh            # Constantes, rutas, detección de distro
├── lib/
│   ├── logger.sh        # Logging: INFO / WARN / ERROR / SUCCESS
│   ├── validator.sh     # Validación de entorno antes de ejecutar
│   ├── cli.sh           # Parseo de argumentos y menú interactivo
│   ├── stow_ops.sh      # Operaciones de GNU Stow (install/adopt/update/remove)
│   ├── git_ops.sh       # Operaciones Git (push/pull/status)
│   └── tools.sh         # Backup, instalación de dependencias
├── .backups/            # Backups automáticos (auto-gestionado)
├── .logs/               # Logs diarios (auto-gestionado)
├── .gitignore
│
├── git/                 # Paquete stow: .gitconfig
├── shell/               # Paquete stow: .zshrc, starship.toml
├── kde/                 # Paquete stow: kdeglobals, dolphinrc, kwinrc...
├── terminal/            # Paquete stow: konsolerc
├── vscode/              # Paquete stow: settings.json, keybindings.json
├── zotero/              # Paquete stow: prefs.js
├── obsidian/            # Paquete stow: Documents/.obsidian/
├── calibre/             # Paquete stow: gui.json, viewer.json
├── kate/                # Paquete stow: katerc, lspclient/
├── texstudio/           # Paquete stow: texstudio.ini
├── rstudio/             # Paquete stow: rstudio-prefs.json
└── ...                  # demás paquetes
```

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

## 🐛 Bugs Corregidos

### Bug #1: `set -euo pipefail` ausente

- **Descripción**: Ningún script original tenía protección contra errores silenciosos
- **Impacto**: Un `stow` fallido podía continuar y dejar el sistema en estado inconsistente
- **Corrección**: `set -euo pipefail` al inicio de `main.sh` con manejo explícito de errores por módulo

### Bug #2: `stow` sin manejo de conflictos

- **Descripción**: Los scripts originales ejecutaban `stow` directamente sin verificar si había archivos reales en su lugar
- **Impacto**: Fallos crípticos de stow sin indicar al usuario qué hacer
- **Corrección**: `stow_ops.sh` detecta conflictos con `--simulate`, informa claramente y sugiere la acción correcta (adoptar o instalar con force)

### Bug #3: `ln -sf` hardcodeado en `adoptconfig.sh`

- **Descripción**: Se usaban `ln -sf` manuales para rstudio y texstudio además de stow
- **Impacto**: Duplicidad de gestión; si stow y ln apuntan a lugares distintos, hay inconsistencias difíciles de depurar
- **Corrección**: Todo pasa por stow de forma uniforme; los directorios padre se crean automáticamente si no existen

### Bug #4: Análisis de datos sensibles incompleto

- **Descripción**: `analizadatosensibles.sh` solo revisaba `prefs.js`
- **Impacto**: `.gitconfig` con nombre/email, `settings.json` de VSCode con tokens podían subirse sin revisión
- **Corrección**: `validator.sh` revisa todos los archivos definidos en `SENSITIVE_FILES_TO_CHECK` con una lista expandida de patrones

### Bug #5: Sin distinción Arch vs Kubuntu

- **Descripción**: Los scripts usaban `apt install stow` aunque pueden correrse en Arch
- **Impacto**: Error inmediato en Arch donde `apt` no existe
- **Corrección**: `config.sh` detecta la distro con `/etc/os-release` y selecciona el gestor de paquetes correcto; `tools.sh` tiene ramas separadas para cada distro

---

## 🔧 Solución de Problemas

### Error: "El directorio de dotfiles no existe"

```bash
git clone https://github.com/achalmed/.dotfiles.git /home/achalmaedison/.dotfiles
```

### Error: "GNU Stow no está instalado"

```bash
./main.sh instalar-deps
# o manualmente:
sudo pacman -S stow      # Arch
sudo apt install stow    # Kubuntu
```

### Error: "Hay conflictos — archivo real existe en laptop"

Significa que existe un archivo normal (no symlink) donde stow quiere crear el symlink.

```bash
# Ver dónde están los conflictos
./main.sh estado

# Opción 1: Adoptar la versión de la laptop al repo
./main.sh adoptar -p <paquete>

# Opción 2: Forzar con la versión del repo (hace backup automático)
./main.sh instalar -p <paquete> --force
```

### Error: "Falló git push"

```bash
# Verificar conexión
ping github.com

# Verificar que tienes remote configurado
cd ~/.dotfiles && git remote -v

# Si el remote no existe:
git remote add origin https://github.com/achalmed/.dotfiles.git

# Si usas SSH:
git remote set-url origin git@github.com:achalmed/.dotfiles.git
```

### Error: "Datos sensibles detectados antes del push"

El scanner encontró posibles credenciales. Revisa el archivo indicado:

```bash
# Ver qué encontró
./main.sh seguridad

# Editar el archivo y eliminar la credencial
nano <archivo_indicado>

# Volver a intentar
./main.sh sync-push
```

### Los symlinks quedaron rotos después de mover archivos

```bash
# Re-aplicar todos los symlinks
./main.sh actualizar
```

---

## ⚠️ Notas y Advertencias

**Distros soportadas:** El script detecta automáticamente Arch Linux (y derivados: Archcraft, EndeavourOS, Manjaro) y Ubuntu/Kubuntu (y derivados: Debian, Linux Mint, Pop!\_OS). Para otras distros, las operaciones de stow funcionan pero la instalación de dependencias requiere hacerse manualmente.

**Archivo `prefs.js` de Zotero:** Contiene la ruta del perfil `25vfdnq5.default` que es específica de tu instalación. En una nueva máquina, Zotero generará un ID de perfil diferente. Ajusta la ruta en `config.sh` → `SENSITIVE_FILES_TO_CHECK` si cambia.

**Obsidian vault:** El vault está configurado directamente en `~/Documents` (el directorio Documents completo es el vault, con `.obsidian/` dentro). Si en alguna máquina está en otra ruta, actualiza la estructura del paquete `obsidian/` en el repo para que refleje la ruta correcta.

**Backups:** Se guardan en `.dotfiles/.backups/` y se mantienen los últimos 10 automáticamente. No son parte del repo git (están en `.gitignore` recomendado). Son backups de emergencia, no reemplazan un backup completo del sistema.

**KDE Plasma:** `plasma-org.kde.plasma.desktop-appletsrc` contiene layouts de paneles y widgets que pueden ser específicos del hardware y la resolución de pantalla. Al instalar en una nueva máquina, KDE podría mostrar un layout diferente al esperado.

**Agregar un nuevo paquete stow:** Crea el directorio con la estructura de rutas relativas al home. Por ejemplo, para agregar `~/.config/miapp/config.yaml`:

```bash
mkdir -p ~/.dotfiles/miapp/.config/miapp/
# Mueve o copia tu config al repo
mv ~/.config/miapp/config.yaml ~/.dotfiles/miapp/.config/miapp/
# Agrega 'miapp' a STOW_PACKAGES en config.sh
# Luego instala el symlink
./main.sh instalar -p miapp
```
