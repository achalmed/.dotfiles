#!/usr/bin/env bash
# =============================================================================
# lib/stow_ops.sh — Gestión de dotfiles con archivos explícitos
# =============================================================================
# Este módulo usa el mapa PACKAGE_FILES de config.sh para saber exactamente
# qué archivos sincronizar, dando control total sobre qué se versiona.
#
# Los symlinks se crean directamente (ln -sfn), archivo por archivo, según
# la lista explícita. El binario de GNU Stow NO es necesario: el layout de
# los paquetes es 100% compatible con stow (rutas relativas a $HOME dentro
# de cada paquete), así que 'stow <paquete>' también funcionaría, pero
# enlazaría TODO el paquete sin el control archivo-por-archivo de este módulo.
#
# FLUJOS:
#   adoptar   → laptop → repo (con resolución interactiva de conflictos)
#   instalar  → repo   → laptop (symlinks explícitos)
#   actualizar → re-sincronizar symlinks
#   eliminar  → quitar symlinks sin tocar el repo
# =============================================================================

# _read_choice()
# Lee una opción del usuario desde la terminal. Si no hay TTY disponible
# (ejecución no interactiva, CI, pipes), devuelve el valor por defecto
# para no colgar ni abortar el script.
#
# Arguments:
#   $1 - Valor por defecto si no hay TTY
#
# Output (stdout): la opción elegida (o el default)
_read_choice() {
    local default="$1"
    local choice
    if [ -r /dev/tty ] && [ -w /dev/tty ]; then
        read -r choice </dev/tty || choice="$default"
        echo "${choice:-$default}"
    else
        echo "$default"
    fi
}

# _get_package_files()
# Devuelve la lista de archivos de un paquete desde PACKAGE_FILES.
# Cada elemento es una ruta relativa al HOME del usuario.
#
# Arguments:
#   $1 - Nombre del paquete
#
# Output (stdout):
#   Una ruta por línea (relativa a HOME)
_get_package_files() {
    local pkg="$1"
    local file_list="${PACKAGE_FILES[$pkg]:-}"

    if [ -z "$file_list" ]; then
        return 0
    fi

    # El separador es '|'; IFS se restaura al salir de la función
    local IFS='|'
    for f in $file_list; do
        # Trim de espacios y tabs
        f="$(echo "$f" | tr -d ' \t')"
        [ -n "$f" ] && echo "$f"
    done
}

# _ensure_repo_dir()
# Crea el directorio en el repo con la estructura correcta para stow.
# Si el archivo vive en .config/app/file, la estructura es:
#   DOTFILES_DIR/paquete/.config/app/file
#
# Arguments:
#   $1 - Paquete
#   $2 - Ruta relativa del archivo (ej: .config/katerc)
_ensure_repo_dir() {
    local pkg="$1"
    local rel_path="$2"
    local repo_file_dir="${DOTFILES_DIR}/${pkg}/$(dirname "$rel_path")"
    mkdir -p "$repo_file_dir"
}

# _repo_path()
# Devuelve la ruta absoluta de un archivo dentro del repo.
#
# Arguments:
#   $1 - Paquete
#   $2 - Ruta relativa del archivo
_repo_path() {
    echo "${DOTFILES_DIR}/${1}/${2}"
}

# _home_path()
# Devuelve la ruta absoluta de un archivo en HOME.
#
# Arguments:
#   $1 - Ruta relativa del archivo
_home_path() {
    echo "${HOME}/${1}"
}

