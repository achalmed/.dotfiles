#!/usr/bin/env bash
# =============================================================================
# lib/tools.sh — Backup, instalación de dependencias y utilidades
# =============================================================================
# Agrupa operaciones auxiliares que no encajan en stow_ops ni git_ops pero
# son esenciales para la gestión segura de dotfiles:
#   - Backups antes de operaciones destructivas
#   - Instalación de dependencias según la distro
#   - Limpieza de backups antiguos
# =============================================================================

# create_backup()
# Crea un backup comprimido de las configuraciones actuales de la laptop
# (los archivos reales, no los symlinks) antes de operaciones potencialmente
# destructivas. Los backups se guardan en DOTFILES_DIR/.backups/
#
# Arguments:
#   $1 - Prefijo del backup (ej: "pre-install", "pre-adopt", "manual")
#
# Returns:
#   0 si el backup se creó correctamente
#   1 si falló
create_backup() {
    local prefix="${1:-manual}"
    local timestamp
    timestamp="$(date '+%Y%m%d_%H%M%S')"
    local backup_name="${prefix}_${timestamp}"
    local backup_path="${BACKUP_DIR}/${backup_name}"

    if [ "$DRY_RUN" = true ]; then
        log_info "[dry-run] Se crearía backup en: ${backup_path}.tar.gz"
        return 0
    fi

    mkdir -p "$BACKUP_DIR" || {
        log_error "No se pudo crear el directorio de backups: ${BACKUP_DIR}"
        return 1
    }

    log_info "Creando backup: ${backup_name}.tar.gz"

    # Recolectar archivos reales (no symlinks) que serían afectados por stow
    # Buscamos en los directorios de configuración más comunes
    local dirs_to_backup=(
        "$HOME/.config"
        "$HOME/.zotero"
        "$HOME/.gitconfig"
        "$HOME/.zshrc"
        "$HOME/.lyx"
    )

    local existing_dirs=()
    for dir in "${dirs_to_backup[@]}"; do
        [ -e "$dir" ] && existing_dirs+=("$dir")
    done

    if [ ${#existing_dirs[@]} -eq 0 ]; then
        log_warn "No se encontraron directorios de configuración para respaldar."
        return 0
    fi

    # Crear el archivo tar excluyendo directorios muy grandes (caché, etc.)
    if tar -czf "${backup_path}.tar.gz" \
        --exclude="**/cache/**" \
        --exclude="**/Cache/**" \
        --exclude="**/.cache/**" \
        --exclude="**/CacheStorage/**" \
        --exclude="**/GPUCache/**" \
        --warning=no-file-changed \
        "${existing_dirs[@]}" 2>/dev/null; then
        local size
        size="$(du -sh "${backup_path}.tar.gz" 2>/dev/null | cut -f1)"
        log_success "Backup creado: ${backup_name}.tar.gz (${size})"
    else
        # tar puede retornar código no-cero si algunos archivos cambiaron durante
        # la copia (código 1 = advertencia, no error crítico)
        if [ -f "${backup_path}.tar.gz" ]; then
            log_warn "Backup creado con advertencias (normal si configs estaban en uso)."
        else
            log_error "Falló la creación del backup."
            return 1
        fi
    fi

    # Limpiar backups viejos automáticamente (mantener los últimos 10)
    _cleanup_old_backups
    return 0
}

# _cleanup_old_backups()
# Elimina backups antiguos manteniendo solo los últimos 10.
# Así el directorio .backups no crece indefinidamente.
_cleanup_old_backups() {
    local max_backups=10
    local backup_count
    backup_count="$(find "$BACKUP_DIR" -name "*.tar.gz" 2>/dev/null | wc -l)"

    if [ "$backup_count" -gt "$max_backups" ]; then
        local to_delete=$(( backup_count - max_backups ))
        log_info "Limpiando ${to_delete} backup(s) antiguo(s)..."
        # Elimina los más viejos (orden por fecha de modificación)
        find "$BACKUP_DIR" -name "*.tar.gz" -printf '%T+ %p\n' 2>/dev/null | \
            sort | head -n "$to_delete" | cut -d' ' -f2- | \
            xargs rm -f 2>/dev/null || true
    fi
}

# list_backups()
# Muestra todos los backups disponibles con su tamaño y fecha.
list_backups() {
    log_section "Backups disponibles"

    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        log_info "No hay backups disponibles en: ${BACKUP_DIR}"
        return 0
    fi

    printf "  %-45s %-10s %s\n" "Nombre" "Tamaño" "Fecha"
    printf "  %s\n" "────────────────────────────────────────────────────────────────"

    find "$BACKUP_DIR" -name "*.tar.gz" -printf '%T@ %f\n' 2>/dev/null | \
        sort -rn | \
        while read -r _ filename; do
            local filepath="${BACKUP_DIR}/${filename}"
            local size
            size="$(du -sh "$filepath" 2>/dev/null | cut -f1)"
            local date_str
            date_str="$(stat -c '%y' "$filepath" 2>/dev/null | cut -d'.' -f1)"
            printf "  %-45s %-10s %s\n" "$filename" "$size" "$date_str"
        done
}

# install_dependencies()
# Instala todas las dependencias necesarias según la distro detectada.
# Maneja los casos especiales como starship (no está en repos de Ubuntu).
install_dependencies() {
    log_section "Instalando dependencias del sistema"
    log_info "Distro detectada: ${DISTRO}"

    if [ "$DRY_RUN" = true ]; then
        log_info "[dry-run] Se instalarían las dependencias para: ${DISTRO}"
        return 0
    fi

    case "$DISTRO" in
        arch | archcraft | endeavouros | manjaro)
            _install_deps_arch
            ;;
        ubuntu | kubuntu | debian | linuxmint | pop)
            _install_deps_apt
            ;;
        *)
            log_warn "Distro '${DISTRO}' no reconocida. Instalando paquetes base manualmente..."
            log_warn "Necesitas: stow git zsh"
            return 1
            ;;
    esac
}

