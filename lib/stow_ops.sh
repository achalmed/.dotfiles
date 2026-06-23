#!/usr/bin/env bash
# =============================================================================
# lib/stow_ops.sh — Operaciones de GNU Stow para gestión de symlinks
# =============================================================================
# Este módulo encapsula toda la interacción con stow. Separar la lógica de
# stow del resto permite cambiar la implementación (ej: pasar a otro gestor
# de symlinks) sin afectar los demás módulos.
#
# Flujos principales:
#   install_configs  → repo    a laptop (stow)
#   adopt_configs    → laptop  a repo   (stow --adopt)
#   update_configs   → actualizar symlinks existentes (stow -R)
#   remove_configs   → eliminar symlinks              (stow -D)
# =============================================================================

# _run_stow()
# Función base que ejecuta stow con el modo y paquetes indicados.
# Maneja dry-run, verbose y errores de conflictos de forma uniforme.
#
# Arguments:
#   $1 - Modo stow: "" (instalar), "--adopt", "-R" (restow), "-D" (delete)
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
    [ "$DRY_RUN" = true ] && stow_flags+=("-n")

    cd "$DOTFILES_DIR" || {
        log_error "No se puede acceder a: ${DOTFILES_DIR}"
        return 1
    }

    log_info "${description}: ${#packages[@]} paquete(s)"

    for package in "${packages[@]}"; do
        # Limpiar comentarios inline del nombre (ej: "positron # IDE" → "positron")
        package="$(echo "$package" | awk '{print $1}')"

        if ! validate_stow_package_exists "$package"; then
            log_warn "Saltando paquete inexistente: ${package}"
            continue
        fi

        log_step "→" "Procesando: ${package}"

        if stow "${stow_flags[@]}" --dir="$DOTFILES_DIR" --target="$HOME" "$package" 2>&1; then
            log_success "  ✓ ${package}"
        else
            local exit_code=$?
            log_error "  ✗ ${package} (código: ${exit_code})"

            # Diagnóstico específico para errores comunes de stow
            if stow -n --dir="$DOTFILES_DIR" --target="$HOME" "$package" 2>&1 | grep -q "conflict\|existing target"; then
                log_warn "  Hay conflictos en '${package}'. Archivos del sistema colisionan con el repo."
                log_warn "  Usa 'adoptar' si quieres importar esos archivos al repo."
                log_warn "  O usa --force (-f) para sobrescribir (crea backup automáticamente)."
            fi
            failed=1
        fi
    done

    return $failed
}

# install_configs()
# Crea symlinks desde el repositorio hacia la laptop.
# Escenario: llegaste a una máquina nueva o limpiaste tu home.
#
# Flow: repo → laptop (stow sin flags extra)
install_configs() {
    log_section "Instalando configuraciones: repo → laptop"

    validate_stow_installed || return 1
    validate_dotfiles_dir   || return 1

    # Backup automático si NO se pidió omitirlo
    if [ "$NO_BACKUP" = false ] && [ "$DRY_RUN" = false ]; then
        log_info "Creando backup preventivo antes de instalar..."
        create_backup "pre-install" || log_warn "Backup falló; continuando de todos modos."
    fi

    _run_stow "" "${TARGET_PACKAGES[@]}"
    local result=$?

    if [ $result -eq 0 ]; then
        log_success "Instalación completada. Los symlinks apuntan al repo."
    else
        log_error "Algunos paquetes no se instalaron correctamente. Revisa los mensajes anteriores."
    fi
    return $result
}

# adopt_configs()
# Mueve los archivos de configuración existentes en la laptop al repositorio
# y crea symlinks en su lugar.
#
# IMPORTANTE: stow --adopt mueve el archivo real al repo y deja un symlink.
# Es la operación correcta cuando ya tienes configs en la laptop y quieres
# comenzar a versionarlas. NO sobrescribe con lo que ya hay en el repo.
#
# Flow: laptop → repo (stow --adopt)
adopt_configs() {
    log_section "Adoptando configuraciones: laptop → repo"

    validate_stow_installed || return 1
    validate_dotfiles_dir   || return 1

    cat << 'EOF'

  ⚠  ADVERTENCIA IMPORTANTE sobre --adopt:
  ─────────────────────────────────────────
  Esta operación MUEVE los archivos de tu laptop al repositorio.
  Si el repo ya tiene una versión diferente del mismo archivo,
  la versión del repo PREVALECE (stow actualiza el symlink pero
  no sobreescribe lo que ya está en el repo).

  Recomendación: revisa 'git diff' después de adoptar para ver
  qué cambió antes de hacer commit.

EOF

    confirm_action "¿Confirmas que quieres adoptar las configuraciones de la laptop al repo?" || return 0

    # Backup de lo que hay en el repo ANTES de adoptar
    if [ "$NO_BACKUP" = false ] && [ "$DRY_RUN" = false ]; then
        log_info "Creando backup del repo antes de adoptar..."
        create_backup "pre-adopt" || log_warn "Backup falló; continuando."
    fi

    _run_stow "--adopt" "${TARGET_PACKAGES[@]}"
    local result=$?

    if [ $result -eq 0 ]; then
        log_success "Adopción completada."
        log_info "Ejecuta 'git diff' en ${DOTFILES_DIR} para revisar qué cambió."
        log_info "Luego usa 'sync-push' para subir los cambios a GitHub."
    else
        log_error "La adopción falló en algunos paquetes."
    fi
    return $result
}

