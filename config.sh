#!/usr/bin/env bash
# =============================================================================
# config.sh — Configuración centralizada del gestor de dotfiles
# =============================================================================
# FILOSOFÍA DE ARCHIVOS GESTIONADOS (principio de mínima captura):
#   Solo se versionan archivos de PERSONALIZACIÓN: aquello que el usuario
#   configuró manualmente y quiere reproducir en otra máquina.
#
#   Se excluyen SIEMPRE: caché, logs, locks, bases de datos, IDs de máquina,
#   credenciales, historial, listas MRU, posiciones/geometría de ventanas,
#   estado de sesión y cualquier archivo regenerable o dependiente del hardware.
#
#   Cada paquete tiene una lista explícita de qué archivos gestionar.
#   Si no está en la lista → no se toca. Así el repo permanece limpio.
#
# ARCHIVOS HÍBRIDOS (config + estado en el mismo archivo):
#   Algunas apps (KDE, TeXstudio) mezclan preferencias reales con algo de
#   estado en un mismo archivo. Se versionan solo cuando las preferencias
#   dominan; el churn residual es aceptable y se documenta en el README.
#   Los archivos donde el estado domina (digikamrc, krusaderrc, okularrc,
#   prefs.js de Zotero, registrymodifications.xcu de LibreOffice,
#   plasma-*appletsrc) quedaron EXCLUIDOS deliberadamente — ver README.
# =============================================================================

# --- Rutas principales -------------------------------------------------------
readonly DOTFILES_DIR="${DOTFILES_DIR:-$HOME/.dotfiles}"
readonly BACKUP_DIR="${DOTFILES_DIR}/.backups"
readonly LOG_DIR="${DOTFILES_DIR}/.logs"
readonly LOG_FILE="${LOG_DIR}/dotfiles-$(date '+%Y-%m-%d').log"

# --- Versión del proyecto -----------------------------------------------------
readonly VERSION="3.0.0"
readonly SCRIPT_NAME="dotfiles-manager"

# --- Detección de distribución ------------------------------------------------
# IMPORTANTE: NO usar 'source /etc/os-release' porque ese archivo define
# variables como VERSION, NAME, ID que colisionan con las nuestras al ser
# declaradas readonly. Leemos solo el campo ID con grep.
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
        readonly PKG_QUERY="dpkg -s"
        ;;
    *)
        readonly PKG_MANAGER="unknown"
        readonly PKG_INSTALL="echo 'Gestor de paquetes desconocido. Instala manualmente:'"
        readonly PKG_UPDATE="echo 'Gestor de paquetes desconocido.'"
        readonly PKG_QUERY="echo 'Gestor de paquetes desconocido.'"
        ;;
esac

# --- Paquetes gestionados -------------------------------------------------
# Lista canónica de todos los paquetes del repositorio.
# Convención: un paquete = una aplicación, nombrado igual que la app.
# Orden: los módulos base (shell, git) van primero.
# El layout de cada paquete es 100% compatible con GNU Stow
# (rutas relativas a $HOME dentro del directorio del paquete).
readonly STOW_PACKAGES=(
    git
    shell
    kde
    konsole
    positron      # Positron IDE (fork de VSCode); config en ~/.config/Positron/
    obsidian      # config del vault (~/Documents es el vault)
    meta          # recursos del vault: plantillas, scripts, dashboards (~/Documents/meta)
    calibre
    kate
    texstudio
    okular
    rstudio
    xournalpp
    koreader
)

# =============================================================================
# MAPA DE ARCHIVOS POR PAQUETE
# =============================================================================
# Define exactamente qué archivos gestiona cada paquete.
# Formato: PACKAGE_FILES["nombre"]="ruta1|ruta2|ruta3"
# Las rutas son RELATIVAS al directorio HOME del usuario.
# Una ruta puede ser un directorio: se gestiona completo (symlink de directorio).
#
# REGLAS de inclusión:
#   ✓ Preferencias, apariencia, temas, atajos, keybindings
#   ✓ Snippets, plantillas, scripts propios
#   ✓ Configuración de plugins (JSON/INI/TOML/Lua, no binarios)
#
# REGLAS de exclusión (nunca versionar):
#   ✗ Caché (Cache/, .cache/, *.sqlite, *.db), logs, locks
#   ✗ IDs de máquina, crashpad/, GPU cache, session storage
#   ✗ Credenciales (privateKey.pem, cert9.db, logins.json, contraseñas)
#   ✗ Historial, MRU, "recent files", posiciones de ventanas
#   ✗ Estado volátil (workspace.json de Obsidian, *-migration.json)
# =============================================================================
declare -A PACKAGE_FILES

