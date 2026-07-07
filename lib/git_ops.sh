#!/usr/bin/env bash
# =============================================================================
# lib/git_ops.sh — Operaciones Git para sincronización con GitHub
# =============================================================================
# Encapsula toda la interacción con Git. El repositorio de dotfiles tiene
# características especiales: los archivos son symlinks en $HOME, por lo que
# el flujo de trabajo es diferente a un repo de código normal.
#
# Flujos:
#   sync_push → commit de cambios + push a GitHub
#   sync_pull → pull desde GitHub + re-stow para aplicar cambios
#   show_git_status → estado legible del repo
# =============================================================================

# sync_push()
# Guarda los cambios locales del repositorio y los sube a GitHub.
# Incluye validación de datos sensibles antes del commit.
#
# Flujo completo:
#   1. Verificar que no hay datos sensibles
#   2. Mostrar qué archivos cambiaron (git status)
#   3. Pedir mensaje de commit
#   4. git add . && git commit && git push
sync_push() {
    log_section "Sincronizando cambios: laptop → GitHub"

    validate_git_installed    || return 1
    validate_dotfiles_dir     || return 1
    validate_git_configured   || log_warn "Continuando sin configuración de usuario Git..."

    cd "$DOTFILES_DIR" || return 1

    # Verificar datos sensibles ANTES de cualquier operación Git
    log_info "Verificando datos sensibles antes de subir..."
    if ! validate_no_sensitive_data; then
        log_error "Abortando push por datos sensibles detectados."
        log_error "Revisa los archivos indicados y elimina las credenciales."
        return 1
    fi

    # Mostrar estado actual antes de commitear
    log_info "Archivos con cambios:"
    git status --short

    # Verificar si hay algo que commitear
    if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
        log_info "No hay cambios para commitear. El repo está al día."
        return 0
    fi

    # Pedir mensaje de commit descriptivo
    local commit_message=""
    if [ "$DRY_RUN" = true ]; then
        commit_message="[dry-run] Simulación de commit"
    else
        # Solo preguntar si hay terminal disponible; en modo no interactivo
        # se usa el mensaje automático directamente.
        if [ -r /dev/tty ] && [ -w /dev/tty ]; then
            echo ""
            printf "  Mensaje de commit (Enter para mensaje automático): "
            read -r commit_message </dev/tty || commit_message=""
        fi
        if [ -z "$commit_message" ]; then
            commit_message="dotfiles: actualizar configuraciones - $(date '+%Y-%m-%d %H:%M')"
        fi
    fi

    confirm_action "¿Subir cambios a GitHub con mensaje: '${commit_message}'?" || return 0

    if [ "$DRY_RUN" = true ]; then
        log_info "[dry-run] Se ejecutaría: git add . && git commit -m '${commit_message}' && git push"
        return 0
    fi

    # Agregar todos los cambios
    log_step "1/3" "git add ."
    if ! git add .; then
        log_error "Falló git add. Verifica el estado del repositorio."
        return 1
    fi

    # Commitear
    log_step "2/3" "git commit"
    if ! git commit -m "$commit_message"; then
        log_error "Falló git commit."
        git reset HEAD 2>/dev/null || true  # Deshacer el add si el commit falla
        return 1
    fi

    # Push a la rama actual
    local current_branch
    current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'main')"
    log_step "3/3" "git push origin ${current_branch}"

    if ! validate_internet_connection; then
        log_warn "Sin conexión. El commit se guardó localmente."
        log_warn "Ejecuta 'sync-push' cuando tengas conexión para subir a GitHub."
        return 0
    fi

    if ! git push origin "$current_branch"; then
        log_error "Falló git push. El commit se guardó localmente."
        log_warn "Intenta de nuevo cuando tengas conexión con: git push origin ${current_branch}"
        return 1
    fi

    log_success "Cambios subidos a GitHub exitosamente."
    return 0
}

