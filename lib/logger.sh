#!/usr/bin/env bash
# =============================================================================
# lib/logger.sh — Sistema de logging centralizado
# =============================================================================
# Todas las salidas pasan por estas funciones para garantizar formato
# consistente tanto en consola como en el archivo de log diario.
# Los mensajes de ERROR y WARN van a stderr para no contaminar stdout
# cuando el script se usa en pipelines.
# =============================================================================

# _ensure_log_dir()
# Crea el directorio de logs si no existe.
# Se llama una sola vez al inicializar el logger.
_ensure_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR" || {
            echo "[ERROR] No se pudo crear el directorio de logs: $LOG_DIR" >&2
            return 1
        }
    fi
}

# _write_log()
# Función interna: escribe una línea formateada tanto en consola como en archivo.
#
# Arguments:
#   $1 - Nivel (INFO, WARN, ERROR, DEBUG, SUCCESS)
#   $2 - Mensaje
#   $3 - Color ANSI para consola (opcional)
_write_log() {
    local level="$1"
    local message="$2"
    local color="${3:-}"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local formatted_line="[${level}] ${timestamp} - ${message}"

    # Salida en consola (con color si disponible)
    if [ -n "$color" ]; then
        printf "${color}%s${COLOR_RESET}\n" "$formatted_line"
    else
        printf "%s\n" "$formatted_line"
    fi

    # Salida en archivo (sin códigos de color)
    if [ -n "${LOG_FILE:-}" ]; then
        _ensure_log_dir
        printf "%s\n" "$formatted_line" >> "$LOG_FILE" 2>/dev/null || true
        # El '|| true' es intencional: si el log falla (disco lleno, permisos),
        # no debe interrumpir la operación principal.
    fi
}

# log_info()
# Mensajes informativos de progreso normal.
#
# Arguments:
#   $1 - Mensaje a registrar
log_info() {
    _write_log "INFO   " "$1" "${COLOR_CYAN}"
}

# log_success()
# Confirmación de operaciones completadas exitosamente.
#
# Arguments:
#   $1 - Mensaje a registrar
log_success() {
    _write_log "SUCCESS" "$1" "${COLOR_GREEN}"
}

# log_warn()
# Advertencias: la operación continuó pero hay algo que revisar.
#
# Arguments:
#   $1 - Mensaje a registrar
log_warn() {
    _write_log "WARN   " "$1" "${COLOR_YELLOW}" >&2
}

# log_error()
# Errores: la operación falló o hay un problema crítico.
#
# Arguments:
#   $1 - Mensaje a registrar
log_error() {
    _write_log "ERROR  " "$1" "${COLOR_RED}" >&2
}

# log_section()
# Imprime un separador visual para distinguir secciones en la salida.
#
# Arguments:
#   $1 - Título de la sección
log_section() {
    local title="$1"
    local line="════════════════════════════════════════════════════"
    printf "\n${COLOR_BOLD}%s${COLOR_RESET}\n" "$line"
    printf "${COLOR_BOLD}  %s${COLOR_RESET}\n" "$title"
    printf "${COLOR_BOLD}%s${COLOR_RESET}\n\n" "$line"
    _write_log "SECTION" "$title" ""
}

# log_step()
# Imprime un paso numerado dentro de una sección.
#
# Arguments:
#   $1 - Número del paso
#   $2 - Descripción del paso
log_step() {
    local step_num="$1"
    local description="$2"
    printf "  ${COLOR_BOLD}[%s]${COLOR_RESET} %s\n" "$step_num" "$description"
}
