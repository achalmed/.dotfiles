#!/usr/bin/env bash
# =============================================================================
# lib/validator.sh — Validación de entorno y entradas
# =============================================================================
# Todas las validaciones ocurren ANTES de ejecutar cualquier lógica.
# Fallar rápido con mensajes claros es mejor que fallar silenciosamente
# a mitad de una operación que ya modificó archivos.
# =============================================================================

# validate_dotfiles_dir()
# Verifica que el directorio de dotfiles exista y sea un repositorio Git.
# Es el prerequisito más básico: sin él, ninguna operación tiene sentido.
#
# Returns:
#   0 si el directorio es válido
#   1 si no existe o no es un repo Git
validate_dotfiles_dir() {
    if [ ! -d "$DOTFILES_DIR" ]; then
        log_error "El directorio de dotfiles no existe: ${DOTFILES_DIR}"
        log_error "Clona tu repositorio primero con: git clone <url> ${DOTFILES_DIR}"
        return 1
    fi

    if [ ! -d "${DOTFILES_DIR}/.git" ]; then
        log_warn "El directorio ${DOTFILES_DIR} no es un repositorio Git."
        log_warn "Las operaciones de sincronización con GitHub no estarán disponibles."
        # No es un error fatal; algunas operaciones locales pueden continuar
    fi

    return 0
}

# validate_stow_installed()
# Verifica que GNU Stow esté instalado antes de cualquier operación de enlaces.
#
# Returns:
#   0 si stow está instalado
#   1 si no está instalado
validate_stow_installed() {
    if ! command -v stow &>/dev/null; then
        log_error "GNU Stow no está instalado."
        case "$DISTRO" in
            arch | archcraft | manjaro)
                log_error "Instálalo con: sudo pacman -S stow"
                ;;
            ubuntu | kubuntu | debian)
                log_error "Instálalo con: sudo apt install stow"
                ;;
            *)
                log_error "Instálalo usando el gestor de paquetes de tu distro."
                ;;
        esac
        return 1
    fi
    return 0
}

# validate_git_installed()
# Verifica que Git esté instalado.
#
# Returns:
#   0 si git está instalado
#   1 si no lo está
validate_git_installed() {
    if ! command -v git &>/dev/null; then
        log_error "Git no está instalado. Es necesario para sincronizar con GitHub."
        return 1
    fi
    return 0
}

# validate_git_configured()
# Verifica que Git tenga nombre de usuario y email configurados.
# Sin esto, los commits fallan de forma confusa.
#
# Returns:
#   0 si git está configurado
#   1 si faltan configuraciones
validate_git_configured() {
    local git_name
    local git_email
    git_name="$(git config --global user.name 2>/dev/null || echo '')"
    git_email="$(git config --global user.email 2>/dev/null || echo '')"

    if [ -z "$git_name" ] || [ -z "$git_email" ]; then
        log_warn "Git no tiene usuario/email configurado globalmente."
        log_warn "Esto puede causar errores al hacer commits."
        log_warn "Configúralo con:"
        log_warn "  git config --global user.name 'Tu Nombre'"
        log_warn "  git config --global user.email 'tu@email.com'"
        return 1
    fi
    return 0
}

# validate_stow_package_exists()
# Verifica que un paquete stow concreto exista en el repositorio.
#
# Arguments:
#   $1 - Nombre del paquete stow a verificar
#
# Returns:
#   0 si el directorio del paquete existe
#   1 si no existe
validate_stow_package_exists() {
    local package="$1"
    if [ ! -d "${DOTFILES_DIR}/${package}" ]; then
        log_warn "El paquete stow '${package}' no existe en ${DOTFILES_DIR}/"
        return 1
    fi
    return 0
}

# validate_no_sensitive_data()
# Escanea archivos de configuración en busca de datos sensibles antes de
# hacer commit. Evita exponer accidentalmente credenciales en GitHub.
#
# Returns:
#   0 si no se encontraron datos sensibles
#   1 si se encontraron posibles datos sensibles
validate_no_sensitive_data() {
    local found_sensitive=0
    local pattern
    local file

    log_info "Escaneando archivos versionados en busca de datos sensibles..."

    cd "$DOTFILES_DIR" || return 1

    # Archivos rastreados + nuevos sin ignorar (lo que subiría un 'git add .')
    while IFS= read -r file; do
        [ -f "$file" ] || continue

        # Saltar archivos en la allowlist (falsos positivos revisados)
        local allowed=false
        local allowed_file
        for allowed_file in "${SENSITIVE_SCAN_ALLOWLIST[@]}"; do
            if [ "$file" = "$allowed_file" ]; then
                allowed=true
                break
            fi
        done
        if $allowed; then
            continue
        fi

        # Saltar archivos binarios
        grep -qI . "$file" 2>/dev/null || continue

        for pattern in "${SENSITIVE_PATTERNS[@]}"; do
            if grep -qiE "$pattern" "$file" 2>/dev/null; then
                log_warn "Posible dato sensible en: ${file}"
                log_warn "  patrón: ${pattern}"
                found_sensitive=1
                break
            fi
        done
    done < <(git ls-files --cached --others --exclude-standard 2>/dev/null)

    if [ "$found_sensitive" -eq 1 ]; then
        log_error "Se encontraron posibles datos sensibles. Revisa los archivos antes de hacer commit."
        log_error "Si es un falso positivo revisado, agrégalo a SENSITIVE_SCAN_ALLOWLIST en config.sh."
        return 1
    fi

    log_success "No se encontraron datos sensibles en los archivos versionados."
    return 0
}

# validate_internet_connection()
# Verifica conectividad básica a GitHub antes de operaciones de red.
# Usa un ping silencioso para no depender de curl/wget.
#
# Returns:
#   0 si hay conexión
#   1 si no hay conexión
validate_internet_connection() {
    if ! ping -c 1 -W 3 github.com &>/dev/null; then
        log_warn "No se detectó conexión a internet o acceso a GitHub."
        log_warn "Las operaciones de sincronización remota no estarán disponibles."
        return 1
    fi
    return 0
}

# validate_clean_working_tree()
# Verifica que no haya cambios sin commitear en el repositorio.
# Útil antes de operaciones de pull para evitar conflictos.
#
# Returns:
#   0 si el árbol de trabajo está limpio
#   1 si hay cambios pendientes
validate_clean_working_tree() {
    cd "$DOTFILES_DIR" || return 1

    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        log_warn "Hay cambios no commiteados en el repositorio de dotfiles."
        return 1
    fi
    return 0
}
