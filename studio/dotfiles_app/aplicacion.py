"""dotfiles_app/aplicacion.py — arma Dotfiles Studio: la aplicación (gui_comun.nucleo), los controladores, el registro
de acciones (menú, barra, menú contextual, paleta, atajos) y carga `qml/Main.qml`.

Toda operación existe una sola vez, aquí, en `Acciones`. «Ejecutar» (F5) y «Aplicar» (Ctrl+Intro) son dos acciones
cuyo texto, icono y disponibilidad cambian con la vista activa (`Espacio.vista`) y con la operación marcada; lo que
necesita un diálogo lo pide a QML por `Interfaz.pedir(nombre)`, y QML llama de vuelta a los controladores. Python no
construye interfaz; la ventana no escribe por su cuenta: toda orden es `main.sh` o `git`.
"""

from __future__ import annotations

from pathlib import Path

from gui_comun.acciones import Acciones, StandardKey
from gui_comun.consola import Consola
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QObject, Signal, Slot
from gui_comun.tareas import Tareas

from dotfiles_app import estado as est
from dotfiles_app.controladores.ajustes import Ajustes
from dotfiles_app.controladores.cambios import Cambios
from dotfiles_app.controladores.espacio import VISTAS, Espacio
from dotfiles_app.controladores.guia import Guia
from dotfiles_app.controladores.paquetes import OPERACIONES, Paquetes
from dotfiles_app.controladores.sistema import Sistema

APP_DIR = Path(__file__).resolve().parent
QML_DIR = APP_DIR / "qml"
RECURSOS_DIR = APP_DIR / "recursos"
APP_ID = "dotfiles-studio"
NOMBRE = "Dotfiles Studio"
APP_VERSION = "2.0.0"
ORG_NAME = "EdisonAchalma"
APP_NAME = "DotfilesStudio"            # el applicationName de QSettings de 1.x: las preferencias se conservan
DESCRIPCION = ("La configuración de la máquina, enlazada archivo por archivo desde el repo: el estado de cada paquete y de "
               "cada enlace, instalar, adoptar y eliminar por main.sh (simular antes, respaldo siempre), los cambios del "
               "repo con su diff entero y la confirmación por ruta tras el escáner de credenciales. El gestor de terminal "
               "(main.sh) sigue funcionando por su cuenta: la ventana es opcional.")
ACENTO = "indigo"                          # el icono del lanzador: la única marca del studio


def datos_lanzador() -> dict:
    return dict(app_id=APP_ID, nombre=NOMBRE, comentario="La configuración de la máquina: paquetes, enlaces, cambios y respaldos de ~/.dotfiles",
                orden=["/usr/bin/python3", str(APP_DIR.parent / "main.py")],
                logo_svg=(RECURSOS_DIR / "marca.svg").read_text(encoding="utf-8"), acento=ACENTO,
                categorias="Settings;", palabras="dotfiles;configuración;stow;kde;enlaces;")


class Interfaz(QObject):
    """Lo que Python pide a QML (abrir un diálogo, enfocar el filtro, seleccionar una fila) y poco más."""

    pedir = Signal(str, "QVariantMap")

    @Slot(str)
    def abrir(self, nombre: str) -> None:
        self.pedir.emit(nombre, {})


