#!/usr/bin/env bash
# =============================================================================
# main.sh — Punto de entrada del gestor de dotfiles
# =============================================================================
# Orquesta todos los módulos. Su única responsabilidad es:
#   1. Cargar dependencias en el orden correcto
#   2. Parsear argumentos y detectar el comando
#   3. Delegar al módulo correspondiente
#   4. Retornar el código de salida apropiado
#
# NO contiene lógica de negocio. Todo el "cómo" está en lib/.
#
# Uso:
#   ./main.sh                    → Menú interactivo
#   ./main.sh <comando> [opts]   → Ejecución directa
#   ./main.sh --help             → Ver todos los comandos
# =============================================================================

# Fallar inmediatamente ante cualquier error no manejado.
# -e: salir en error, -u: error en variables no definidas,
# -o pipefail: el pipe falla si falla cualquier comando intermedio.
set -euo pipefail

# --- Resolución de la ruta del script ----------------------------------------
# Usar ${BASH_SOURCE[0]} en lugar de $0 garantiza que funciona tanto
# cuando se ejecuta directamente como cuando se hace source del script.
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Carga de módulos en orden de dependencia ---------------------------------
# El orden importa: config define las constantes que usan los demás módulos.
# shellcheck source=config.sh
source "${SCRIPT_DIR}/config.sh"

# shellcheck source=lib/logger.sh
source "${SCRIPT_DIR}/lib/logger.sh"

# shellcheck source=lib/validator.sh
source "${SCRIPT_DIR}/lib/validator.sh"

# shellcheck source=lib/cli.sh
source "${SCRIPT_DIR}/lib/cli.sh"

# shellcheck source=lib/tools.sh
source "${SCRIPT_DIR}/lib/tools.sh"

# shellcheck source=lib/stow_ops.sh
source "${SCRIPT_DIR}/lib/stow_ops.sh"

# shellcheck source=lib/git_ops.sh
source "${SCRIPT_DIR}/lib/git_ops.sh"

# --- Función principal --------------------------------------------------------

# main()
# Punto de entrada. Parsea argumentos y delega al módulo correcto.
#
# Arguments:
#   $@ - Todos los argumentos de la línea de comandos
main() {
    # Inicializar el directorio de logs
    mkdir -p "$LOG_DIR" 2>/dev/null || true

    log_info "Iniciando ${SCRIPT_NAME} v${VERSION} en ${DISTRO}"

    # Parsear argumentos y detectar el modo (menu, o un comando específico)
    parse_arguments "$@"

    # Si se detectó modo menú en parse_arguments, mostrar el menú
    if [ "$COMMAND" = "menu" ]; then
        show_menu
        # show_menu establece COMMAND y retorna; continuar con el dispatch
    fi

    # Si el menú o cli pidieron selección de paquetes específica
    if [ "$COMMAND" != "estado" ] && \
       [ "$COMMAND" != "sync-push" ] && \
       [ "$COMMAND" != "sync-pull" ] && \
       [ "$COMMAND" != "seguridad" ] && \
       [ "$COMMAND" != "backup" ] && \
       [ "$COMMAND" != "instalar-deps" ] && \
       [ ${#TARGET_PACKAGES[@]} -eq "${#STOW_PACKAGES[@]}" ] && \
       [ -t 0 ]; then
        # Solo pedir selección interactiva si:
        # - es terminal interactivo (-t 0)
        # - el comando opera sobre paquetes
        # - no se especificaron paquetes explícitamente (se usan todos por defecto)
        prompt_package_selection
    fi

    # --- Dispatch de comandos -------------------------------------------------
    case "$COMMAND" in
        instalar)
            install_configs
            ;;
        adoptar)
            adopt_configs
            ;;
        actualizar)
            update_configs
            ;;
        eliminar)
            remove_configs
            ;;
        sync-push)
            sync_push
            ;;
        sync-pull)
            sync_pull
            ;;
        estado)
            show_full_status
            ;;
        backup)
            create_backup "manual"
            list_backups
            ;;
        seguridad)
            validate_no_sensitive_data
            ;;
        instalar-deps)
            install_dependencies
            ;;
        "")
            log_error "No se especificó ningún comando."
            show_help
            exit 2
            ;;
        *)
            log_error "Comando desconocido: '${COMMAND}'"
            show_help
            exit 2
            ;;
    esac

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log_info "Operación finalizada correctamente."
    else
        log_error "La operación finalizó con errores (código: ${exit_code})."
    fi

    return $exit_code
}

# Ejecutar main solo si el script se llama directamente (no con source)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
