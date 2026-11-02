#!/usr/bin/python3
"""
capturar.py — una captura de Dotfiles Studio para la documentación, con el repo real y sin tocar el escritorio ni las
preferencias: XDG_CONFIG_HOME temporal (con el aspecto del usuario copiado o con otro esquema de color de KDE),
1280 × 800, la vista y la fila pedidas, el panel inferior en Registro (la Salida de main.sh lleva rutas de HOME y el
repo es público: docs/rediseno.md D8) y, si se pide, la paleta de órdenes abierta.

Uso (desde ~/.dotfiles, con el Python del sistema):
    /usr/bin/python3 studio/capturar.py docs/figuras/dotfiles-studio-oscuro.png
    /usr/bin/python3 studio/capturar.py salida.png --esquema <ruta>/LliphiClaro.colors
    /usr/bin/python3 studio/capturar.py salida.png --vista paquetes --fila 4 --paleta "adop"
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))


def main() -> int:
    parser = argparse.ArgumentParser(description="Captura de Dotfiles Studio con el repo real")
    parser.add_argument("salida")
    parser.add_argument("--esquema", help="archivo .colors de KDE (relanza con XDG_CONFIG_HOME temporal)")
    parser.add_argument("--vista", default="paquetes", help="paquetes · cambios · guia")
    parser.add_argument("--filtro", default="todos", help="todos · atencion · activos (vista paquetes)")
    parser.add_argument("--fila", type=int, default=0, help="fila que queda seleccionada en el centro (−1: ninguna)")
    parser.add_argument("--pestana", type=int, default=0, help="pestaña del panel de detalles")
    parser.add_argument("--simular", action="store_true", help="corre la simulación (F5) antes de capturar")
    parser.add_argument("--paleta", default=None, help="abre la paleta de órdenes con este texto")
    parser.add_argument("--ancho", type=int, default=1280)
    parser.add_argument("--alto", type=int, default=800)
    args = parser.parse_args()

    if "DOTFILES_STUDIO_CAPTURA" not in os.environ:    # primera pasada: entorno temporal (y esquema) y relanzar
        import dotfiles_app  # noqa: F401  (localiza gui_comun)
        from gui_comun.galeria.esquema import entorno_con_esquema
        carpeta = Path(tempfile.mkdtemp(prefix="dotfiles-studio-captura-"))
        (carpeta / "config").mkdir(parents=True, exist_ok=True)
        config_usuario = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        for nombre in ("kdeglobals", "kcminputrc", "Kvantum"):      # el aspecto del usuario, copiado; sus preferencias no
            origen = config_usuario / nombre
            if origen.is_dir():
                shutil.copytree(origen, carpeta / "config" / nombre, dirs_exist_ok=True)
            elif origen.is_file():
                shutil.copy2(origen, carpeta / "config" / nombre)
        if args.esquema:
            env = entorno_con_esquema(Path(args.esquema).expanduser(), carpeta / "config")
        else:
            env = dict(os.environ, XDG_CONFIG_HOME=str(carpeta / "config"))
        env["XDG_CACHE_HOME"] = str(carpeta / "cache")
        env["DOTFILES_STUDIO_CAPTURA"] = "1"
        env.setdefault("QT_QPA_PLATFORMTHEME", "kde")     # sin pantalla, la paleta de Qt también lee el kdeglobals temporal
        orden = [sys.executable, str(AQUI / "capturar.py")] + [a for a in sys.argv[1:] if not a.startswith("--esquema") and a != args.esquema]
        return subprocess.run(orden, env=env).returncode

    from dotfiles_app import aplicacion
    from gui_comun.nucleo import Aplicacion
    from gui_comun.qt import QTimer

    app = Aplicacion(aplicacion.APP_ID, aplicacion.NOMBRE, version=aplicacion.APP_VERSION, nombre_ajustes=aplicacion.APP_NAME)
    piezas = aplicacion.construir(app)
    app.exponer("descripcionStudio", aplicacion.DESCRIPCION)
    espacio, paquetes, tareas = piezas["espacio"], piezas["paquetes"], piezas["tareas"]
    if not app.cargar(aplicacion.QML_DIR / "Main.qml"):
        return 1
    raiz = app.motor.rootObjects()[0]
    raiz.setProperty("width", args.ancho)
    raiz.setProperty("height", args.alto)
    espacio.fijarVista(args.vista)
    if args.vista == "paquetes":
        paquetes.fijarFiltro(args.filtro)
    def seleccionar():                                     # cuando la vista ya pintó el modelo
        if args.fila >= 0:
            piezas["interfaz"].pedir.emit("seleccionar_paquete" if args.vista == "paquetes" else "seleccionar_fila", {"fila": args.fila})
        if args.simular and args.vista == "paquetes":
            paquetes.simular()

    def listo():
        if tareas.activa:
            QTimer.singleShot(100, listo)
            return
        raiz.setProperty("mostrarDetalles", True)
        raiz.setProperty("mostrarInferior", True)
        inferior = raiz.property("inferior")
        if inferior is not None:
            inferior.setProperty("pestanaActual", 1)              # Registro: sin rutas de HOME
        QTimer.singleShot(300, lambda: piezas["interfaz"].pedir.emit("pestana", {"indice": args.pestana}))
        if args.paleta is not None:
            QTimer.singleShot(900, lambda: piezas["interfaz"].pedir.emit("paleta", {"texto": args.paleta}))
        app.capturar(args.salida, espera_ms=1800)

    QTimer.singleShot(400, seleccionar)
    QTimer.singleShot(900, listo)
    codigo = app.app.exec()
    app.cerrar()
    print("CAPTURA", args.salida)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
