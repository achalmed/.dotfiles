"""studio/dotfiles_app/__init__.py — paquete de Dotfiles Studio; al importarse localiza `gui_comun`.

La ventana es opcional: el repo se instala antes que cualquier otra cosa y `main.sh` no depende de ella. Necesita el
binding de Qt del sistema (PySide6 o PyQt6 de apt, los únicos que cargan Kirigami) y `gui-comun` 3.0 o superior:

- instalado con pip desde su repo público, con versión fija (`INSTALAR`), o
- señalado con la variable de entorno `GUI_COMUN_DIR` (la carpeta del repo `gui-comun`, para desarrollar contra una
  copia local), que tiene prioridad sobre lo instalado.

Nunca se busca en otra carpeta: el repo no depende de ningún espacio de trabajo (docs/decisiones.md §La ventana).
"""

import importlib.util as _util
import os as _os
import sys as _sys

VERSION_GUI_COMUN = "v3.0.0"
INSTALAR = ("  sudo apt install python3-pyside6.qtquick python3-pyside6.qtquickcontrols2 qml6-module-org-kde-kirigami \\\n"
            "      qml6-module-org-kde-kirigamiaddons-formcard qml6-module-org-kde-desktop qml6-module-org-kde-syntaxhighlighting\n"
            f"  /usr/bin/python3 -m pip install --user --break-system-packages \"gui-comun @ git+https://github.com/achalmed/gui-comun@{VERSION_GUI_COMUN}\"\n"
            "  (o: ./main.sh instalar-deps, que lo recuerda al final)")

_dir = _os.environ.get("GUI_COMUN_DIR")
if _dir and _os.path.isdir(_os.path.join(_dir, "gui_comun")) and _dir not in _sys.path:
    _sys.path.insert(0, _dir)


def faltan() -> list[str]:
    """Los módulos que faltan para abrir la ventana (vacío si están todos)."""
    pendientes = []
    if _util.find_spec("PySide6") is None and _util.find_spec("PyQt6") is None:
        pendientes.append("PySide6 (python3-pyside6.*)")
    try:
        import gui_comun
        version = tuple(int(x) for x in gui_comun.__version__.split(".")[:2])
        if version < (3, 0):
            pendientes.append(f"gui_comun 3.0 o superior (hay {gui_comun.__version__})")
    except Exception:  # noqa: BLE001  (no está, o es un paquete vacío sin versión)
        pendientes.append("gui_comun (el paquete gui-comun)")
    return pendientes
