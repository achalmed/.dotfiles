#!/usr/bin/env python3
"""
main.py — Punto de entrada de Dotfiles Studio (opcional: el repo funciona sin ella, con ../main.sh).

Uso:
    python3 studio/main.py                           # desde ~/.dotfiles
    python3 studio/main.py --smoke                   # construye la interfaz y sale (prueba de humo)
    python3 studio/main.py --instalar-lanzador [-n]  # acceso directo en el menú (lo llama main.sh instalar-studio)
"""

import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI))

from dotfiles_app import INSTALAR, faltan  # noqa: E402

APP_ID = "dotfiles-studio"


def datos_lanzador() -> dict:
    from dotfiles_app.ventana import ACENTO, LOGO
    return dict(app_id=APP_ID, nombre="Dotfiles Studio", comentario="La configuración de la máquina: paquetes, enlaces, "
                "cambios y respaldos de ~/.dotfiles", orden=[sys.executable, str(_AQUI / "main.py")], logo_svg=LOGO,
                acento=ACENTO, categorias="Settings;", palabras="dotfiles;configuración;stow;kde;enlaces;")


def main() -> int:
    if faltan():
        print(f"Dotfiles Studio necesita {', '.join(faltan())}. Instálalo con:\n  {INSTALAR}", file=sys.stderr)
        return 3
    from gui_comun import lanzador
    atendido = lanzador.desde_main(sys.argv[1:], **datos_lanzador())   # --instalar-lanzador / --quitar-lanzador
    if atendido is not None:
        return atendido
    from gui_comun.diseno import preparar_plataforma
    preparar_plataforma()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    QApplication.setOrganizationName("EdisonAchalma")
    QApplication.setApplicationName("DotfilesStudio")
    QApplication.setDesktopFileName(APP_ID)
    app = QApplication([sys.argv[0]])
    from dotfiles_app.ventana import Ventana
    ventana = Ventana()
    ventana.show()
    if "--smoke" in sys.argv:
        QTimer.singleShot(0, app.quit)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