# sync_pull()
# Descarga los cambios más recientes de GitHub y los aplica.
# Después de un pull, re-aplica stow para que los nuevos archivos
# del repo tengan sus symlinks correspondientes.
#
# Flujo completo:
#   1. Verificar estado del árbol de trabajo
#   2. git pull
#   3. re-stow para aplicar nuevos archivos del repo
sync_pull() {
    log_section "Sincronizando desde GitHub: GitHub → laptop"

    validate_git_installed || return 1
    validate_dotfiles_dir  || return 1

    cd "$DOTFILES_DIR" || return 1

    # Advertir si hay cambios sin commitear que podrían perderse
    if ! validate_clean_working_tree; then
        log_warn "Hay cambios locales sin commitear."
        log_warn "Opciones:"
        log_warn "  1. Commitéalos primero con 'sync-push'"
        log_warn "  2. Guárdalos temporalmente con: git stash"
        log_warn "  3. Descártalos con: git checkout ."
        confirm_action "¿Continuar con el pull de todos modos? (riesgo de conflictos)" || return 0
    fi

    if ! validate_internet_connection; then
        log_error "Sin conexión a internet. No se puede hacer pull."
        return 1
    fi

    local current_branch
    current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'main')"

    log_step "1/2" "git pull origin ${current_branch}"

    if [ "$DRY_RUN" = true ]; then
        log_info "[dry-run] Se ejecutaría: git pull origin ${current_branch}"
        log_info "[dry-run] Se ejecutaría: stow -R en todos los paquetes"
        return 0
    fi

    if ! git pull origin "$current_branch"; then
        log_error "Falló git pull. Revisa conflictos con: git status"
        return 1
    fi

    log_success "Cambios descargados de GitHub."

    # Re-aplicar symlinks para que los nuevos archivos del repo queden activos
    log_step "2/2" "Actualizando symlinks de todos los paquetes"
    TARGET_PACKAGES=("${STOW_PACKAGES[@]}")
    if ! update_configs; then
        log_warn "Algunos symlinks no se actualizaron. Revisa el estado con 'estado'."
    fi

    log_success "Sincronización completa. La laptop está al día con GitHub."
    return 0
}

# show_git_status()
# Muestra el estado completo del repositorio Git de forma legible.
show_git_status() {
    log_section "Estado del repositorio Git"

    validate_git_installed || return 1
    validate_dotfiles_dir  || return 1

    cd "$DOTFILES_DIR" || return 1

    # Rama actual y estado respecto al remoto
    local current_branch
    current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'desconocida')"
    printf "  Rama actual:    ${COLOR_BOLD}%s${COLOR_RESET}\n" "$current_branch"

    # Último commit
    local last_commit
    last_commit="$(git log --oneline -1 2>/dev/null || echo 'sin commits')"
    printf "  Último commit:  %s\n" "$last_commit"

    # Estado respecto al remoto (si hay conexión)
    if validate_internet_connection 2>/dev/null; then
        git fetch --quiet 2>/dev/null || true
        local ahead behind
        ahead="$(git rev-list @{u}..HEAD --count 2>/dev/null || echo '?')"
        behind="$(git rev-list HEAD..@{u} --count 2>/dev/null || echo '?')"
        printf "  Adelante del remoto: %s commit(s)\n" "$ahead"
        printf "  Atrás del remoto:    %s commit(s)\n" "$behind"
    else
        printf "  ${COLOR_YELLOW}Estado remoto: sin conexión${COLOR_RESET}\n"
    fi

    echo ""
    # Archivos modificados
    local modified_count
    modified_count="$(git status --short | wc -l | tr -d ' ')"
    if [ "$modified_count" -gt 0 ]; then
        printf "  ${COLOR_YELLOW}Cambios pendientes (%s archivo(s)):${COLOR_RESET}\n" "$modified_count"
        git status --short | while IFS= read -r line; do
            printf "    %s\n" "$line"
        done
    else
        printf "  ${COLOR_GREEN}Árbol de trabajo limpio. Nada pendiente.${COLOR_RESET}\n"
    fi
}

# show_full_status()
# Combina estado de stow + estado de Git en una sola vista.
show_full_status() {
    show_stow_status
    show_git_status
    echo ""
    printf "  ${COLOR_BOLD}Directorio:${COLOR_RESET} %s\n" "$DOTFILES_DIR"
    printf "  ${COLOR_BOLD}Distro:${COLOR_RESET}     %s\n" "$DISTRO"
    printf "  ${COLOR_BOLD}Log:${COLOR_RESET}        %s\n\n" "$LOG_FILE"
}
