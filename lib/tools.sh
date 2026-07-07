#!/usr/bin/env bash
# =============================================================================
# lib/tools.sh — Backup quirúrgico, instalación de dependencias y utilidades
# =============================================================================
# Dos modos de backup:
#   - Quirúrgico (default): solo respalda los archivos del paquete en trabajo.
#     Rápido, liviano, específico. Se activa automáticamente antes de adopt/install.
#   - Completo (--full):    respalda todo ~/.config, ~/.zotero, etc.
#     Lento, pesado (145MB+). Solo bajo petición explícita.
# =============================================================================

# _resolve_package_paths()
# Dado un nombre de paquete stow, devuelve la lista de rutas reales en $HOME
# que ese paquete gestiona (los archivos que stow linkearía).
# Esto permite hacer backup quirúrgico: solo lo que va a cambiar.
#
# Arguments:
#   $1 - Nombre del paquete stow
#
# Outputs (stdout):
#   Una ruta por línea — rutas absolutas en $HOME
_resolve_package_paths() {
    local pkg_name="$1"
    local pkg_dir="${DOTFILES_DIR}/${pkg_name}"

    [ -d "$pkg_dir" ] || return 0

    # Iterar sobre cada archivo del paquete y calcular su ruta en HOME
    find "$pkg_dir" -type f ! -name ".gitkeep" ! -name ".directory" 2>/dev/null | \
    while IFS= read -r repo_file; do
        local relative="${repo_file#"${pkg_dir}"/}"
        local home_path="${HOME}/${relative}"
        # Emitir la ruta solo si existe en HOME (sea archivo real o symlink)
        if [ -e "$home_path" ] || [ -L "$home_path" ]; then
            echo "$home_path"
        fi
    done
}

# create_backup()
# Crea un backup de las configuraciones antes de una operación.
# Por defecto es QUIRÚRGICO: solo respalda los archivos de los paquetes
# que se van a modificar. Mucho más rápido y liviano que el backup completo.
#
# Arguments:
#   $1 - Prefijo del backup (ej: "pre-install", "pre-adopt", "manual")
#   $2 - Modo: "quirurgico" (default) | "completo"
#   $@ - Nombres de paquetes a respaldar (solo en modo quirúrgico)
#
# Returns:
#   0 si el backup se creó correctamente
#   1 si falló
create_backup() {
    local prefix="${1:-manual}"
    local mode="${2:-quirurgico}"
    shift 2 2>/dev/null || true
    local packages=("$@")

    local timestamp
    timestamp="$(date '+%Y%m%d_%H%M%S')"
    local backup_name="${prefix}_${timestamp}"
    local backup_path="${BACKUP_DIR}/${backup_name}"

    if [ "$DRY_RUN" = true ]; then
        log_info "[dry-run] Se crearía backup ${mode}: ${backup_path}.tar.gz"
        return 0
    fi

    mkdir -p "$BACKUP_DIR" || {
        log_error "No se pudo crear el directorio de backups: ${BACKUP_DIR}"
        return 1
    }

    if [ "$mode" = "completo" ]; then
        _create_full_backup "$backup_path"
    else
        _create_surgical_backup "$backup_path" "${packages[@]}"
    fi
}