# git: solo .gitconfig (sin credenciales — usar credential.helper)
PACKAGE_FILES["git"]=".gitconfig"

# shell: configuración del shell y del prompt.
# starship.toml vive en la ruta XDG estándar (~/.config/starship.toml).
# NOTA: .zshrc actual usa Oh My Zsh; starship queda disponible pero inactivo
# hasta agregar 'eval "$(starship init zsh)"' al .zshrc.
PACKAGE_FILES["shell"]=".zshrc|.config/starship.toml"

# kde: preferencias globales de KDE Plasma.
# Se versionan solo archivos dominados por preferencias:
#   kdeglobals        → tema, colores, fuentes (algo de estado residual, aceptable)
#   kglobalshortcutsrc→ atajos globales
#   kwinrc            → efectos y comportamiento del gestor de ventanas
#   dolphinrc         → preferencias del gestor de archivos
#   plasmarc          → tema de Plasma
#   plasma-localerc   → configuración regional
#   mimeapps.list     → aplicaciones predeterminadas
# EXCLUIDOS (estado/hardware): plasma-org.kde.plasma.desktop-appletsrc
# (layout de paneles, específico de pantalla), plasmashellrc (estado del
# shell por monitor), konsolesshconfig (estado de plugin).
PACKAGE_FILES["kde"]=\
".config/kdeglobals|\
.config/kglobalshortcutsrc|\
.config/kwinrc|\
.config/dolphinrc|\
.config/plasmarc|\
.config/plasma-localerc|\
.config/mimeapps.list"

# konsole: terminal de KDE. La personalización real vive en los PERFILES
# (~/.local/share/konsole/), no en konsolerc (que solo aporta DefaultProfile).
PACKAGE_FILES["konsole"]=\
".config/konsolerc|\
.local/share/konsole/achalmaedison.profile|\
.local/share/konsole/Nothing.colorscheme"

# positron: Positron IDE — solo settings. Agregar keybindings.json y
# snippets aquí cuando existan (hoy están vacíos/ausentes).
# NO: cache, gpu cache, crashpad, session storage, machine id, History/
PACKAGE_FILES["positron"]=".config/Positron/User/settings.json"

# obsidian: configuración del vault en ~/Documents/.obsidian/
# NO: workspace.json (estado de ventanas), vault-stats.json,
#     core-plugins-migration.json (estado de migración regenerable),
#     binarios de plugins (main.js/manifest.json se reinstalan),
#     themes/ (se reinstalan; appearance.json registra cuál usar)
PACKAGE_FILES["obsidian"]=\
"Documents/.obsidian/app.json|\
Documents/.obsidian/appearance.json|\
Documents/.obsidian/community-plugins.json|\
Documents/.obsidian/core-plugins.json|\
Documents/.obsidian/hotkeys.json|\
Documents/.obsidian/snippets|\
Documents/.obsidian/plugins/dataview/data.json|\
Documents/.obsidian/plugins/obsidian-minimal-settings/data.json|\
Documents/.obsidian/plugins/templater-obsidian/data.json|\
Documents/.obsidian/plugins/quickadd/data.json|\
Documents/.obsidian/plugins/obsidian-zotero-desktop-connector/data.json"

# meta: recursos de trabajo del vault (~/Documents/meta) — plantillas,
# scripts de automatización, dashboards y documentación del sistema.
# Se gestionan como symlinks de DIRECTORIO (el contenido evoluciona dentro).
# EXCLUIDOS: attachments/ (binarios), archivo/ (material archivado),
#            .claude/ (config local de Claude), templates/ (vacío hoy).
PACKAGE_FILES["meta"]=\
"Documents/meta/dataview|\
Documents/meta/javascript|\
Documents/meta/longform|\
Documents/meta/quickadd|\
Documents/meta/sistema|\
Documents/meta/tablero|\
Documents/meta/templater|\
Documents/meta/zotero|\
Documents/meta/readme.md"

