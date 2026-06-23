#!/usr/bin/env bash
# =============================================================================
# config.sh — Configuración centralizada del gestor de dotfiles
# =============================================================================
# Todas las constantes y rutas globales están aquí para que cualquier cambio
# de entorno (nueva máquina, nueva distro) solo requiera editar este archivo.
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
detect_distro() {
    if [ -f /etc/os-release ]; then
        # shellcheck source=/dev/null
        source /etc/os-release
        echo "${ID:-unknown}"
    else
        echo "unknown"
    fi
}
readonly DISTRO
DISTRO="$(detect_distro)"

# --- Gestor de paquetes por distro --------------------------------------------
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
readonly STOW_PACKAGES=(
    git
    shell
    kde
    terminal
    digikam
    vscode
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
)

# --- Archivos/directorios a excluir del análisis de datos sensibles -----------
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
readonly SENSITIVE_FILES_TO_CHECK=(
    "${DOTFILES_DIR}/zotero/.zotero/zotero/25vfdnq5.default/prefs.js"
    "${DOTFILES_DIR}/git/.gitconfig"
    "${DOTFILES_DIR}/vscode/.config/Code/User/settings.json"
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
