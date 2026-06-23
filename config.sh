#!/usr/bin/env bash
# =============================================================================
# config.sh — Configuración centralizada del gestor de dotfiles
# =============================================================================
# FILOSOFÍA DE ARCHIVOS GESTIONADOS:
#   Solo se versionan archivos de PERSONALIZACIÓN (lo que el usuario configura).
#   Se excluyen: caché, logs, locks, bases de datos SQLite, IDs de máquina,
#   credenciales, archivos temporales, y datos que no son portables entre máquinas.
#
#   Cada paquete tiene una lista explícita de qué archivos gestionar.
#   Si no está en la lista → no se toca. Así el repo permanece limpio.
# =============================================================================

# --- Rutas principales -------------------------------------------------------
readonly DOTFILES_DIR="/home/achalmaedison/.dotfiles"
readonly BACKUP_DIR="${DOTFILES_DIR}/.backups"
readonly LOG_DIR="${DOTFILES_DIR}/.logs"
readonly LOG_FILE="${LOG_DIR}/dotfiles-$(date '+%Y-%m-%d').log"

# --- Versión del proyecto -----------------------------------------------------
readonly VERSION="2.0.0"
readonly SCRIPT_NAME="dotfiles-manager"

# --- Detección de distribución ------------------------------------------------
# Se detecta al cargar config para que todos los módulos tengan acceso.
# Arch y Kubuntu difieren en: gestor de paquetes, rutas XDG, y algunos
# paths de configuración de aplicaciones.
#
# IMPORTANTE: NO usar 'source /etc/os-release' porque ese archivo define
# variables como VERSION, NAME, ID que colisionan con las nuestras al ser
# declaradas readonly más adelante. En su lugar, leemos solo el campo ID
# con grep para extraer únicamente lo que necesitamos.
_detect_distro() {
    if [ -f /etc/os-release ]; then
        grep -E '^ID=' /etc/os-release | cut -d'=' -f2 | tr -d '"'
    else
        echo "unknown"
    fi
}
readonly DISTRO="$(_detect_distro)"

# --- Gestor de paquetes por distro -------------------------------------------
case "$DISTRO" in
    arch | archcraft | endeavouros | manjaro)
        readonly PKG_MANAGER="pacman"
        readonly PKG_INSTALL="sudo pacman -S --noconfirm"
        readonly PKG_UPDATE="sudo pacman -Syu --noconfirm"
        readonly PKG_QUERY="pacman -Q"
        ;;
    ubuntu | kubuntu | debian | linuxmint | pop)
        readonly PKG_MANAGER="apt"
        readonly PKG_INSTALL="sudo apt install -y"
        readonly PKG_UPDATE="sudo apt update && sudo apt upgrade -y"
        readonly PKG_QUERY="dpkg -l"
        ;;
    *)
        readonly PKG_MANAGER="unknown"
        readonly PKG_INSTALL="echo 'Gestor de paquetes desconocido. Instala manualmente:'"
        readonly PKG_UPDATE="echo 'Gestor de paquetes desconocido.'"
        readonly PKG_QUERY="echo 'Gestor de paquetes desconocido.'"
        ;;
esac

# --- Paquetes requeridos por distro -------------------------------------------
# Arch usa nombres distintos a Ubuntu/Kubuntu para algunos paquetes.
declare -A REQUIRED_PACKAGES_ARCH=(
    [stow]="stow"
    [git]="git"
    [zsh]="zsh"
    [starship]="starship"
)

declare -A REQUIRED_PACKAGES_APT=(
    [stow]="stow"
    [git]="git"
    [zsh]="zsh"
    # starship no está en repos oficiales de Ubuntu; se instala via curl
    [curl]="curl"
)

# --- Módulos Stow a gestionar -------------------------------------------------
# Lista canónica de todos los paquetes stow del repositorio.
# Orden importa: los módulos base (shell, git) van primero.
# NOTA: el paquete "positron" reemplaza a "vscode" — Positron IDE guarda
# su config en ~/.config/Positron/ en lugar de ~/.config/Code/User/
readonly STOW_PACKAGES=(
    git
    shell
    kde
    terminal
    digikam
    vscode
    positron      # Positron IDE (fork de VSCode); config en ~/.config/Positron/
    zotero
    obsidian
    calibre
    libreoffice
    xournalpp
    kate
    texstudio
    lyx
    okular
    rstudio
    vlc
    krusader
    koreader
)