# calibre: solo las preferencias estables de personalización.
# NO: caches/, conversion/, fonts/, plugins binarios, server-users.sqlite,
#     dynamic.pickle.json (estado interno)
# EXCLUIDOS tras auditoría: gui.json (geometría de ventanas + modelo del
# monitor = hardware) y gui.py.json (historial de búsquedas). Además calibre
# reescribe esos archivos de forma atómica y ROMPE los symlinks al usarlos.
PACKAGE_FILES["calibre"]=\
".config/calibre/global.py.json|\
.config/calibre/tweak_book_gui.json|\
.config/calibre/viewer-webengine.json"

# kate: configuración del editor, LSP y herramientas externas
PACKAGE_FILES["kate"]=\
".config/katerc|\
.config/kate/lspclient/settings.json|\
.config/kate/externaltools"

# texstudio: texstudio.ini es un archivo HÍBRIDO: contiene toda la
# configuración del editor (atajos, toolbars, compilación) pero también
# algo de estado (último documento, geometría). Se versiona porque las
# preferencias dominan y no hay forma de separarlas. Churn menor esperado.
# NO: cache/, completion/, packageCache.dat, lastSession
PACKAGE_FILES["texstudio"]=".config/texstudio/texstudio.ini"

# okular: SOLO okularpartrc (preferencias de visualización).
# EXCLUIDO: okularrc (dominado por "Recent Files" y geometría de ventana).
PACKAGE_FILES["okular"]=".config/okularpartrc"

# rstudio: solo rstudio-prefs.json (preferencias del editor)
# NO: cache, blobs, cookies, sessions, crashpad, GPU cache
PACKAGE_FILES["rstudio"]=".config/rstudio/rstudio-prefs.json"

# xournalpp: solo settings.xml. palettes/ y plugins/ están vacíos hoy;
# agregarlos aquí si algún día contienen material propio.
PACKAGE_FILES["xournalpp"]=".config/xournalpp/settings.xml"

# koreader: lector de ebooks — solo configuración de lectura personal.
# defaults.custom.lua es el mecanismo oficial de KOReader para overrides
# persistentes del usuario: eso es lo que se versiona.
# EXCLUIDO tras auditoría: settings.reader.lua (lastfile/MRU + geometría;
# KOReader lo reescribe en cada uso y rompe el symlink).
# NO: cache/, history.lua, screenshots/, ota/, data/dict,
#     settings/statistics.sqlite3, vocabulary_builder.sqlite3
PACKAGE_FILES["koreader"]=\
".config/koreader/defaults.custom.lua|\
.config/koreader/settings/gestures.lua|\
.config/koreader/settings/hotkeys.lua|\
.config/koreader/settings/directory_defaults.lua"

# --- Patrones de datos sensibles a revisar antes de push --------------------
# Patrones tipo clave=valor para reducir falsos positivos: buscan la palabra
# seguida de separador y un valor no vacío, no la palabra suelta.
readonly SENSITIVE_PATTERNS=(
    '(password|passwd|contrasena)[[:space:]"'"'"']*[=:][[:space:]"'"'"']*[^[:space:]"'"'"']{4,}'
    '(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)[[:space:]"'"'"']*[=:][[:space:]"'"'"']*[A-Za-z0-9_/+.-]{8,}'
    'BEGIN[[:space:]](RSA|OPENSSH|EC|DSA|PGP)[[:space:]]PRIVATE[[:space:]]KEY'
    'ghp_[A-Za-z0-9]{20,}'
    'sk-[A-Za-z0-9_-]{20,}'
)

# Archivos versionados que NUNCA deben disparar el escáner (falsos positivos
# conocidos y revisados manualmente). Rutas relativas al repo.
readonly SENSITIVE_SCAN_ALLOWLIST=(
    # ejemplo: "kate/.config/katerc"
)

# --- Colores para output (solo si el terminal los soporta) --------------------
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