# _is_our_symlink()
# Verifica que una ruta en HOME es un symlink que apunta a nuestro repo.
# Usa readlink -f para resolver rutas relativas correctamente.
#
# Returns: 0 si es nuestro symlink, 1 si no
_is_our_symlink() {
    local path="$1"
    [ -L "$path" ] || return 1
    local real_target
    real_target="$(readlink -f "$path" 2>/dev/null)" || return 1
    [[ "$real_target" == "${DOTFILES_DIR}"/* ]]
}

# _create_symlink()
# Crea un symlink desde HOME apuntando al archivo en el repo.
# Crea los directorios padre si no existen.
#
# Arguments:
#   $1 - Ruta en el repo (absoluta)
#   $2 - Ruta en HOME (absoluta)
_create_symlink() {
    local repo_file="$1"
    local home_file="$2"

    # Crear directorio padre en HOME si no existe
    local parent_dir
    parent_dir="$(dirname "$home_file")"
    mkdir -p "$parent_dir"

    [ "$DRY_RUN" = true ] && {
        log_info "  [dry-run] ln -sfn ${repo_file} → ${home_file}"
        return 0
    }

    # Crear symlink. -n evita que, si el destino es un symlink a directorio,
    # el enlace se cree DENTRO del directorio en lugar de reemplazarlo.
    ln -sfn "$repo_file" "$home_file"
}

# =============================================================================
# ADOPTAR: laptop → repo
# =============================================================================
# Lógica para cada archivo del paquete:
#   1. Si existe en HOME pero NO en repo → mover al repo + crear symlink
#   2. Si existe en AMBOS → preguntar al usuario qué versión usar:
#        a) Laptop: copiar laptop→repo, actualizar symlink
#        b) Repo:   eliminar versión de laptop, crear symlink al repo
#   3. Si SOLO está en repo → solo crear symlink (no hay nada que mover)
#   4. Si no existe en ninguno → avisar y saltar

# adopt_configs()
# Punto de entrada para adoptar un conjunto de paquetes.
adopt_configs() {
    log_section "Adoptando configuraciones: laptop → repo"
    validate_dotfiles_dir   || return 1

    local total_adopted=0
    local total_skipped=0

    for package in "${TARGET_PACKAGES[@]}"; do
        local pkg_name
        pkg_name="$(echo "$package" | awk '{print $1}')"

        if [ -z "${PACKAGE_FILES[$pkg_name]:-}" ]; then
            log_warn "Paquete '${pkg_name}' no tiene archivos definidos en config.sh."
            log_warn "Agrega los archivos a PACKAGE_FILES[\"${pkg_name}\"] en config.sh."
            total_skipped=$((total_skipped + 1))
            continue
        fi

        log_section "Adoptando paquete: ${pkg_name}"
        _adopt_package "$pkg_name"
        local result=$?
        [ $result -eq 0 ] && total_adopted=$((total_adopted + 1)) || \
            total_skipped=$((total_skipped + 1))
    done

    echo ""
    log_success "Adopción completada: ${total_adopted} paquetes procesados, ${total_skipped} saltados."
    log_info "Revisa cambios: cd ${DOTFILES_DIR} && git diff"
    log_info "Sube a GitHub:  ./main.sh sync-push"
}

# _adopt_package()
# Adopta todos los archivos de un paquete con resolución interactiva.
#
# Arguments:
#   $1 - Nombre del paquete
_adopt_package() {
    local pkg="$1"
    local files_adopted=0
    local files_skipped=0

    # Crear el directorio base del paquete en el repo si no existe
    mkdir -p "${DOTFILES_DIR}/${pkg}"

    while IFS= read -r rel_path; do
        local home_file repo_file
        home_file="$(_home_path "$rel_path")"
        repo_file="$(_repo_path "$pkg" "$rel_path")"

        local home_exists=false repo_exists=false
        if [ -e "$home_file" ] || [ -L "$home_file" ]; then
            home_exists=true
        fi
        if [ -e "$repo_file" ]; then
            repo_exists=true
        fi

        _is_our_symlink "$home_file" && {
            # Ya es nuestro symlink → todo OK
            [ "$VERBOSE" = true ] && \
                log_success "  ✓ ya conectado: ${rel_path}"
            files_adopted=$((files_adopted + 1))
            continue
        }

        if $home_exists && ! $repo_exists; then
            # CASO 1: Solo en laptop → mover al repo
            _adopt_laptop_only "$pkg" "$rel_path" "$home_file" "$repo_file"
            files_adopted=$((files_adopted + 1))

        elif $home_exists && $repo_exists; then
            # CASO 2: En ambos → resolver conflicto interactivamente
            if _resolve_conflict "$pkg" "$rel_path" "$home_file" "$repo_file"; then
                files_adopted=$((files_adopted + 1))
            else
                files_skipped=$((files_skipped + 1))
            fi

        elif ! $home_exists && $repo_exists; then
            # CASO 3: Solo en repo → crear symlink en HOME
            _adopt_repo_only "$rel_path" "$home_file" "$repo_file"
            files_adopted=$((files_adopted + 1))

        else
            # CASO 4: No existe en ninguno
            log_warn "  ○ no encontrado en laptop ni en repo: ${rel_path}"
            log_warn "    (¿la app está instalada? ¿el archivo existe?)"
            files_skipped=$((files_skipped + 1))
        fi

    done < <(_get_package_files "$pkg")

    printf "  ${COLOR_CYAN}%s:${COLOR_RESET} %d adoptados, %d saltados\n" \
        "$pkg" "$files_adopted" "$files_skipped"

    # Limpiar archivos del repo que ya no están en la lista de gestionados
    _clean_repo_orphans "$pkg"
}

# _adopt_laptop_only()
# Caso 1: El archivo existe solo en la laptop. Moverlo al repo y crear symlink.
_adopt_laptop_only() {
    local pkg="$1" rel_path="$2" home_file="$3" repo_file="$4"

    _ensure_repo_dir "$pkg" "$rel_path"

    if [ "$DRY_RUN" = true ]; then
        log_info "  [dry-run] mover: ${rel_path} → repo"
        return 0
    fi

    # mv preserva atributos y es atómico en el mismo filesystem.
    # Fallback a cp -a + rm para casos cross-filesystem.
    if ! mv "$home_file" "$repo_file" 2>/dev/null; then
        cp -a "$home_file" "$repo_file"
        rm -rf "$home_file"
    fi

    _create_symlink "$repo_file" "$home_file"
    log_success "  ✓ movido al repo: ${rel_path}"
}

# _adopt_repo_only()
# Caso 3: El archivo existe solo en el repo. Crear symlink en HOME.
_adopt_repo_only() {
    local rel_path="$1" home_file="$2" repo_file="$3"

    _create_symlink "$repo_file" "$home_file"
    [ "$DRY_RUN" = false ] && log_success "  ✓ symlink creado: ${rel_path}"
}

# _resolve_conflict()
# Caso 2: El archivo existe en ambos lados. Preguntar al usuario.
# Muestra un diff visual para que el usuario pueda decidir con información.
#
# Returns: 0 si se resolvió, 1 si el usuario saltó
_resolve_conflict() {
    local pkg="$1" rel_path="$2" home_file="$3" repo_file="$4"

    echo ""
    printf "  ${COLOR_YELLOW}⚠  CONFLICTO:${COLOR_RESET} %s\n" "$rel_path"
    printf "  ├─ Laptop: %s\n" "$home_file"
    printf "  └─ Repo:   %s\n" "$repo_file"

    # Mostrar diff si los archivos son texto y diff está disponible
    if command -v diff &>/dev/null && \
       [ -f "$home_file" ] && [ -f "$repo_file" ] && \
       file "$home_file" 2>/dev/null | grep -q "text"; then
        local diff_output
        diff_output="$(diff --unified=2 "$repo_file" "$home_file" 2>/dev/null | head -40)"
        if [ -n "$diff_output" ]; then
            printf "\n  ${COLOR_CYAN}Diferencias (repo vs laptop):${COLOR_RESET}\n"
            echo "$diff_output" | while IFS= read -r line; do
                printf "  %s\n" "$line"
            done
            echo ""
        else
            printf "  ${COLOR_GREEN}→ Los archivos son idénticos.${COLOR_RESET}\n"
        fi
    fi

    if [ "$DRY_RUN" = true ]; then
        log_info "  [dry-run] se preguntaría al usuario qué versión usar"
        return 0
    fi

    # Menú de resolución
    printf "  ¿Qué versión usar?\n"
    printf "  ${COLOR_GREEN}[l]${COLOR_RESET} Laptop → repo (actualiza el repo con la versión de la laptop)\n"
    printf "  ${COLOR_CYAN}[r]${COLOR_RESET} Repo   → laptop (mantiene el repo, crea symlink)\n"
    printf "  ${COLOR_YELLOW}[s]${COLOR_RESET} Saltar este archivo\n"
    printf "  Opción [l/r/s]: "
    choice="$(_read_choice "s")"

    case "$choice" in
        [lL])
            # Laptop → repo: copiar laptop al repo, luego symlink
            _ensure_repo_dir "$pkg" "$rel_path"
            create_backup "conflicto-${pkg}" "quirurgico" "$pkg"
            if [ -d "$home_file" ]; then
                rm -rf "$repo_file"
                cp -r "$home_file" "$repo_file"
                rm -rf "$home_file"
            else
                cp "$home_file" "$repo_file"
                rm "$home_file"
            fi
            _create_symlink "$repo_file" "$home_file"
            log_success "  ✓ actualizado desde laptop: ${rel_path}"
            return 0
            ;;
        [rR])
            # Repo → laptop: backup del archivo de laptop, luego symlink al repo
            create_backup "conflicto-${pkg}" "quirurgico" "$pkg"
            if [ -d "$home_file" ] && ! [ -L "$home_file" ]; then
                rm -rf "$home_file"
            elif [ -f "$home_file" ]; then
                rm "$home_file"
            fi
            _create_symlink "$repo_file" "$home_file"
            log_success "  ✓ conectado al repo (versión del repo prevalece): ${rel_path}"
            return 0
            ;;
        *)
            log_warn "  → Saltado: ${rel_path}"
            return 1
            ;;
    esac
}

# _clean_repo_orphans()
# Elimina del repo archivos que ya no están en la lista PACKAGE_FILES.
# Esto resuelve el caso donde el repo tenía más archivos que la laptop.
#
# Arguments:
#   $1 - Nombre del paquete
_clean_repo_orphans() {
    local pkg="$1"
    local pkg_dir="${DOTFILES_DIR}/${pkg}"

    [ -d "$pkg_dir" ] || return 0

    # Construir set de archivos válidos para este paquete
    local -A valid_files=()
    while IFS= read -r rel; do
        valid_files["${pkg_dir}/${rel}"]=1
    done < <(_get_package_files "$pkg")

    # Recorrer archivos actuales del repo
    local orphans=()
    while IFS= read -r repo_file; do
        # Ignorar directorios y archivos del sistema git
        [ -f "$repo_file" ] || continue
        [[ "$repo_file" == *"/.git/"* ]] && continue

        # Verificar si está en la lista de válidos (o dentro de un directorio válido)
        local is_valid=false
        for valid in "${!valid_files[@]}"; do
            if [[ "$repo_file" == "$valid" ]] || [[ "$repo_file" == "${valid}/"* ]]; then
                is_valid=true
                break
            fi
        done

        $is_valid || orphans+=("$repo_file")
    done < <(find "$pkg_dir" -type f ! -path "*/.git/*" 2>/dev/null)

    if [ ${#orphans[@]} -gt 0 ]; then
        echo ""
        printf "  ${COLOR_YELLOW}Archivos huérfanos en el repo (ya no en la lista de gestión):${COLOR_RESET}\n"
        for orphan in "${orphans[@]}"; do
            local display="${orphan#${DOTFILES_DIR}/${pkg}/}"
            printf "  ${COLOR_RED}  ✗${COLOR_RESET} %s\n" "$display"
        done
        printf "  ¿Eliminar estos archivos del repo? [s/N]: "
        choice="$(_read_choice "n")"
        if [[ "$choice" =~ ^[sS] ]]; then
            for orphan in "${orphans[@]}"; do
                [ "$DRY_RUN" = false ] && rm -f "$orphan" && \
                    log_success "  Eliminado del repo: ${orphan#${DOTFILES_DIR}/}"
            done
            # Limpiar directorios vacíos
            find "$pkg_dir" -type d -empty -not -path "*/.git/*" \
                -delete 2>/dev/null || true
        else
            log_info "  Huérfanos conservados. Puedes eliminarlos manualmente después."
        fi
    fi
}

# =============================================================================
# INSTALAR: repo → laptop
# =============================================================================

# install_configs()
# Crea symlinks desde el repo hacia la laptop para todos los paquetes.
install_configs() {
    log_section "Instalando configuraciones: repo → laptop"
    validate_dotfiles_dir || return 1

    local total_ok=0
    local total_skip=0

    for package in "${TARGET_PACKAGES[@]}"; do
        local pkg_name
        pkg_name="$(echo "$package" | awk '{print $1}')"

        if [ -z "${PACKAGE_FILES[$pkg_name]:-}" ]; then
            log_warn "Paquete '${pkg_name}' sin archivos definidos en config.sh — saltando."
            total_skip=$((total_skip + 1))
            continue
        fi

        if [ ! -d "${DOTFILES_DIR}/${pkg_name}" ]; then
            log_warn "Paquete '${pkg_name}' no existe en el repo — saltando."
            log_warn "Usa 'adoptar -p ${pkg_name}' primero para agregarlo."
            total_skip=$((total_skip + 1))
            continue
        fi

        _install_package "$pkg_name"
        total_ok=$((total_ok + 1))
    done

    echo ""
    log_success "Instalación: ${total_ok} paquetes procesados, ${total_skip} saltados."
}

# _install_package()
# Crea symlinks para todos los archivos de un paquete.
# Si ya existe un archivo real en HOME, pregunta qué hacer (igual que adoptar).
_install_package() {
    local pkg="$1"
    log_info "Instalando: ${pkg}"

    # Backup quirúrgico antes de instalar
    if [ "$NO_BACKUP" = false ] && [ "$DRY_RUN" = false ]; then
        create_backup "pre-install-${pkg}" "quirurgico" "$pkg"
    fi

    while IFS= read -r rel_path; do
        local home_file repo_file
        home_file="$(_home_path "$rel_path")"
        repo_file="$(_repo_path "$pkg" "$rel_path")"

        # Si no existe en el repo, no hay nada que instalar
        if [ ! -e "$repo_file" ]; then
            log_warn "  ○ no en repo: ${rel_path}"
            continue
        fi

        # Si ya es nuestro symlink, actualizar
        if _is_our_symlink "$home_file"; then
            _create_symlink "$repo_file" "$home_file"
            [ "$VERBOSE" = true ] && log_success "  ✓ actualizado: ${rel_path}"
            continue
        fi

        # Si existe archivo real en HOME → conflicto
        if [ -e "$home_file" ]; then
            if [ "$FORCE" = true ]; then
                # --force: reemplazar sin preguntar (ya se hizo backup)
                choice="r"
            else
                printf "\n  ${COLOR_YELLOW}⚠  Archivo real existe:${COLOR_RESET} ~/%s\n" "$rel_path"
                printf "  ¿Qué hacer?\n"
                printf "  ${COLOR_GREEN}[r]${COLOR_RESET} Reemplazar con versión del repo (backup automático)\n"
                printf "  ${COLOR_YELLOW}[s]${COLOR_RESET} Saltar\n"
                printf "  Opción [r/s]: "
                choice="$(_read_choice "s")"
            fi
            case "$choice" in
                [rR])
                    [ "$DRY_RUN" = false ] && {
                        [ -d "$home_file" ] && rm -rf "$home_file" || rm -f "$home_file"
                    }
                    _create_symlink "$repo_file" "$home_file"
                    log_success "  ✓ instalado (repo): ${rel_path}"
                    ;;
                *)
                    log_warn "  → Saltado: ${rel_path}"
                    ;;
            esac
        else
            # No existe en HOME → crear symlink directamente
            _create_symlink "$repo_file" "$home_file"
            [ "$DRY_RUN" = false ] && log_success "  ✓ instalado: ${rel_path}"
        fi

    done < <(_get_package_files "$pkg")
}

# =============================================================================
# ACTUALIZAR, ELIMINAR, ESTADO
# =============================================================================

# update_configs()
# Re-crea todos los symlinks (útil si se agregaron archivos al repo).
update_configs() {
    log_section "Actualizando symlinks"
    validate_dotfiles_dir || return 1

    for package in "${TARGET_PACKAGES[@]}"; do
        local pkg_name
        pkg_name="$(echo "$package" | awk '{print $1}')"
        [ -z "${PACKAGE_FILES[$pkg_name]:-}" ] && continue

        log_info "Actualizando: ${pkg_name}"
        while IFS= read -r rel_path; do
            local home_file repo_file
            home_file="$(_home_path "$rel_path")"
            repo_file="$(_repo_path "$pkg_name" "$rel_path")"

            [ -e "$repo_file" ] || continue
            _create_symlink "$repo_file" "$home_file"
            [ "$VERBOSE" = true ] && log_success "  ✓ ${rel_path}"
        done < <(_get_package_files "$pkg_name")
    done
    log_success "Symlinks actualizados."
}

# remove_configs()
# Elimina los symlinks de la laptop SIN borrar los archivos del repositorio.
# Útil para desactivar temporalmente un paquete o antes de desinstalar
# una aplicación.
#
# Flow: stow -D (solo elimina los symlinks)
remove_configs() {
    log_section "Eliminando symlinks"
    validate_dotfiles_dir || return 1
    confirm_action "¿Eliminar symlinks de: ${TARGET_PACKAGES[*]}? (El repo no se modifica)" || return 0

    for package in "${TARGET_PACKAGES[@]}"; do
        local pkg_name
        pkg_name="$(echo "$package" | awk '{print $1}')"
        [ -z "${PACKAGE_FILES[$pkg_name]:-}" ] && continue

        log_info "Eliminando symlinks de: ${pkg_name}"
        while IFS= read -r rel_path; do
            local home_file
            home_file="$(_home_path "$rel_path")"
            if _is_our_symlink "$home_file"; then
                [ "$DRY_RUN" = false ] && rm "$home_file"
                [ "$VERBOSE" = true ] && log_success "  ✓ eliminado: ${rel_path}"
            fi
        done < <(_get_package_files "$pkg_name")
    done
    log_success "Symlinks eliminados. Repo intacto."
}

# =============================================================================
# ESTADO
# =============================================================================

# show_stow_status()
# Muestra el estado de todos los paquetes con sus archivos.
# Leyenda:
#   ✓ activo    → symlink apuntando al repo
#   ⚠ conflicto → archivo real en HOME (adoptar o instalar --force)
#   ○ pendiente → en repo pero sin symlink en HOME
#   ✗ ausente   → en la lista pero sin archivo en repo ni en HOME
#   — no config → paquete sin archivos en PACKAGE_FILES
#   ∅ sin repo  → paquete en PACKAGE_FILES pero sin directorio en .dotfiles
show_stow_status() {
    log_section "Estado de dotfiles"

    local count_ok=0 count_conflict=0 count_pending=0
    local count_absent=0 count_noconfig=0

    printf "  %-16s %-12s %s\n" "PAQUETE" "ESTADO" "DETALLE"
    printf "  %s\n" "──────────────────────────────────────────────────────────────────"

    for package in "${STOW_PACKAGES[@]}"; do
        local pkg_name
        pkg_name="$(echo "$package" | awk '{print $1}')"

        # Sin definición de archivos
        if [ -z "${PACKAGE_FILES[$pkg_name]:-}" ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "— sin config" "agrega a PACKAGE_FILES en config.sh"
            count_noconfig=$((count_noconfig + 1))
            continue
        fi

        # Contar estado de archivos
        local ok=0 conflict=0 pending=0 absent=0 total=0
        local details_ok=() details_conflict=() details_pending=() details_absent=()

        while IFS= read -r rel_path; do
            total=$((total + 1))
            local home_file repo_file
            home_file="$(_home_path "$rel_path")"
            repo_file="$(_repo_path "$pkg_name" "$rel_path")"

            if _is_our_symlink "$home_file"; then
                ok=$((ok + 1))
                details_ok+=("${rel_path}")
            elif [ -e "$home_file" ] && [ -e "$repo_file" ]; then
                conflict=$((conflict + 1))
                details_conflict+=("${rel_path}")
            elif [ -e "$repo_file" ] && ! [ -e "$home_file" ]; then
                pending=$((pending + 1))
                details_pending+=("${rel_path}")
            else
                absent=$((absent + 1))
                details_absent+=("${rel_path}")
            fi
        done < <(_get_package_files "$pkg_name")

        # Estado global del paquete
        if [ "$ok" -eq "$total" ] && [ "$total" -gt 0 ]; then
            printf "  ${COLOR_GREEN}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "✓ activo" "${ok}/${total} archivos conectados"
            count_ok=$((count_ok + 1))
        elif [ "$conflict" -gt 0 ] && [ "$ok" -eq 0 ]; then
            printf "  ${COLOR_RED}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "⚠ conflicto" "${conflict} archivos reales en HOME (adoptar)"
            count_conflict=$((count_conflict + 1))
        elif [ "$conflict" -gt 0 ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "~ parcial" "${ok} OK | ${conflict} conflicto | ${pending} pendiente"
            count_conflict=$((count_conflict + 1))
        elif [ "$pending" -gt 0 ] || [ "$absent" -gt 0 ]; then
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "○ pendiente" "${pending} para instalar | ${absent} sin archivo"
            count_pending=$((count_pending + 1))
        else
            printf "  ${COLOR_YELLOW}%-16s${COLOR_RESET} %-12s %s\n" \
                "$pkg_name" "∅ sin repo" "ningún archivo en .dotfiles aún (adoptar primero)"
            count_absent=$((count_absent + 1))
        fi

        # Modo verbose: detalle por archivo
        if [ "$VERBOSE" = true ]; then
            for f in "${details_ok[@]}"; do
                printf "  ${COLOR_GREEN}    ✓${COLOR_RESET} %s\n" "$f"
            done
            for f in "${details_conflict[@]}"; do
                printf "  ${COLOR_RED}    ⚠${COLOR_RESET} %s  ${COLOR_RED}← archivo real (adoptar)${COLOR_RESET}\n" "$f"
            done
            for f in "${details_pending[@]}"; do
                printf "  ${COLOR_YELLOW}    ○${COLOR_RESET} %s  ← en repo, falta symlink (instalar)\n" "$f"
            done
            for f in "${details_absent[@]}"; do
                printf "  ${COLOR_CYAN}    ✗${COLOR_RESET} %s  ← no en repo ni en HOME\n" "$f"
            done
        fi
    done

    # Resumen
    echo ""
    printf "  Resumen: ${COLOR_GREEN}%d activos${COLOR_RESET} | ${COLOR_RED}%d conflictos${COLOR_RESET} | ${COLOR_YELLOW}%d pendientes${COLOR_RESET} | %d ausentes | %d sin config\n" \
        "$count_ok" "$count_conflict" "$count_pending" "$count_absent" "$count_noconfig"
    echo ""

    if [ "$count_conflict" -gt 0 ]; then
        printf "  ${COLOR_BOLD}Para resolver conflictos:${COLOR_RESET}\n"
        printf "  Adoptar (laptop→repo):  ./main.sh adoptar  -p <paquete>\n"
        printf "  Instalar (repo→laptop): ./main.sh instalar -p <paquete>\n"
        echo ""
    fi
    if [ "$VERBOSE" = false ]; then
        printf "  ${COLOR_CYAN}Tip: ./main.sh estado --verbose  →  ver cada archivo${COLOR_RESET}\n\n"
    fi
}