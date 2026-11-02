#!/usr/bin/env bash
# studio/tests/run.sh — corre las pruebas de Dotfiles Studio con pytest, con la carpeta temporal en disco y sin caché.
# Uso: studio/tests/run.sh [opciones de pytest]   (p. ej. -k estado)
# La carpeta temporal va a ~/.cache (no a /tmp, que es RAM). Las pruebas en proceso (servicio, modelos, controladores)
# usan el binding del Python que corre pytest (basta QtCore); las de QML y la de humo abren un proceso hijo con el
# Python del sistema (/usr/bin/python3, el del Qt con Kirigami) sin pantalla (QT_QPA_PLATFORM=offscreen) y con
# XDG_CONFIG_HOME temporal. Todas trabajan sobre un repo y un HOME falsos: nunca tocan los enlaces reales.
# PYTHON_PRUEBAS elige el intérprete de pytest (por omisión, el primero que lo tenga: /usr/bin/python3 o python3).
set -euo pipefail

DIR_PRUEBAS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_TMP="${XDG_CACHE_HOME:-$HOME/.cache}/pytest/dotfiles-studio"
mkdir -p "$BASE_TMP"

if [ -z "${PYTHON_PRUEBAS:-}" ]; then
    for candidato in /usr/bin/python3 python3; do
        if "$candidato" -c "import pytest" >/dev/null 2>&1; then PYTHON_PRUEBAS="$candidato"; break; fi
    done
fi
if [ -z "${PYTHON_PRUEBAS:-}" ]; then
    echo "studio/tests/run.sh: ningún Python con pytest (apt install python3-pytest)." >&2
    exit 3
fi

export PYTHONDONTWRITEBYTECODE=1
export QT_QPA_PLATFORM=offscreen
exec "$PYTHON_PRUEBAS" -m pytest "$DIR_PRUEBAS" --basetemp "$BASE_TMP" -p no:cacheprovider -q "$@"
