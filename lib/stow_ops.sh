#!/usr/bin/env bash
# =============================================================================
# lib/stow_ops.sh — Operaciones de GNU Stow para gestión de symlinks
# =============================================================================
# Flujos principales:
#   install_configs  → repo  → laptop  (stow)
#   adopt_configs    → laptop → repo   (stow --adopt)
#   update_configs   → re-stow symlinks existentes
#   remove_configs   → eliminar symlinks (stow -D)
#   show_stow_status → vista de estado, compacta o detallada
# =============================================================================

# _is_stow_symlink()
# Determina si una ruta en HOME es un symlink gestionado por stow
# que apunta al repositorio de dotfiles.
#
# Stow puede crear symlinks RELATIVOS (ej: "../../.dotfiles/git/.gitconfig")
# o ABSOLUTOS. Ambos son válidos; debemos resolver el destino real antes
# de comparar con DOTFILES_DIR.
#
# Arguments:
#   $1 - Ruta del symlink a verificar
#
# Returns:
#   0 si es un symlink de stow apuntando a DOTFILES_DIR
#   1 si no lo es
_is_stow_symlink() {
    local path="$1"
    [ -L "$path" ] || return 1

    # readlink -f resuelve rutas relativas y cadenas de symlinks a ruta absoluta
    local real_target
    real_target="$(readlink -f "$path" 2>/dev/null)" || return 1

    # Verificar que el destino real vive dentro del repo de dotfiles
    [[ "$real_target" == "${DOTFILES_DIR}"/* ]]
}

# _run_stow()
# Función base: ejecuta stow con el modo indicado sobre una lista de paquetes.
# Maneja dry-run, verbose y reporta errores con diagnóstico específico.
#
# Arguments:
#   $1 - Modo: "" (instalar) | "--adopt" | "-R" (restow) | "-D" (delete)
#   $@ - Paquetes a procesar
#
# Returns:
#   0 si todos los paquetes se procesaron correctamente
#   1 si alguno falló
_run_stow() {
    local stow_mode="$1"
    shift
    local packages=("$@")
    local failed=0
    local stow_flags=()
    local description=""

    # Construir flags según modo
    case "$stow_mode" in
        "--adopt") description="Adoptando (laptop → repo)"; stow_flags=("--adopt") ;;
        "-R")      description="Actualizando symlinks";      stow_flags=("-R") ;;
        "-D")      description="Eliminando symlinks";        stow_flags=("-D") ;;
        "")        description="Instalando (repo → laptop)"; stow_flags=() ;;
        *)
            log_error "Modo stow desconocido: ${stow_mode}"
            return 1
            ;;
    esac

    [ "$VERBOSE" = true ] && stow_flags+=("--verbose")
    [ "$DRY_RUN" = true ]  && stow_flags+=("-n")

    cd "$DOTFILES_DIR" || {
        log_error "No se puede acceder a: ${DOTFILES_DIR}"
        return 1
    }

    log_info "${description}: ${#packages[@]} paquete(s)"

    for package in "${packages[@]}"; do
        # Limpiar comentarios inline (ej: "positron # IDE" → "positron")
        package="$(echo "$package" | awk '{print $1}')"

        if ! validate_stow_package_exists "$package"; then
            log_warn "Saltando paquete inexistente: ${package}"
            continue
        fi

        log_step "→" "Procesando: ${package}"

        if stow "${stow_flags[@]}" --dir="$DOTFILES_DIR" --target="$HOME" "$package" 2>&1; then
            log_success "  ✓ ${package}"
        else
            log_error "  ✗ ${package}"
            if stow -n --dir="$DOTFILES_DIR" --target="$HOME" "$package" 2>&1 \
               | grep -q "conflict\|existing target"; then
                log_warn "  Conflicto: un archivo real bloquea el symlink."
                log_warn "  → Usa 'adoptar -p ${package}' para importar la versión de la laptop."
                log_warn "  → Usa 'instalar -p ${package} --force' para usar la versión del repo."
            fi
            failed=1
        fi
    done

    return $failed
}

# install_configs()
# Crea symlinks: repo → laptop.
# Escenario típico: máquina nueva o primera instalación.
install_configs() {
    log_section "Instalando configuraciones: repo → laptop"
    validate_stow_installed || return 1
    validate_dotfiles_dir   || return 1

    if [ "$NO_BACKUP" = false ] && [ "$DRY_RUN" = false ]; then
        local pkg_names=()
        for p in "${TARGET_PACKAGES[@]}"; do pkg_names+=("$(echo "$p" | awk '{print $1}')"); done
        create_backup "pre-install" "quirurgico" "${pkg_names[@]}"
    fi

    _run_stow "" "${TARGET_PACKAGES[@]}"
    local result=$?
    [ $result -eq 0 ] && log_success "Instalación completada." || \
        log_error "Algunos paquetes no se instalaron. Revisa los mensajes anteriores."
    return $result
}

# adopt_configs()
# Mueve archivos existentes de la laptop al repo y crea symlinks.
#
# Comportamiento de stow --adopt (IMPORTANTE para entender el output):
#   - Si el archivo SOLO existe en la laptop (no en el repo):
#     → Lo MUEVE al repo y crea el symlink. git status mostrará "new file".
#   - Si el archivo existe en AMBOS lugares (laptop y repo):
#     → El repo PREVALECE: stow reemplaza el archivo de la laptop con un
#       symlink al repo. El archivo de la laptop se pierde (por eso hacemos
#       backup antes). git status NO mostrará cambio porque el repo no cambió.
#   - Si el archivo SOLO existe en el repo:
#     → Solo crea el symlink en la laptop.
#
# En resumen: adopt NO actualiza el repo con el contenido de la laptop
# cuando el repo ya tiene ese archivo. Para eso necesitas copiar manualmente.
adopt_configs() {
    log_section "Adoptando configuraciones: laptop → repo"
    validate_stow_installed || return 1
    validate_dotfiles_dir   || return 1

    cat << 'EOF'

  ⚠  ADVERTENCIA — Comportamiento de --adopt:
  ─────────────────────────────────────────────
  • Archivo solo en laptop  → se MUEVE al repo (verás cambio en git diff)
  • Archivo en ambos lados  → el REPO PREVALECE. La versión de la laptop
    se reemplaza por un symlink al repo SIN actualizar el repo.
    Si quieres que el repo tome la versión de la laptop, copia el archivo
    manualmente antes de adoptar:
      cp ~/.config/archivo ~/.dotfiles/paquete/.config/archivo
  • Revisa 'git diff' después para ver qué cambió realmente.

EOF

    confirm_action "¿Confirmas que quieres adoptar las configuraciones de la laptop al repo?" || return 0
    # Backup de lo que hay en el repo ANTES de adoptar
    if [ "$NO_BACKUP" = false ] && [ "$DRY_RUN" = false ]; then
        local pkg_names=()
        for p in "${TARGET_PACKAGES[@]}"; do pkg_names+=("$(echo "$p" | awk '{print $1}')"); done
        # Backup quirúrgico: solo los archivos de los paquetes en trabajo
        create_backup "pre-adopt" "quirurgico" "${pkg_names[@]}"
    fi

    _run_stow "--adopt" "${TARGET_PACKAGES[@]}"
    local result=$?
    if [ $result -eq 0 ]; then
        log_success "Adopción completada."
        log_info "Revisa cambios con: cd ${DOTFILES_DIR} && git diff"
        log_info "Luego sube con:     ./main.sh sync-push"
    else
        log_error "La adopción falló en algunos paquetes."
    fi
    return $result
}

# update_configs()
# Re-aplica symlinks. Útil al agregar nuevos archivos al repo.
update_configs() {
    log_section "Actualizando symlinks"
    validate_stow_installed || return 1
    validate_dotfiles_dir   || return 1
    _run_stow "-R" "${TARGET_PACKAGES[@]}"
    local result=$?
    [ $result -eq 0 ] && log_success "Symlinks actualizados." || \
        log_error "Algunos symlinks no se pudieron actualizar."
    return $result
}

# remove_configs()
# Elimina los symlinks de la laptop SIN borrar los archivos del repositorio.
# Útil para desactivar temporalmente un paquete o antes de desinstalar
# una aplicación.
#
# Flow: stow -D (solo elimina los symlinks)
remove_configs() {
    log_section "Eliminando symlinks"
    validate_stow_installed || return 1
    validate_dotfiles_dir   || return 1
    confirm_action "¿Eliminar symlinks de: ${TARGET_PACKAGES[*]}? (El repo no se toca)" || return 0
    _run_stow "-D" "${TARGET_PACKAGES[@]}"
    local result=$?
    [ $result -eq 0 ] && log_success "Symlinks eliminados. Repo intacto." || \
        log_error "Algunos symlinks no se pudieron eliminar."
    return $result
}

# show_stow_status()
# Vista del estado de todos los paquetes.
# Con --verbose muestra cada archivo individual del paquete.
#
# Leyenda de iconos:
#   ✓ activo    → symlink apuntando correctamente al repo
#   ⚠ conflicto → archivo REAL (no symlink) bloquea la instalación
#   ○ pendiente → paquete en repo pero sin symlink en HOME
#   ∅ vacío     → directorio del paquete existe pero sin archivos
#   — ausente   → directorio del paquete no existe en .dotfiles
show_stow_status() {
    log_section "Estado de symlinks"

    local pkg_ok=0
    local pkg_conflict=0
    local pkg_missing=0
    local pkg_empty=0
    local pkg_absent=0

    printf "  %-16s %-12s %s\n" "PAQUETE" "ESTADO" "DETALLE"
    printf "  %s\n" "────────────────────────────────────────────────────────────────"

    for package in "${STOW_PACKAGES[@]}"; do
        local pkg_name
        pkg_name="$(echo "$package" | awk '{print $1}')"

        # --- Caso 1: directorio del paquete no existe en el repo ---
        if [ ! -d "${DOTFILES_DIR}/${pkg_name}" ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "— ausente" "no existe en .dotfiles/"
            pkg_absent=$((pkg_absent + 1))
            continue
        fi

        # Recolectar todos los archivos del paquete
        local pkg_files=()
        while IFS= read -r f; do
            pkg_files+=("$f")
        done < <(find "${DOTFILES_DIR}/${pkg_name}" -type f \
            ! -name ".gitkeep" ! -name ".directory" 2>/dev/null)

        # --- Caso 2: directorio existe pero está vacío ---
        if [ ${#pkg_files[@]} -eq 0 ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "∅ vacío" "sin archivos en el repo todavía"
            pkg_empty=$((pkg_empty + 1))
            continue
        fi

        # Evaluar el estado de CADA archivo del paquete
        local count_ok=0
        local count_conflict=0
        local count_missing=0
        local file_details=()

        for repo_file in "${pkg_files[@]}"; do
            local rel="${repo_file#${DOTFILES_DIR}/${pkg_name}/}"
            local home_path="${HOME}/${rel}"

            if _is_stow_symlink "$home_path"; then
                count_ok=$((count_ok + 1))
                file_details+=("${COLOR_GREEN}    ✓${COLOR_RESET} ~/${rel}")
            elif [ -f "$home_path" ] || [ -d "$home_path" ]; then
                count_conflict=$((count_conflict + 1))
                file_details+=("${COLOR_RED}    ⚠${COLOR_RESET} ~/${rel}  ← archivo real (adoptar)")
            else
                count_missing=$((count_missing + 1))
                file_details+=("${COLOR_YELLOW}    ○${COLOR_RESET} ~/${rel}  ← no existe (instalar)")
            fi
        done

        # Determinar estado global del paquete
        local total=${#pkg_files[@]}
        if [ "$count_conflict" -gt 0 ] && [ "$count_ok" -eq 0 ]; then
            printf "  ${COLOR_RED}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "⚠ conflicto" "${count_conflict}/${total} archivos bloqueados"
            pkg_conflict=$((pkg_conflict + 1))
        elif [ "$count_ok" -eq "$total" ]; then
            printf "  ${COLOR_GREEN}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "✓ activo" "${count_ok}/${total} symlinks OK"
            pkg_ok=$((pkg_ok + 1))
        elif [ "$count_ok" -gt 0 ] && [ "$count_conflict" -gt 0 ]; then
            # Existe como archivo/directorio REAL → conflicto para stow
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "~ parcial" "${count_ok} OK | ${count_conflict} bloqueados | ${count_missing} pendientes"
            pkg_conflict=$((pkg_conflict + 1))
        elif [ "$count_ok" -gt 0 ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "~ parcial" "${count_ok}/${total} symlinks, ${count_missing} pendientes"
            pkg_missing=$((pkg_missing + 1))
        else
            # No existe nada en esa ruta → listo para instalar
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "○ pendiente" "${total} archivos listos para instalar"
            pkg_missing=$((pkg_missing + 1))
        fi

        # Modo detallado: mostrar cada archivo
        if [ "$VERBOSE" = true ]; then
            for detail in "${file_details[@]}"; do
                printf "${detail}\n"
            done
        fi
    done

    # Resumen
    echo ""
    printf "  Resumen: ${COLOR_GREEN}%d activos${COLOR_RESET} | ${COLOR_RED}%d conflictos${COLOR_RESET} | ${COLOR_YELLOW}%d pendientes${COLOR_RESET} | %d vacíos | %d ausentes\n" \
        "$pkg_ok" "$pkg_conflict" "$pkg_missing" "$pkg_empty" "$pkg_absent"
    echo ""

    if [ "$pkg_conflict" -gt 0 ]; then
        printf "  ${COLOR_BOLD}Para resolver conflictos:${COLOR_RESET}\n"
        printf "  Laptop → repo:  ./main.sh adoptar  -p <paquete>\n"
        printf "  Repo   → laptop:./main.sh instalar -p <paquete> --force\n"
        echo ""
    fi
    if [ "$VERBOSE" = false ] && [ $((pkg_conflict + pkg_missing)) -gt 0 ]; then
        printf "  ${COLOR_CYAN}Tip: usa ./main.sh estado --verbose (-v) para ver cada archivo individual${COLOR_RESET}\n\n"
    fi
}