def construir(app: Aplicacion) -> dict:
    """Crea controladores y acciones, y los expone al QML. Devuelve lo creado (para las pruebas)."""
    consola = Consola()
    tareas = Tareas(consola)
    interfaz = Interfaz()
    ajustes = Ajustes()
    espacio = Espacio(consola, ajustes)
    paquetes = Paquetes(espacio, consola, tareas, detallado=ajustes.detallado)
    cambios = Cambios(espacio, consola, tareas)
    guia = Guia(espacio)
    sistema = Sistema(espacio, consola, tareas)
    acciones = Acciones()
    acciones.estandar(NOMBRE)
    pedir = lambda que, **datos: (lambda *_: interfaz.pedir.emit(que, datos))

    # la ruta sobre la que actúan Dolphin, terminal y copiar: lo seleccionado en la vista o, si no, el repo
    def objetivo() -> str:
        if espacio.vista == "paquetes":
            return paquetes.rutaSeleccionada
        if espacio.vista == "cambios":
            return cambios.rutaSeleccionada
        return guia.rutaAbsoluta if espacio.vista == "guia" else ""

    # --- Archivo
    acciones.registrar("archivo.dolphin", "Abrir en &Dolphin", "system-file-manager", None, "Archivo", al_disparar=lambda *_: espacio.abrirDolphin(objetivo()),
                       descripcion="Abre en el gestor de archivos la carpeta del paquete, del archivo o del cambio seleccionado (si no, el repo)")
    acciones.registrar("archivo.terminal", "Abrir &terminal aquí", "utilities-terminal", "Shift+F4", "Archivo", al_disparar=lambda *_: espacio.abrirTerminal(objetivo()))
    acciones.registrar("archivo.copiar", "&Copiar ruta", "edit-copy", "Ctrl+Shift+C", "Archivo", al_disparar=lambda *_: espacio.copiarRuta(objetivo()))
    # --- Editar
    acciones.registrar("editar.filtrar", "&Filtrar", "edit-find", StandardKey.Find, "Editar", al_disparar=pedir("filtrar"),
                       descripcion="Filtra el árbol de paquetes (por nombre o archivo) o la tabla de cambios")
    acciones.registrar("editar.todo", "Seleccionar &todo", "edit-select-all", StandardKey.SelectAll, "Editar", al_disparar=pedir("seleccionar_todo"))
    acciones.registrar("editar.expandir", "&Expandir todo", "expand-all", "Ctrl+Shift+Plus", "Editar", al_disparar=pedir("expandir"))
    acciones.registrar("editar.contraer", "&Contraer todo", "collapse-all", "Ctrl+Shift+Minus", "Editar", al_disparar=pedir("contraer"))
    # --- Ver › Vista
    for i, (nombre, texto, icono) in enumerate(VISTAS, start=1):
        acciones.registrar(f"ver.vista.{nombre}", f"&{i} {texto}", icono, f"Ctrl+{i}", "Ver › Vista", marcable=True,
                           al_disparar=lambda *_, n=nombre: espacio.fijarVista(n))
    # --- Acción (lo que hace la vista activa)
    acciones.registrar("herr.ejecutar", "&Simular", "system-run", StandardKey.Refresh, "Acción", al_disparar=lambda *_: ejecutar(),
                       descripcion="Paquetes: simula la operación marcada (--dry-run, no toca el disco) · Cambios: relee git · Guía: relee el documento")
    acciones.registrar("herr.aplicar", "&Aplicar", "dialog-ok-apply", "Ctrl+Return", "Acción", habilitada=False, al_disparar=pedir("aplicar"),
                       descripcion="Paquetes: la operación marcada, tras confirmar (con respaldo) · Cambios: confirma el archivo seleccionado tras el escáner")
    acciones.registrar("herr.cancelar", "&Cancelar la operación", "process-stop", None, "Acción", habilitada=False, al_disparar=tareas.cancelar)
    for nombre, texto, icono, descripcion in (("instalar", "&Instalar", "emblem-symbolic-link", "Crea los enlaces repo → HOME; con respaldo"),
                                              ("adoptar", "A&doptar", "document-import", "Lleva al repo los archivos reales de HOME y deja el enlace; con respaldo"),
                                              ("eliminar", "&Eliminar enlaces", "edit-delete", "Quita los enlaces de HOME; el repo no cambia")):
        acciones.registrar(f"op.{nombre}", texto, icono, None, "Operación", marcable=True, marcada=nombre == paquetes.operacion, descripcion=descripcion,
                           al_disparar=lambda *_, n=nombre: paquetes.fijarOperacion(n))
    acciones.registrar("op.detallado", "Salida &detallada (--verbose)", "view-list-details", None, "Operación", marcable=True, marcada=paquetes.detallado,
                       al_disparar=lambda marcada: setattr(paquetes, "detallado", bool(marcada)))
    acciones.registrar("op.forzar", "&Reemplazar los archivos reales (--force)", "document-replace", None, "Operación", marcable=True,
                       descripcion="Al instalar, sustituye por el enlace un archivo real de HOME (queda en .backups/); sin esto, main.sh lo salta",
                       al_disparar=lambda marcada: setattr(paquetes, "forzar", bool(marcada)))
    # --- Repositorio
    acciones.registrar("repo.releer", "&Releer el estado", "view-refresh", None, "Repositorio", descripcion="Vuelve a leer config.sh, los enlaces y git",
                       al_disparar=lambda *_: (paquetes.recargar(), cambios.recargar()))
    acciones.registrar("repo.seguridad", "&Escanear credenciales", "security-high", None, "Repositorio", al_disparar=sistema.seguridad,
                       descripcion="El escáner de datos sensibles de main.sh sobre lo versionado")
    acciones.registrar("repo.subir", "&Subir a GitHub…", "cloud-upload", None, "Repositorio", al_disparar=pedir("subir"),
                       descripcion="git push de la rama actual, tras confirmar (el repo es público)")
    # --- Herramientas (lo que no es un paquete)
    acciones.registrar("sistema.fuentes", "Instalar &fuentes de usuario…", "font", None, "Herramientas", al_disparar=pedir("sistema", nombre="fuentes"))
    acciones.registrar("sistema.dependencias", "Instalar &dependencias de la distribución…", "system-software-install", None, "Herramientas",
                       al_disparar=pedir("sistema", nombre="dependencias"))
    acciones.registrar("sistema.respaldo", "&Respaldo de la configuración…", "document-save-all", None, "Herramientas", al_disparar=pedir("sistema", nombre="respaldo"))
    # --- Guía y Ayuda
    acciones.registrar("guia.abrir", "Abrir el documento con el &sistema", "document-open", None, "Guía", al_disparar=guia.abrir)
    acciones.registrar("ayuda.manual", "&Manual (la Guía)", "help-contents", StandardKey.HelpContents, "Ayuda",
                       al_disparar=lambda *_: (guia.fijarDocumento("README.md"), espacio.fijarVista("guia")))

    acciones.definir_menus([
        ("&Archivo", ["archivo.dolphin", "archivo.terminal", "archivo.copiar", "|", "app.salir"]),
        ("&Editar", ["editar.filtrar", "editar.todo", "|", "editar.expandir", "editar.contraer"]),
        ("&Ver", ["ventana.navegacion", "ventana.detalles", "ventana.inferior", "|",
                  ("&Vista", [f"ver.vista.{n}" for n, *_r in VISTAS]), "|", "ventana.pantalla_completa"]),
        ("A&cción", ["herr.ejecutar", "herr.aplicar", "herr.cancelar", "|", "op.instalar", "op.adoptar", "op.eliminar", "|", "op.detallado", "op.forzar"]),
        ("&Repositorio", ["repo.releer", "repo.seguridad", "|", "repo.subir"]),
        ("&Herramientas", ["sistema.fuentes", "sistema.dependencias", "sistema.respaldo", "|", "guia.abrir", "|", "ventana.paleta"]),
        ("A&justes", ["app.ajustes"]),
        ("Ay&uda", ["ayuda.manual", "app.acerca"]),
    ])
    acciones.definir_barra(["herr.ejecutar", "herr.aplicar", "|", "repo.seguridad"])

    # la paleta: cada paquete y cada documento
    def entradas_paleta(_texto: str) -> list[dict]:
        salida = [{"nombre": f"paq.{p.nombre}", "texto": f"Paquete: {p.nombre}", "grupo": "Paquetes", "icono": "package-x-generic",
                   "ejecutar": lambda n=p.nombre: (espacio.fijarVista("paquetes"), interfaz.pedir.emit("seleccionar_paquete", {"fila": paquetes.filaDe(n)}))}
                  for p in paquetes._paquetes]
        salida += [{"nombre": f"doc.{d['ruta']}", "texto": f"Guía: {d['texto']}", "grupo": "Guía", "icono": "text-markdown",
                    "ejecutar": lambda r=d["ruta"]: (guia.fijarDocumento(r), espacio.fijarVista("guia"))} for d in est.documentos()]
        return salida
    acciones.anadir_fuente(entradas_paleta)

    # ------------------------------------------------- Ejecutar y Aplicar según la vista y la operación
    def ejecutar():
        {"paquetes": paquetes.simular, "cambios": cambios.recargar, "guia": guia.recargar}[espacio.vista]()

    def vista_cambiada():
        v = espacio.vista
        e, a = acciones.accion("herr.ejecutar"), acciones.accion("herr.aplicar")
        if v == "paquetes":
            e.texto, e.icono = f"&Simular {paquetes.operacion}", "system-run"
            a.texto, a.icono = f"&Aplicar {paquetes.operacion}…", {"instalar": "emblem-symbolic-link", "adoptar": "document-import", "eliminar": "edit-delete"}[paquetes.operacion]
        elif v == "cambios":
            e.texto, e.icono = "&Releer el estado de git", "view-refresh"
            a.texto, a.icono = "&Confirmar este archivo…", "vcs-commit"
        else:
            e.texto, e.icono = "&Releer el documento", "view-refresh"
        a.visible = v != "guia"
        for nombre in acciones.nombres():
            if nombre.startswith("ver.vista."):
                acciones.marcar(nombre, nombre == f"ver.vista.{v}")
        for nombre in ("editar.expandir", "editar.contraer", "op.instalar", "op.adoptar", "op.eliminar", "op.detallado", "op.forzar"):
            acciones.habilitar(nombre, v == "paquetes")
        acciones.habilitar("editar.todo", v != "guia")
        acciones.habilitar("guia.abrir", v == "guia")
        disponibilidad()

    def disponibilidad():
        v, activa = espacio.vista, tareas.activa
        puede = {"paquetes": paquetes.haySeleccion, "cambios": cambios.filaActual >= 0}.get(v, False)
        acciones.habilitar("herr.aplicar", bool(puede) and not activa)
        acciones.habilitar("herr.ejecutar", not activa and (v != "paquetes" or paquetes.haySeleccion))
        acciones.habilitar("herr.cancelar", activa)
        acciones.habilitar("repo.subir", cambios.hayParaSubir and not activa)
        acciones.habilitar("repo.seguridad", not activa)
        for nombre in ("sistema.fuentes", "sistema.dependencias", "sistema.respaldo", "repo.releer"):
            acciones.habilitar(nombre, not activa)

    def opciones_cambiadas():
        for nombre in OPERACIONES:
            acciones.marcar(f"op.{nombre}", nombre == paquetes.operacion)
        acciones.marcar("op.detallado", paquetes.detallado)
        acciones.marcar("op.forzar", paquetes.forzar)
        ajustes.detallado = paquetes.detallado
        vista_cambiada()

    def barra_estado():
        espacio.fijarResumen(paquetes.resumen)
        espacio.fijarContexto(cambios.contexto)

    espacio.vistaCambiada.connect(vista_cambiada)
    paquetes.opcionesCambiadas.connect(opciones_cambiadas)
    paquetes.seleccionCambiada.connect(disponibilidad)
    paquetes.cambiado.connect(barra_estado)
    paquetes.terminado.connect(lambda _c: cambios.recargar())           # instalar o adoptar cambian el repo
    cambios.cambiado.connect(barra_estado)
    cambios.filaCambiada.connect(disponibilidad)
    cambios.terminado.connect(lambda _c: paquetes.recargar())          # confirmar no cambia los enlaces, pero releer no cuesta
    sistema.terminado.connect(lambda _n, _c: (paquetes.recargar(), cambios.recargar()))
    tareas.cambiada.connect(disponibilidad)
    vista_cambiada()
    barra_estado()

    piezas = dict(consola=consola, tareas=tareas, interfaz=interfaz, ajustes=ajustes, espacio=espacio, paquetes=paquetes,
                  cambios=cambios, guia=guia, sistema=sistema, acciones=acciones)
    for nombre, objeto in piezas.items():
        app.exponer(nombre, objeto)
    app._piezas = piezas           # que vivan lo que la aplicación
    return piezas


def main(argv: list[str]) -> int:
    from gui_comun import lanzador
    atendido = lanzador.desde_main(argv, **datos_lanzador())         # --instalar-lanzador / --quitar-lanzador
    if atendido is not None:
        return atendido
    app = Aplicacion(APP_ID, NOMBRE, version=APP_VERSION, organizacion=ORG_NAME, nombre_ajustes=APP_NAME)
    construir(app)
    app.exponer("descripcionStudio", DESCRIPCION)
    return app.ejecutar(QML_DIR / "Main.qml", humo="--smoke" in argv)
