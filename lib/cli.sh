#!/usr/bin/env bash
# =============================================================================
# lib/cli.sh — Parseo de argumentos y menú interactivo
# =============================================================================
# El script se puede usar de dos formas:
#   1. Modo CLI: ./main.sh <comando> [opciones]  → para scripts/automatización
#   2. Modo menú: ./main.sh                      → para uso interactivo
# Centralizar el parsing aquí mantiene main.sh limpio y la CLI extensible.
# =============================================================================

# --- Variables de estado global (modificadas por parse_arguments) -------------
COMMAND=""
TARGET_PACKAGES=()
VERBOSE=false
DRY_RUN=false
FORCE=false
NO_BACKUP=false

# parse_arguments()
# Parsea todos los argumentos pasados al script principal.
# Establece las variables globales de estado para que main.sh pueda
# delegar al módulo correcto.
#
# Arguments:
#   $@ - Todos los argumentos del script
parse_arguments() {
    if [ $# -eq 0 ]; then
        # Sin argumentos → modo menú interactivo
        COMMAND="menu"
        return 0
    fi

    COMMAND="$1"
    shift

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --verbose | -v)
                VERBOSE=true
                shift
                ;;
            --dry-run | -n)
                DRY_RUN=true
                log_warn "Modo simulación activado. No se realizarán cambios reales."
                shift
                ;;
            --force | -f)
                FORCE=true
                shift
                ;;
            --no-backup)
                NO_BACKUP=true
                shift
                ;;
            --packages | -p)
                # Acepta lista separada por comas: --packages git,shell,kde
                IFS=',' read -ra TARGET_PACKAGES <<< "$2"
                shift 2
                ;;
            --help | -h)
                show_help
                exit 0
                ;;
            --version)
                echo "${SCRIPT_NAME} v${VERSION} — Distro detectada: ${DISTRO}"
                exit 0
                ;;
            -*)
                log_error "Opción desconocida: $1"
                show_help
                exit 2
                ;;
            *)
                # Argumento posicional extra (ej: nombre de paquete suelto)
                TARGET_PACKAGES+=("$1")
                shift
                ;;
        esac
    done

    # Si no se especificaron paquetes, usar la lista completa de config.sh
    if [ ${#TARGET_PACKAGES[@]} -eq 0 ]; then
        TARGET_PACKAGES=("${STOW_PACKAGES[@]}")
    fi
}

# show_help()
# Imprime la ayuda completa del script con todos los comandos disponibles.
show_help() {
    cat << EOF

${COLOR_BOLD}${SCRIPT_NAME} v${VERSION}${COLOR_RESET}
Gestor de dotfiles para Arch Linux y Kubuntu con GNU Stow y Git.

${COLOR_BOLD}USO:${COLOR_RESET}
  $(basename "$0") [COMANDO] [OPCIONES]
  $(basename "$0")                          → Abre el menú interactivo

${COLOR_BOLD}COMANDOS:${COLOR_RESET}
  ${COLOR_GREEN}instalar${COLOR_RESET}       Crea symlinks desde el repo hacia la laptop (repo → laptop)
  ${COLOR_GREEN}adoptar${COLOR_RESET}        Mueve configs existentes de la laptop al repo (laptop → repo)
  ${COLOR_GREEN}actualizar${COLOR_RESET}     Actualiza symlinks existentes (re-stow)
  ${COLOR_GREEN}eliminar${COLOR_RESET}       Elimina symlinks sin borrar archivos del repo
  ${COLOR_GREEN}estado${COLOR_RESET}         Muestra estado de todos los symlinks y el repo Git
  ${COLOR_GREEN}sync-push${COLOR_RESET}      Guarda cambios locales y los sube a GitHub
  ${COLOR_GREEN}sync-pull${COLOR_RESET}      Descarga cambios desde GitHub y actualiza symlinks
  ${COLOR_GREEN}backup${COLOR_RESET}         Crea backup de configs actuales antes de hacer cambios
  ${COLOR_GREEN}seguridad${COLOR_RESET}      Escanea archivos en busca de datos sensibles
  ${COLOR_GREEN}instalar-deps${COLOR_RESET}  Instala dependencias según la distro detectada

${COLOR_BOLD}OPCIONES:${COLOR_RESET}
  -p, --packages LISTA  Paquetes específicos separados por coma (ej: git,shell,kde)
  -v, --verbose         Mostrar información detallada de cada operación
  -n, --dry-run         Simular sin realizar cambios reales
  -f, --force           Forzar operación aunque haya conflictos
      --no-backup       Omitir backup automático antes de operaciones destructivas
  -h, --help            Mostrar esta ayuda
      --version         Mostrar versión y distro detectada

${COLOR_BOLD}EJEMPLOS:${COLOR_RESET}
  $(basename "$0") instalar                        # Instala todos los paquetes
  $(basename "$0") instalar -p git,shell,kde        # Solo esos paquetes
  $(basename "$0") adoptar -p zotero               # Adopta solo zotero
  $(basename "$0") sync-push                       # Guarda y sube a GitHub
  $(basename "$0") estado                          # Ver estado actual
  $(basename "$0") instalar --dry-run --verbose    # Simular instalación

${COLOR_BOLD}DISTRO DETECTADA:${COLOR_RESET} ${DISTRO}
${COLOR_BOLD}DOTFILES_DIR:${COLOR_RESET}     ${DOTFILES_DIR}

EOF
}

# show_menu()
# Menú interactivo principal. Se muestra cuando no se pasan argumentos.
# Diseñado para usuarios que prefieren no memorizar comandos.
show_menu() {
    while true; do
        clear
        cat << EOF
${COLOR_BOLD}${COLOR_CYAN}
  ╔══════════════════════════════════════════════════╗
  ║         GESTOR DE DOTFILES — ${SCRIPT_NAME}        ║
  ║         Distro: ${DISTRO} | v${VERSION}              ║
  ╚══════════════════════════════════════════════════╝
${COLOR_RESET}
  ${COLOR_BOLD}── CONFIGURACIÓN LOCAL ──────────────────────────${COLOR_RESET}
  ${COLOR_GREEN}1)${COLOR_RESET} Instalar configs del repo → laptop
  ${COLOR_GREEN}2)${COLOR_RESET} Adoptar configs existentes de laptop → repo
  ${COLOR_GREEN}3)${COLOR_RESET} Actualizar symlinks (re-stow)
  ${COLOR_GREEN}4)${COLOR_RESET} Eliminar symlinks

  ${COLOR_BOLD}── SINCRONIZACIÓN CON GITHUB ─────────────────────${COLOR_RESET}
  ${COLOR_GREEN}5)${COLOR_RESET} Subir cambios a GitHub (push)
  ${COLOR_GREEN}6)${COLOR_RESET} Descargar cambios desde GitHub (pull)

  ${COLOR_BOLD}── HERRAMIENTAS ─────────────────────────────────${COLOR_RESET}
  ${COLOR_GREEN}7)${COLOR_RESET} Ver estado (symlinks + Git)
  ${COLOR_GREEN}8)${COLOR_RESET} Crear backup de configuraciones actuales
  ${COLOR_GREEN}9)${COLOR_RESET} Escanear datos sensibles
  ${COLOR_GREEN}10)${COLOR_RESET} Instalar dependencias del sistema

  ${COLOR_RED}0)${COLOR_RESET} Salir

