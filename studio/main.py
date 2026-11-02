#!/usr/bin/python3
"""
main.py — Punto de entrada de Dotfiles Studio, la ventana OPCIONAL del gestor (el repo funciona sin ella, con ../main.sh).
Sin lógica: la aplicación se arma en dotfiles_app/aplicacion.py.

Corre con el Python del sistema (/usr/bin/python3), cuyo Qt es el que trae Kirigami; el PySide6 de un entorno de
pip o de Anaconda no puede cargar los módulos QML de KDE. Necesita `gui-comun` 2.1 o superior: instalado con pip
desde su repo público (dotfiles_app/__init__.py dice cómo) o señalado con la variable GUI_COMUN_DIR.

Uso:
    /usr/bin/python3 studio/main.py                      # desde ~/.dotfiles
    /usr/bin/python3 studio/main.py --smoke              # construye la interfaz y sale (prueba de humo)
    /usr/bin/python3 studio/main.py --instalar-lanzador  # el acceso directo del menú (-n simula; lo llama main.sh instalar-studio)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))      # el paquete del studio

from dotfiles_app import INSTALAR, faltan  # noqa: E402  (dotfiles_app localiza gui_comun al importarse, si puede)

if __name__ == "__main__":
    if faltan():
        print(f"Dotfiles Studio necesita {', '.join(faltan())}. Instálalo con:\n{INSTALAR}", file=sys.stderr)
        sys.exit(3)
    from dotfiles_app.aplicacion import main  # noqa: E402
    sys.exit(main(sys.argv[1:]))