# =============================================================================
# MAPA DE ARCHIVOS POR PAQUETE
# =============================================================================
# Define exactamente qué archivos gestiona cada paquete.
# Formato: PACKAGE_FILES["nombre"]="ruta1|ruta2|ruta3"
# Las rutas son RELATIVAS al directorio HOME del usuario.
#
# REGLAS de inclusión:
#   ✓ Archivos JSON/INI/TOML de configuración de la app
#   ✓ Archivos de preferencias personalizadas
#   ✓ Snippets, temas, plugins (código, no binarios)
#   ✓ Keybindings personalizados
#
# REGLAS de exclusión (nunca versionar):
#   ✗ Caché (Cache/, .cache/, *.sqlite, *.db)
#   ✗ Logs (*.log, Log/)
#   ✗ Locks (*.lock, LOCK, code.lock)
#   ✗ IDs de máquina (machineid, crashpad/)
#   ✗ Datos de sesión (Session Storage/, Local Storage/)
#   ✗ Credenciales (privateKey.pem, cert9.db, logins.json)
#   ✗ Datos binarios grandes (CRX, VSIX, GPU cache)
#   ✗ Archivos de estado volátil (workspace.json en Obsidian)
# =============================================================================
declare -A PACKAGE_FILES

# git: solo .gitconfig (sin credenciales — usar credential.helper)
PACKAGE_FILES["git"]=".gitconfig"

# shell: configuración del prompt y del shell
PACKAGE_FILES["shell"]=".zshrc|starship.toml"

# kde: configuración de KDE Plasma (solo los archivos de preferencias globales)
PACKAGE_FILES["kde"]=\
".config/kdeglobals|\
.config/dolphinrc|\
.config/kwinrc|\
.config/plasma-org.kde.plasma.desktop-appletsrc|\
.config/plasmarc|\
.config/mimeapps.list|\
.config/kglobalshortcutsrc|\
.config/plasmashellrc|\
.config/plasma-localerc|\
.config/konsolerc|\
.config/konsolesshconfig"

# terminal: Konsole (ya incluido en kde pero también standalone)
PACKAGE_FILES["terminal"]=".config/konsolerc"

# digikam: solo preferencias (sin historial ni caché de BD)
PACKAGE_FILES["digikam"]=".config/digikamrc"

# positron: Positron IDE — solo settings, snippets y keybindings
# NO: cache, gpu cache, crashpad, session storage, machine id, cookies
PACKAGE_FILES["positron"]=\
".config/Positron/User/settings.json|\
.config/Positron/User/keybindings.json|\
.config/Positron/User/snippets"

# zotero: solo prefs.js — contiene tus preferencias de la app
# NO: bases de datos SQLite (places.sqlite etc), cache, locks, credenciales
# El ID de perfil 0xh8512f.default es específico de esta instalación.
PACKAGE_FILES["zotero"]=".zotero/zotero/0xh8512f.default/prefs.js"

# obsidian: configuración del vault en ~/Documents/.obsidian/
# NO: workspace.json (estado de ventanas, no portable), vault-stats.json (estadísticas)
# NO: plugins binarios — solo los JSON de configuración de cada plugin
# NO: themes (grandes, se reinstalan) — solo appearance.json para saber cuál usar
PACKAGE_FILES["obsidian"]=\
"Documents/.obsidian/app.json|\
Documents/.obsidian/appearance.json|\
Documents/.obsidian/community-plugins.json|\
Documents/.obsidian/core-plugins.json|\
Documents/.obsidian/core-plugins-migration.json|\
Documents/.obsidian/hotkeys.json|\
Documents/.obsidian/snippets|\
Documents/.obsidian/plugins/dataview/data.json|\
Documents/.obsidian/plugins/obsidian-linter/settings.json|\
Documents/.obsidian/plugins/obsidian-minimal-settings/data.json|\
Documents/.obsidian/plugins/obsidian-style-settings/data.json|\
Documents/.obsidian/plugins/templater-obsidian/data.json|\
Documents/.obsidian/plugins/quickadd/data.json|\
Documents/.obsidian/plugins/obsidian-zotero-desktop-connector/data.json"