EOF
        printf "  Elige una opción: "
        read -r choice

        case "$choice" in
            1) COMMAND="instalar";   return 0 ;;
            2) COMMAND="adoptar";    return 0 ;;
            3) COMMAND="actualizar"; return 0 ;;
            4) COMMAND="eliminar";   return 0 ;;
            5) COMMAND="sync-push";  return 0 ;;
            6) COMMAND="sync-pull";  return 0 ;;
            7) COMMAND="estado";     return 0 ;;
            8) COMMAND="backup";     return 0 ;;
            9) COMMAND="seguridad";  return 0 ;;
            10) COMMAND="instalar-deps"; return 0 ;;
            0)
                log_info "Saliendo del gestor de dotfiles."
                exit 0
                ;;
            *)
                log_warn "Opción inválida. Elige un número del 0 al 10."
                sleep 1
                ;;
        esac
    done
}

# confirm_action()
# Pide confirmación al usuario antes de operaciones potencialmente destructivas.
# El DRY_RUN y FORCE modifican este comportamiento.
#
# Arguments:
#   $1 - Mensaje de confirmación a mostrar
#
# Returns:
#   0 si el usuario confirma o FORCE=true
#   1 si el usuario cancela
confirm_action() {
    local message="$1"

    if [ "$FORCE" = true ]; then
        return 0
    fi

    printf "\n  ${COLOR_YELLOW}⚠  %s${COLOR_RESET}\n" "$message"
    printf "  ¿Continuar? [s/N]: "
    read -r response

    case "$response" in
        [sS] | [sS][iI])
            return 0
            ;;
        *)
            log_info "Operación cancelada por el usuario."
            return 1
            ;;
    esac
}

# prompt_package_selection()
# En modo interactivo, permite elegir paquetes específicos o todos.
# Útil cuando el usuario no recuerda exactamente qué paquetes tiene.
#
# Returns (via TARGET_PACKAGES global):
#   Lista de paquetes seleccionados
prompt_package_selection() {
    echo ""
    log_section "Selección de paquetes"
    echo "  Paquetes disponibles:"
    local i=1
    for pkg in "${STOW_PACKAGES[@]}"; do
        printf "  %2d) %s\n" "$i" "$pkg"
        ((i++))
    done
    printf "  %2d) %s\n" "0" "Todos los paquetes"
    echo ""
    printf "  Ingresa números separados por coma (o 0 para todos): "
    read -r selection

    if [ "$selection" = "0" ] || [ -z "$selection" ]; then
        TARGET_PACKAGES=("${STOW_PACKAGES[@]}")
        log_info "Seleccionados todos los paquetes."
        return
    fi

    TARGET_PACKAGES=()
    IFS=',' read -ra selections <<< "$selection"
    for num in "${selections[@]}"; do
        num=$(echo "$num" | tr -d ' ')
        if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#STOW_PACKAGES[@]}" ]; then
            TARGET_PACKAGES+=("${STOW_PACKAGES[$((num - 1))]}")
        else
            log_warn "Número inválido ignorado: ${num}"
        fi
    done

    if [ ${#TARGET_PACKAGES[@]} -eq 0 ]; then
        log_warn "No se seleccionaron paquetes válidos. Usando todos."
        TARGET_PACKAGES=("${STOW_PACKAGES[@]}")
    fi
}