# _create_surgical_backup()
# Backup liviano: solo los archivos de los paquetes especificados.
# Ideal para uso automático antes de adopt/install de paquetes concretos.
# Un backup de "git" ocupa KB, no MB.
#
# Arguments:
#   $1        - Ruta base del backup (sin extensión)
#   $@ (rest) - Nombres de paquetes a respaldar
_create_surgical_backup() {
    local backup_path="$1"
    shift
    local packages=("$@")

    if [ ${#packages[@]} -eq 0 ]; then
        log_warn "Backup quirúrgico sin paquetes especificados — omitiendo."
        return 0
    fi

    local backup_name
    backup_name="$(basename "$backup_path")"
    local pkg_label
    pkg_label="$(IFS='+'; echo "${packages[*]}")"
    log_info "Creando backup quirúrgico [${pkg_label}]: ${backup_name}.tar.gz"

    # Recolectar todas las rutas HOME de los paquetes
    local files_to_backup=()
    for pkg in "${packages[@]}"; do
        while IFS= read -r path; do
            [ -n "$path" ] && files_to_backup+=("$path")
        done < <(_resolve_package_paths "$pkg")
    done

    if [ ${#files_to_backup[@]} -eq 0 ]; then
        log_info "No hay archivos actuales en HOME para respaldar de [${pkg_label}]."
        log_info "(Normal si es la primera instalación de este paquete)"
        return 0
    fi

    if tar -czf "${backup_path}.tar.gz" \
        --warning=no-file-changed \
        "${files_to_backup[@]}" 2>/dev/null; then
        local size
        size="$(du -sh "${backup_path}.tar.gz" 2>/dev/null | cut -f1)"
        log_success "Backup quirúrgico creado: ${backup_name}.tar.gz (${size})"
    else
        [ -f "${backup_path}.tar.gz" ] && \
            log_warn "Backup creado con advertencias menores." || \
            { log_error "Falló el backup quirúrgico."; return 1; }
    fi

    _cleanup_old_backups
    return 0
}

# _create_full_backup()
# Backup completo de toda la configuración del sistema.
# Útil antes de migraciones grandes o reinstalaciones.
# Puede pesar 100MB+. Solo se llama bajo petición explícita.
#
# Arguments:
#   $1 - Ruta base del backup (sin extensión)
_create_full_backup() {
    local backup_path="$1"
    local backup_name
    backup_name="$(basename "$backup_path")"

    log_warn "Backup COMPLETO solicitado — puede tardar y ocupar mucho espacio."
    log_info "Creando backup completo: ${backup_name}.tar.gz"

    local dirs_to_backup=()
    local candidates=(
        "$HOME/.config"
        "$HOME/.gitconfig"
        "$HOME/.zshrc"
        "$HOME/.local/share/konsole"
        "$HOME/Documents/meta"
        "$HOME/Documents/.obsidian"
    )
    for d in "${candidates[@]}"; do
        [ -e "$d" ] && dirs_to_backup+=("$d")
    done

    if [ ${#dirs_to_backup[@]} -eq 0 ]; then
        log_warn "No se encontraron directorios para respaldar."
        return 0
    fi

    # Crear el archivo tar excluyendo directorios muy grandes (caché, etc.)
    if tar -czf "${backup_path}.tar.gz" \
        --exclude="*/cache/*" \
        --exclude="*/Cache/*" \
        --exclude="*/.cache/*" \
        --exclude="*/CacheStorage/*" \
        --exclude="*/GPUCache/*" \
        --exclude="*/caches/*" \
        --warning=no-file-changed \
        "${dirs_to_backup[@]}" 2>/dev/null; then
        local size
        size="$(du -sh "${backup_path}.tar.gz" 2>/dev/null | cut -f1)"
        log_success "Backup completo creado: ${backup_name}.tar.gz (${size})"
    else
        # tar puede retornar código no-cero si algunos archivos cambiaron durante
        # la copia (código 1 = advertencia, no error crítico)
        [ -f "${backup_path}.tar.gz" ] && \
            log_warn "Backup completo creado con advertencias." || \
            { log_error "Falló el backup completo."; return 1; }
    fi
    # Limpiar backups viejos automáticamente
    _cleanup_old_backups
}

# _cleanup_old_backups()
# Elimina backups antiguos manteniendo solo los últimos 15.
# Así el directorio .backups no crece indefinidamente.
_cleanup_old_backups() {
    local max_backups=15
    local backup_count
    backup_count="$(find "$BACKUP_DIR" -name "*.tar.gz" 2>/dev/null | wc -l)"

    if [ "$backup_count" -gt "$max_backups" ]; then
        local to_delete=$(( backup_count - max_backups ))
        log_info "Limpiando ${to_delete} backup(s) antiguo(s) (límite: ${max_backups})..."
        find "$BACKUP_DIR" -name "*.tar.gz" -printf '%T+ %p\n' 2>/dev/null | \
            sort | head -n "$to_delete" | cut -d' ' -f2- | \
            xargs rm -f 2>/dev/null || true
    fi
}

# list_backups()
# Muestra todos los backups disponibles con tamaño y fecha.
list_backups() {
    log_section "Backups disponibles"

    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        log_info "No hay backups en: ${BACKUP_DIR}"
        return 0
    fi

    printf "  %-50s %-8s %s\n" "Nombre" "Tamaño" "Fecha"
    printf "  %s\n" "────────────────────────────────────────────────────────────────────"

    find "$BACKUP_DIR" -name "*.tar.gz" -printf '%T@ %f\n' 2>/dev/null | \
        sort -rn | \
        while read -r _ filename; do
            local filepath="${BACKUP_DIR}/${filename}"
            local size
            size="$(du -sh "$filepath" 2>/dev/null | cut -f1)"
            local date_str
            date_str="$(stat -c '%y' "$filepath" 2>/dev/null | cut -d'.' -f1)"
            printf "  %-50s %-8s %s\n" "$filename" "$size" "$date_str"
        done

    echo ""
    local total_size
    total_size="$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
    printf "  Total en disco: %s  |  Directorio: %s\n" "$total_size" "$BACKUP_DIR"
}

# install_dependencies()
# Instala todas las dependencias necesarias según la distro detectada.
# Maneja los casos especiales como starship (no está en repos de Ubuntu).
install_dependencies() {
    log_section "Instalando dependencias del sistema"
    log_info "Distro detectada: ${DISTRO}"

    if [ "$DRY_RUN" = true ]; then
        log_info "[dry-run] Se instalarían dependencias para: ${DISTRO}"
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
            log_warn "Distro '${DISTRO}' no reconocida."
            log_warn "Instala manualmente: stow git zsh"
            return 1
            ;;
    esac
}

# _install_deps_arch()
# Instala dependencias en Arch Linux y derivados (pacman).
_install_deps_arch() {
    sudo pacman -Sy --noconfirm 2>/dev/null || log_warn "No se pudo actualizar pacman"
    local packages=("stow" "git" "zsh" "starship" "curl")
    local to_install=()
    for pkg in "${packages[@]}"; do
        if ! pacman -Q "$pkg" &>/dev/null; then
            to_install+=("$pkg")
            log_info "  → pendiente: ${pkg}"
        else
            log_success "  ✓ ya instalado: ${pkg}"
        fi
    done
    [ ${#to_install[@]} -gt 0 ] && sudo pacman -S --noconfirm "${to_install[@]}"
    log_success "Dependencias Arch instaladas."
    _post_install_zsh
}

# _install_deps_apt()
# Instala dependencias en Ubuntu/Kubuntu y derivados (apt).
# Starship requiere instalación separada via curl (no está en repos oficiales).
_install_deps_apt() {
    sudo apt update -qq || log_warn "No se pudo actualizar apt"
    local packages=("stow" "git" "zsh" "curl")
    local to_install=()
    for pkg in "${packages[@]}"; do
        if ! dpkg -s "$pkg" &>/dev/null; then
            to_install+=("$pkg")
            log_info "  → pendiente: ${pkg}"
        else
            log_success "  ✓ ya instalado: ${pkg}"
        fi
    done
    [ ${#to_install[@]} -gt 0 ] && sudo apt install -y "${to_install[@]}"
    # Starship no está en repos de Ubuntu
    if ! command -v starship &>/dev/null; then
        log_info "Instalando Starship via script oficial..."
        curl -sS https://starship.rs/install.sh | sh -s -- --yes && \
            log_success "Starship instalado." || \
            log_warn "Instala Starship manualmente: https://starship.rs"
    else
        log_success "  ✓ ya instalado: starship"
    fi
    log_success "Dependencias Kubuntu instaladas."
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
        if confirm_action "¿Cambiar shell predeterminado a Zsh?"; then
            chsh -s "$(which zsh)" && \
                log_success "Shell cambiado a Zsh. Reinicia la sesión." || \
                log_warn "Hazlo manualmente: chsh -s $(which zsh)"
        fi
    else
        log_success "  ✓ Zsh ya es el shell predeterminado."
    fi
}