# calibre: configuración principal de la interfaz y comportamiento
# NO: caché de fonts (scanner_cache.json), historial, metadata-sources-cache
# NO: plugins binarios, store/, caches/
PACKAGE_FILES["calibre"]=\
".config/calibre/gui.json|\
.config/calibre/gui.py.json|\
.config/calibre/tweaks.json|\
.config/calibre/viewer.json|\
.config/calibre/viewer-webengine.json|\
.config/calibre/tts.json|\
.config/calibre/tweak_book_gui.json|\
.config/calibre/save_to_disk.py.json|\
.config/calibre/customize.py.json|\
.config/calibre/global.py.json"

# libreoffice: solo registrymodifications (tus personalizaciones de UI)
# NO: backup/, extensiones, uno_packages, temp, gallery, pack, basic, database
PACKAGE_FILES["libreoffice"]=\
".config/libreoffice/4/user/registrymodifications.xcu|\
.config/libreoffice/4/user/config/autotbl.fmt"

# xournalpp: solo settings.xml
PACKAGE_FILES["xournalpp"]=".config/xournalpp/settings.xml"

# kate: configuración del editor y tools externos
# NO: lspclient caché automático
PACKAGE_FILES["kate"]=\
".config/katerc|\
.config/kate/lspclient/settings.json|\
.config/kate/externaltools"

# texstudio: solo texstudio.ini (tu configuración del editor)
# NO: cache/ (enorme), completion/, templates/, packageCache.dat, lastSession, wordCount
PACKAGE_FILES["texstudio"]=".config/texstudio/texstudio.ini"

# lyx: solo preferences
PACKAGE_FILES["lyx"]=".config/lyx/preferences"

# okular: configuración del visor PDF
PACKAGE_FILES["okular"]=\
".config/okularrc|\
.config/okularpartrc"

# rstudio: solo rstudio-prefs.json (tus preferencias de editor)
# NO: cache, blobs, cookies, sessions, crashpad, GPU cache
PACKAGE_FILES["rstudio"]=".config/rstudio/rstudio-prefs.json"

# vlc: configuración del reproductor
PACKAGE_FILES["vlc"]=".config/vlc/vlcrc"

# krusader: configuración del file manager
PACKAGE_FILES["krusader"]=".config/krusaderrc"

# koreader: lector de ebooks — solo configuración de lectura personal
# NO: cache/ (enorme), history.lua (historial), screenshots/, ota/, data/dict
# NO: settings/statistics.sqlite3, vocabulary_builder.sqlite3
PACKAGE_FILES["koreader"]=\
".config/koreader/settings.reader.lua|\
.config/koreader/defaults.custom.lua|\
.config/koreader/settings/gestures.lua|\
.config/koreader/settings/hotkeys.lua|\
.config/koreader/settings/directory_defaults.lua"

# --- Patrones de datos sensibles a revisar antes de push --------------------
readonly SENSITIVE_PATTERNS=(
    "password"
    "secretKey"
    "apiKey"
    "api_key"
    "secret"
    "token"
    "passwd"
    "private_key"
)

# --- Archivos a revisar por datos sensibles -----------------------------------
# Rutas verificadas contra la estructura real del repo en Kubuntu 26.04.
# vscode renombrado a positron (Positron IDE, config en ~/.config/Positron/).
# zotero: el perfil 25vfdnq5.default es específico de esta instalación;
#         si cambia de máquina, actualizar el ID de perfil aquí.
readonly SENSITIVE_FILES_TO_CHECK=(
    "${DOTFILES_DIR}/zotero/.zotero/zotero/0xh8512f.default/prefs.js"  # ID de perfil de esta instalación
    "${DOTFILES_DIR}/git/.gitconfig"
    "${DOTFILES_DIR}/vscode/.config/Code/User/settings.json"
    "${DOTFILES_DIR}/positron/.config/Positron/User/settings.json"
)

# --- Colores para output (solo si el terminal los soporta) --------------------
# Se usan solo en funciones de UI, nunca en logs de archivo.
if tput colors &>/dev/null && [ "$(tput colors)" -ge 8 ]; then
    readonly COLOR_RESET='\033[0m'
    readonly COLOR_GREEN='\033[0;32m'
    readonly COLOR_YELLOW='\033[0;33m'
    readonly COLOR_RED='\033[0;31m'
    readonly COLOR_CYAN='\033[0;36m'
    readonly COLOR_BOLD='\033[1m'
else
    readonly COLOR_RESET=''
    readonly COLOR_GREEN=''
    readonly COLOR_YELLOW=''
    readonly COLOR_RED=''
    readonly COLOR_CYAN=''
    readonly COLOR_BOLD=''
fi