# update_configs()
# Re-aplica los symlinks. Útil cuando:
#   - Agregaste nuevos archivos al repositorio
#   - Cambiaste la estructura de directorios
#   - Los symlinks quedaron rotos por alguna razón
#
# Flow: re-stow (stow -R)
update_configs() {
    log_section "Actualizando symlinks"

    validate_stow_installed || return 1
    validate_dotfiles_dir   || return 1

    _run_stow "-R" "${TARGET_PACKAGES[@]}"
    local result=$?

    if [ $result -eq 0 ]; then
        log_success "Symlinks actualizados correctamente."
    else
        log_error "Algunos symlinks no se pudieron actualizar."
    fi
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

    confirm_action "¿Eliminar los symlinks de: ${TARGET_PACKAGES[*]}? (Los archivos del repo NO se borran)" || return 0

    _run_stow "-D" "${TARGET_PACKAGES[@]}"
    local result=$?

    if [ $result -eq 0 ]; then
        log_success "Symlinks eliminados. Los archivos del repo están intactos."
    else
        log_error "Algunos symlinks no se pudieron eliminar."
    fi
    return $result
}

# show_stow_status()
# Muestra el estado de cada paquete stow con diagnóstico claro:
#   ✓ symlink activo   → el symlink existe y apunta al repo
#   ⚠ conflicto        → existe un archivo REAL (no symlink) en ~/.config/
#                        Solución: ./main.sh adoptar -p <paquete>
#   ○ no instalado     → el directorio existe en el repo pero sin symlink
#                        Solución: ./main.sh instalar -p <paquete>
#   ∅ vacío            → el directorio del paquete no tiene archivos aún
#   — no en repo       → el directorio del paquete no existe en .dotfiles
#
# NOTA sobre contadores con set -e:
# En Bash, ((var++)) retorna código 1 cuando el resultado es 0 (cero),
# lo que con set -e termina el script silenciosamente. Por eso usamos
# la forma "var=$((var + 1))" que siempre retorna código 0.
show_stow_status() {
    log_section "Estado de symlinks por paquete"

    local pkg_ok=0
    local pkg_missing=0
    local pkg_conflict=0
    local pkg_empty=0
    local pkg_absent=0

    printf "  %-16s %-10s %s\n" "PAQUETE" "ESTADO" "DETALLE"
    printf "  %s\n" "──────────────────────────────────────────────────────────"

    for package in "${STOW_PACKAGES[@]}"; do
        # Limpiar el nombre del paquete de comentarios inline (ej: "positron # IDE")
        local pkg_name
        pkg_name="$(echo "$package" | awk '{print $1}')"

        if [ ! -d "${DOTFILES_DIR}/${pkg_name}" ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-10s %s\n"                 "$pkg_name" "— ausente" "directorio no existe en repo"
            pkg_absent=$((pkg_absent + 1))
            continue
        fi

        # Buscar archivos reales (no directorios, no .gitkeep) en el paquete
        local sample_file
        sample_file="$(find "${DOTFILES_DIR}/${pkg_name}" -type f             ! -name ".gitkeep" ! -name ".directory" 2>/dev/null | head -1)"

        if [ -z "$sample_file" ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-10s %s\n"                 "$pkg_name" "∅ vacío" "sin archivos en el repo todavía"
            pkg_empty=$((pkg_empty + 1))
            continue
        fi

        # Calcular la ruta del symlink equivalente en HOME
        local relative_path="${sample_file#${DOTFILES_DIR}/${pkg_name}/}"
        local symlink_path="${HOME}/${relative_path}"

        if [ -L "$symlink_path" ]; then
            # Es un symlink — verificar que apunta al repo (no a otro lado)
            local link_target
            link_target="$(readlink "$symlink_path")"
            if echo "$link_target" | grep -q "$DOTFILES_DIR"; then
                printf "  ${COLOR_GREEN}%-16s${COLOR_RESET} %-10s %s\n"                     "$pkg_name" "✓ activo" "→ ${relative_path}"
            else
                printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-10s %s\n"                     "$pkg_name" "~ externo" "symlink existe pero apunta a otro lugar"
            fi
            pkg_ok=$((pkg_ok + 1))
        elif [ -f "$symlink_path" ] || [ -d "$symlink_path" ]; then
            # Existe como archivo/directorio REAL → conflicto para stow
            printf "  ${COLOR_RED}%-16s${COLOR_RESET} %-10s %s\n"                 "$pkg_name" "⚠ conflicto" "archivo real en ~/${relative_path}"
            pkg_conflict=$((pkg_conflict + 1))
        else
            # No existe nada en esa ruta → listo para instalar
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-10s %s\n"                 "$pkg_name" "○ pendiente" "ejecuta: instalar -p ${pkg_name}"
            pkg_missing=$((pkg_missing + 1))
        fi
    done

    echo ""
    printf "  Resumen: ${COLOR_GREEN}%d OK${COLOR_RESET} | ${COLOR_YELLOW}%d pendiente${COLOR_RESET} | ${COLOR_RED}%d conflictos${COLOR_RESET} | %d vacíos | %d ausentes\n"         "$pkg_ok" "$pkg_missing" "$pkg_conflict" "$pkg_empty" "$pkg_absent"
    echo ""
    printf "  ${COLOR_BOLD}Qué hacer con los conflictos:${COLOR_RESET}\n"
    printf "  Si quieres conservar la versión de la laptop → ./main.sh adoptar\n"
    printf "  Si quieres usar la versión del repo          → ./main.sh instalar --force\n"
}