# _install_deps_arch()
# Instala dependencias en Arch Linux y derivados (pacman).
_install_deps_arch() {
    log_info "Actualizando repositorios de pacman..."
    sudo pacman -Sy --noconfirm 2>/dev/null || log_warn "No se pudo actualizar la base de datos de pacman"

    local packages_arch=("stow" "git" "zsh" "starship" "curl" "wget")
    local to_install=()

    for pkg in "${packages_arch[@]}"; do
        if ! pacman -Q "$pkg" &>/dev/null; then
            to_install+=("$pkg")
            log_info "  → Pendiente de instalar: ${pkg}"
        else
            log_success "  ✓ Ya instalado: ${pkg}"
        fi
    done

    if [ ${#to_install[@]} -gt 0 ]; then
        log_info "Instalando: ${to_install[*]}"
        sudo pacman -S --noconfirm "${to_install[@]}" || {
            log_error "Falló la instalación de algunos paquetes."
            return 1
        }
    fi

    log_success "Dependencias de Arch instaladas correctamente."
    _post_install_zsh
}

# _install_deps_apt()
# Instala dependencias en Ubuntu/Kubuntu y derivados (apt).
# Starship requiere instalación separada via curl (no está en repos oficiales).
_install_deps_apt() {
    log_info "Actualizando lista de paquetes..."
    sudo apt update -qq || log_warn "No se pudo actualizar la lista de paquetes"

    local packages_apt=("stow" "git" "zsh" "curl" "wget")
    local to_install=()

    for pkg in "${packages_apt[@]}"; do
        if ! dpkg -l "$pkg" &>/dev/null; then
            to_install+=("$pkg")
            log_info "  → Pendiente de instalar: ${pkg}"
        else
            log_success "  ✓ Ya instalado: ${pkg}"
        fi
    done

    if [ ${#to_install[@]} -gt 0 ]; then
        log_info "Instalando: ${to_install[*]}"
        sudo apt install -y "${to_install[@]}" || {
            log_error "Falló la instalación de algunos paquetes."
            return 1
        }
    fi

    # Starship: instalación especial via script oficial
    if ! command -v starship &>/dev/null; then
        log_info "Instalando Starship (no disponible en repos de Ubuntu)..."
        if curl -sS https://starship.rs/install.sh | sh -s -- --yes; then
            log_success "Starship instalado correctamente."
        else
            log_warn "No se pudo instalar Starship automáticamente."
            log_warn "Instálalo manualmente desde: https://starship.rs"
        fi
    else
        log_success "  ✓ Ya instalado: starship"
    fi

    log_success "Dependencias de Kubuntu/Ubuntu instaladas correctamente."
    _post_install_zsh
}

# _post_install_zsh()
# Configura Zsh como shell predeterminado si aún no lo es.
# Se hace después de instalar las dependencias porque Zsh debe existir
# antes de poder usarlo como shell predeterminado.
_post_install_zsh() {
    local current_shell
    current_shell="$(basename "$SHELL")"

    if [ "$current_shell" != "zsh" ]; then
        log_info "Configurando Zsh como shell predeterminado..."
        if confirm_action "¿Cambiar tu shell predeterminado a Zsh?"; then
            if chsh -s "$(which zsh)"; then
                log_success "Shell cambiado a Zsh. Reinicia tu sesión para aplicar."
            else
                log_warn "No se pudo cambiar el shell. Hazlo manualmente con: chsh -s $(which zsh)"
            fi
        fi
    else
        log_success "  ✓ Zsh ya es el shell predeterminado."
    fi
}
