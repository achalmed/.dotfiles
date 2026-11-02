#!/usr/bin/python3
"""
capturar.py — una captura de Dotfiles Studio para la documentación, sin tocar el escritorio ni las preferencias:
XDG_CONFIG_HOME temporal (con el aspecto del usuario copiado o con otro esquema de color de KDE), 1360 × 860, la página,
el paquete, la operación y el archivo pedidos y, si se pide, la simulación, el escáner o la paleta de órdenes.

Con `--muestra` (lo que usa docs/figuras/), el repo y el HOME son los inventados de `muestra.py` en una carpeta
temporal: ninguna ruta ni configuración de la máquina en pantalla. Sin él, el repo real y el HOME real (solo lectura;
el panel inferior queda en Registro, porque la Salida de main.sh lleva rutas de HOME y el repo es público).

Uso (desde la raíz del repo, con el Python del sistema):
    /usr/bin/python3 studio/capturar.py docs/figuras/dotfiles-studio-oscuro.png --muestra --esquema <ruta>/LliphiOscuro.colors
    /usr/bin/python3 studio/capturar.py salida.png --muestra --paquete shell --operacion adoptar --archivo .zshrc
    /usr/bin/python3 studio/capturar.py salida.png --muestra --pagina seguridad --escanear
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
    parser = argparse.ArgumentParser(description="Captura de Dotfiles Studio")
    parser.add_argument("salida")
    parser.add_argument("--esquema", help="archivo .colors de KDE (relanza con XDG_CONFIG_HOME temporal)")
    parser.add_argument("--muestra", action="store_true", help="repo y HOME de muestra en una carpeta temporal")
    parser.add_argument("--pagina", default="paquetes", help="paquetes · cambios · seguridad · sistema · guia")
    parser.add_argument("--filtro", default="todos", help="todos · atencion · activos · cambios (portada)")
    parser.add_argument("--paquete", default="", help="abre la página de este paquete")
    parser.add_argument("--operacion", default="", help="instalar · adoptar · actualizar · eliminar")
    parser.add_argument("--forzar", action="store_true", help="marca «Reemplazar los archivos reales»")
    parser.add_argument("--archivo", default="", help="el archivo del paquete (o de Cambios) que se compara")
    parser.add_argument("--pestana", type=int, default=0, help="pestaña de la página del paquete (0 comparación · 1 simulación · 2 detalles)")
    parser.add_argument("--simular", action="store_true", help="simula la operación antes de capturar")
    parser.add_argument("--escanear", action="store_true", help="corre el escáner de credenciales antes de capturar")
    parser.add_argument("--confirmar", action="store_true", help="abre el diálogo de confirmación de la operación")
    parser.add_argument("--paleta", default=None, help="abre la paleta de órdenes con este texto")
    parser.add_argument("--ancho", type=int, default=1360)
    parser.add_argument("--alto", type=int, default=860)
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
            # con QApplication (gui-comun 3.0) los controles los pinta Kvantum con la paleta de su tema: el tema de Kvantum
            # va a juego con el esquema forzado (LliphiOscuro.colors → LliphiOscuro), o salen claros
            env = entorno_con_esquema(Path(args.esquema).expanduser(), carpeta / "config")
            tema = Path(args.esquema).stem
            kv = carpeta / "config" / "Kvantum"
            if (kv / tema).is_dir():
                (kv / "kvantum.kvconfig").write_text(f"[General]\ntheme={tema}\n", encoding="utf-8")
        else:
            env = dict(os.environ, XDG_CONFIG_HOME=str(carpeta / "config"))
        env["XDG_CACHE_HOME"] = str(carpeta / "cache")
        env["DOTFILES_STUDIO_CAPTURA"] = "1"
        env.setdefault("QT_QPA_PLATFORMTHEME", "kde")
        if args.muestra:
            import muestra
            repo, casa = muestra.crear(carpeta / "muestra")
            env.update(muestra.ENTORNO_GIT, DOTFILES_DIR=str(repo), HOME=str(casa))
            env["XDG_DATA_HOME"] = env.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")   # las fuentes del usuario
            env.setdefault("PYTHONUSERBASE", str(Path.home() / ".local"))                               # gui-comun de pip
        orden = [sys.executable, str(AQUI / "capturar.py")] + [a for a in sys.argv[1:] if not a.startswith("--esquema") and a != args.esquema]
        r = subprocess.run(orden, env=env).returncode
        shutil.rmtree(carpeta, ignore_errors=True)
        return r

    from dotfiles_app import aplicacion
    from gui_comun.nucleo import Aplicacion
    from gui_comun.qt import QTimer

    app = Aplicacion(aplicacion.APP_ID, aplicacion.NOMBRE, version=aplicacion.APP_VERSION, nombre_ajustes=aplicacion.APP_NAME)
    piezas = aplicacion.construir(app)
    app.exponer("descripcionStudio", aplicacion.DESCRIPCION)
    if not app.cargar(aplicacion.QML_DIR / "Main.qml"):
        return 1
    raiz = app.motor.rootObjects()[0]
    raiz.setProperty("width", args.ancho)
    raiz.setProperty("height", args.alto)
    espacio, catalogo, tareas, acciones = piezas["espacio"], piezas["catalogo"], piezas["tareas"], piezas["acciones"]

    def preparar():
        espacio.fijarVista(args.pagina)
        catalogo.fijarFiltro(args.filtro)
        if args.paquete:
            catalogo.abrir(args.paquete)
            if args.operacion:
                catalogo.fijarOperacion(args.operacion)
            catalogo.forzar = args.forzar
            if args.archivo:
                catalogo.fijarArchivo(args.archivo)
        if args.pagina == "cambios" and args.archivo:
            fila = next((i for i, f in enumerate(piezas["cambios"]._filas) if f["ruta"].endswith(args.archivo)), -1)
            QTimer.singleShot(300, lambda: piezas["interfaz"].pedir.emit("seleccionar_cambio", {"fila": fila}))
        if args.simular:
            catalogo.simular()
        if args.escanear:
            piezas["seguridad"].escanear()

    def listo():
        if tareas.activa:
            QTimer.singleShot(100, listo)
            return
        raiz.setProperty("pestanaPaquete", args.pestana)
        if args.confirmar and args.paquete:
            acciones.accion(f"paq.{catalogo.operacion}").disparar()
        if args.paleta is not None:
            QTimer.singleShot(600, lambda: piezas["interfaz"].pedir.emit("paleta", {"texto": args.paleta}))
        app.capturar(args.salida, espera_ms=1800)

    QTimer.singleShot(300, preparar)
    QTimer.singleShot(900, listo)
    codigo = app.app.exec()
    app.cerrar()
    print("CAPTURA", args.salida)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
