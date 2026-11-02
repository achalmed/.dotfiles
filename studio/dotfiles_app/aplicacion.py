"""dotfiles_app/aplicacion.py — arma Dotfiles Studio: la aplicación (gui_comun.nucleo), los controladores, el registro
de acciones (menú, botones, paleta, atajos) y carga `qml/Main.qml`.

Reingeniería del 2026-11-02 (docs/reingenieria.md): un gestor de paquetes de configuración al estilo de Discover. Cada
operación existe una vez, aquí, en `Acciones`, con su estado (lectura, simulación, escritura, instalación,
publicación, eliminación). Instalar, adoptar, actualizar y quitar enlaces piden confirmación con las consecuencias
calculadas del plan por archivo; lo que necesita un diálogo propio lo pide a QML por `Interfaz.pedir(nombre)`. Python no
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
from dotfiles_app.controladores.catalogo import Catalogo
from dotfiles_app.controladores.espacio import VISTAS, Espacio
from dotfiles_app.controladores.guia import Guia
from dotfiles_app.controladores.seguridad import Seguridad
from dotfiles_app.controladores.sistema import ESTADO_OPERACION as ESTADO_SISTEMA, OPERACIONES as SISTEMA, Sistema
from dotfiles_app.servicios import plan

APP_DIR = Path(__file__).resolve().parent
QML_DIR = APP_DIR / "qml"
RECURSOS_DIR = APP_DIR / "recursos"
APP_ID = "dotfiles-studio"
NOMBRE = "Dotfiles Studio"
APP_VERSION = "3.0.0"
ORG_NAME = "EdisonAchalma"
APP_NAME = "DotfilesStudio"            # el applicationName de QSettings de 1.x: las preferencias se conservan
DESCRIPCION = ("Un gestor de paquetes de configuración: cada paquete con su aplicación, sus archivos y su estado; antes de "
               "instalar, adoptar, actualizar o quitar enlaces, la comparación del repo con HOME, el plan de cada archivo y la "
               "orden exacta de main.sh (simular antes, respaldo siempre); los cambios del repo lado a lado, el escáner de "
               "credenciales que nunca muestra el secreto y lo que el sistema necesita. El gestor de terminal (main.sh) sigue "
               "funcionando por su cuenta: la ventana es opcional.")
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
    espacio = Espacio(consola, ajustes, getattr(app, "escritorio", None))
    catalogo = Catalogo(espacio, consola, tareas, detallado=ajustes.detallado)
    cambios = Cambios(espacio, consola, tareas)
    seguridad = Seguridad(consola, tareas)
    guia = Guia(espacio)
    sistema = Sistema(espacio, consola, tareas)
    acciones = Acciones()
    acciones.estandar(NOMBRE, paneles=False, atajos={"ventana.pantalla_completa": "F11"})
    pedir = lambda que, **datos: (lambda *_: interfaz.pedir.emit(que, datos))

    # la ruta sobre la que actúan Dolphin, abrir, terminal y copiar: lo elegido en la página o, si no, el repo
    def objetivo() -> str:
        if espacio.vista == "paquetes" and catalogo.abierto:
            rel = catalogo.archivo
            if rel and (est.repo() / catalogo.abierto / rel).exists():
                return catalogo.rutaEnRepo(rel)
            return catalogo.rutaEnHome(rel) if rel else catalogo.rutaEnRepo("")
        if espacio.vista == "cambios":
            return cambios.rutaSeleccionada
        if espacio.vista == "guia":
            return guia.rutaAbsoluta
        return ""

    # --- Archivo
    acciones.registrar("archivo.dolphin", "Mostrar en &Dolphin", "system-file-manager", "Ctrl+Alt+D", "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.abrirDolphin(objetivo()),
                       descripcion="Abre Dolphin con el archivo elegido señalado (en el repo; si solo está en HOME, en HOME)")
    acciones.registrar("archivo.abrir", "Abrir con la &aplicación", "document-open", None, "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.abrirConAplicacion(objetivo()),
                       descripcion="Abre el archivo elegido con la aplicación que el escritorio asocia a su tipo")
    acciones.registrar("archivo.terminal", "Abrir &terminal aquí", "utilities-terminal", "Shift+F4", "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.abrirTerminal(objetivo()))
    acciones.registrar("archivo.copiar", "&Copiar ruta", "edit-copy", "Ctrl+Shift+C", "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.copiarRuta(objetivo()))
    # --- Editar
    acciones.registrar("editar.buscar", "&Buscar paquetes", "edit-find", StandardKey.Find, "Editar", al_disparar=pedir("buscar"),
                       descripcion="Busca por paquete, aplicación o ruta de un archivo")
    # --- Ver
    for i, (nombre, texto, icono) in enumerate(VISTAS, start=1):
        acciones.registrar(f"ver.pagina.{nombre}", f"&{i} {texto}", icono, f"Ctrl+{i}", "Ver", marcable=True,
                           al_disparar=lambda *_, n=nombre: (espacio.fijarVista(n), acciones.marcar(f"ver.pagina.{n}", True)))
    acciones.registrar("ver.portada", "&Volver a la portada", "go-previous", "Alt+Left", "Ver", al_disparar=lambda *_: (catalogo.cerrar(), espacio.fijarVista("paquetes")),
                       descripcion="Cierra la página del paquete y vuelve a las tarjetas")
    acciones.registrar("ver.salida", "&Salida y registro", "utilities-terminal", "F4", "Ver", marcable=True, al_disparar=pedir("salida"),
                       descripcion="La salida íntegra de main.sh y git, y el registro")
    # --- Paquete: la operación elegida en la página, simulada o aplicada, y las cuatro con su confirmación
    acciones.registrar("paq.simular", "&Simular", "view-preview", "Ctrl+Shift+Return", "Paquete", operacion="simulacion",
                       al_disparar=lambda *_: catalogo.simular(), descripcion="La operación elegida con --dry-run: no toca el disco")
    acciones.registrar("paq.aplicar", "&Aplicar…", "dialog-ok-apply", "Ctrl+Return", "Paquete", al_disparar=lambda *_: aplicar(),
                       descripcion="Paquetes: la operación elegida, tras confirmar · Cambios: confirma el archivo elegido")
    for op, icono in (("instalar", "emblem-symbolic-link"), ("adoptar", "document-import"), ("actualizar", "view-refresh"), ("eliminar", "edit-delete")):
        acciones.registrar(f"paq.{op}", f"{plan.TEXTO[op]}…", icono, None, "Paquete", operacion=plan.ESTADO_OPERACION[op], confirmar=True,
                           consecuencias=lambda o=op: catalogo.consecuencias(o), descripcion=plan.QUE_HACE[op],
                           al_disparar=lambda *_, o=op: (catalogo.fijarOperacion(o), catalogo.aplicar(o)))
    acciones.registrar("paq.forzar", "&Reemplazar los archivos reales (--force)", "document-replace", None, "Paquete", marcable=True,
                       descripcion="Al instalar, sustituye por el enlace un archivo real de HOME (queda en .backups/); sin esto, main.sh lo salta",
                       al_disparar=lambda marcada: setattr(catalogo, "forzar", bool(marcada)))
    acciones.registrar("paq.detallado", "Salida &detallada (--verbose)", "view-list-details", None, "Paquete", marcable=True, marcada=catalogo.detallado,
                       al_disparar=lambda marcada: setattr(catalogo, "detallado", bool(marcada)))
    acciones.registrar("paq.cancelar", "&Cancelar la operación", "process-stop", None, "Paquete", habilitada=False, al_disparar=tareas.cancelar)
    # --- Repositorio
    acciones.registrar("repo.releer", "&Releer el estado", "view-refresh", StandardKey.Refresh, "Repositorio", operacion="lectura",
                       al_disparar=lambda *_: (catalogo.recargar(), cambios.recargar()), descripcion="Vuelve a leer config.sh, los enlaces de HOME y git")
    acciones.registrar("repo.subir", "&Subir a GitHub…", "cloud-upload", None, "Repositorio", operacion="publicacion", confirmar=True,
                       consecuencias=lambda: (f"Se publican {cambios.adelante} commit(s) de la rama {cambios.rama} en GitHub con «git push». "
                                              "El repo es público: lo confirmado queda a la vista de todos."),
                       al_disparar=lambda *_: cambios.subir(), descripcion="git push de la rama actual (el repo es público)")
    # --- Seguridad
    acciones.registrar("seg.escanear", "&Escanear credenciales", "security-high", "Ctrl+Alt+S", "Seguridad", operacion="lectura",
                       al_disparar=lambda *_: (espacio.fijarVista("seguridad"), seguridad.escanear()),
                       descripcion="Busca claves, tokens, contraseñas y .env en lo que subiría un git add . (sin mostrar el valor)")
    acciones.registrar("seg.main", "Escanear con &main.sh", "utilities-terminal", None, "Seguridad", operacion="lectura",
                       al_disparar=lambda *_: seguridad.escanearConMainSh(), descripcion="./main.sh seguridad, con su salida en la consola")
    acciones.registrar("seg.copiar", "&Copiar el informe", "edit-copy", None, "Seguridad", operacion="lectura", al_disparar=lambda *_: seguridad.copiarInforme(),
                       descripcion="Archivo, línea, tipo y huella de cada hallazgo, en Markdown (sin los valores)")
    # --- Sistema
    for nombre, (titulo, _o, _x, sudo) in SISTEMA.items():
        acciones.registrar(f"sistema.{nombre}", f"{titulo}…", {"fuentes": "font", "dependencias": "system-software-install", "respaldo": "document-save-all"}[nombre],
                           None, "Sistema", operacion=ESTADO_SISTEMA[nombre], confirmar=True, consecuencias=lambda n=nombre: sistema.consecuencias(n),
                           al_disparar=lambda *_, n=nombre: sistema.correr(n, False))
    # --- Guía y Ayuda
    acciones.registrar("guia.abrir", "Abrir el documento con el &sistema", "document-open", None, "Guía", operacion="lectura", al_disparar=guia.abrir)
    acciones.registrar("ayuda.manual", "&Manual (la Guía)", "help-contents", StandardKey.HelpContents, "Ayuda",
                       al_disparar=lambda *_: (guia.fijarDocumento("README.md"), espacio.fijarVista("guia")))

    acciones.definir_menus([
        ("&Archivo", ["archivo.dolphin", "archivo.abrir", "archivo.terminal", "archivo.copiar", "|", "app.salir"]),
        ("&Editar", ["editar.buscar"]),
        ("&Ver", [f"ver.pagina.{n}" for n, *_r in VISTAS] + ["|", "ver.portada", "|", "ver.salida", "ventana.pantalla_completa"]),
        ("&Paquete", ["paq.simular", "paq.aplicar", "paq.cancelar", "|", "paq.instalar", "paq.adoptar", "paq.actualizar", "paq.eliminar", "|",
                      "paq.forzar", "paq.detallado"]),
        ("&Repositorio", ["repo.releer", "|", "seg.escanear", "seg.main", "seg.copiar", "|", "repo.subir"]),
        ("&Sistema", ["sistema.dependencias", "sistema.fuentes", "sistema.respaldo", "|", "ventana.paleta"]),
        ("A&justes", ["app.ajustes"]),
        ("Ay&uda", ["ayuda.manual", "guia.abrir", "|", "app.acerca"]),
    ])
    acciones.definir_barra(["repo.releer", "|", "paq.simular", "paq.aplicar", "|", "seg.escanear"])

    # la paleta: cada paquete y cada documento
    def entradas_paleta(_texto: str) -> list[dict]:
        salida = [{"nombre": f"paquete.{p.nombre}", "texto": f"Paquete: {p.nombre} ({est.aplicacion(p.nombre)['nombre']})", "grupo": "Paquetes",
                   "icono": est.aplicacion(p.nombre)["icono"],
                   "ejecutar": lambda n=p.nombre: (espacio.fijarVista("paquetes"), catalogo.abrir(n))}
                  for p in catalogo._paquetes]
        salida += [{"nombre": f"doc.{d['ruta']}", "texto": f"Guía: {d['texto']}", "grupo": "Guía", "icono": "text-markdown",
                    "ejecutar": lambda r=d["ruta"]: (guia.fijarDocumento(r), espacio.fijarVista("guia"))} for d in est.documentos()]
        return salida
    acciones.anadir_fuente(entradas_paleta)

    # ------------------------------------------------- Aplicar según la página y lo que se puede hacer
    def aplicar():
        if espacio.vista == "paquetes" and catalogo.abierto:
            acciones.accion(f"paq.{catalogo.operacion}").disparar()          # pide la confirmación con sus consecuencias
        elif espacio.vista == "cambios":
            interfaz.pedir.emit("confirmar", {})

    def disponibilidad():
        v, activa = espacio.vista, tareas.activa
        en_pagina = v == "paquetes" and bool(catalogo.abierto)
        for op in plan.OPERACIONES:
            acciones.habilitar(f"paq.{op}", en_pagina and not activa and catalogo.puede(op))
        acciones.habilitar("paq.simular", en_pagina and not activa)
        acciones.habilitar("paq.aplicar", not activa and ((en_pagina and catalogo.puede(catalogo.operacion)) or (v == "cambios" and cambios.filaActual >= 0)))
        acciones.habilitar("paq.forzar", en_pagina)
        acciones.habilitar("paq.cancelar", activa)
        acciones.habilitar("ver.portada", en_pagina)
        acciones.habilitar("repo.subir", cambios.hayParaSubir and not activa)
        for nombre in ("seg.escanear", "seg.main", "repo.releer", *[f"sistema.{n}" for n in SISTEMA]):
            acciones.habilitar(nombre, not activa)
        acciones.habilitar("seg.copiar", seguridad.escaneado)
        acciones.habilitar("guia.abrir", v == "guia")
        a = acciones.accion("paq.aplicar")
        if v == "cambios":
            a.texto, a.icono = "&Confirmar este archivo…", "vcs-commit"
        else:
            a.texto, a.icono = f"&{plan.TEXTO[catalogo.operacion]}…", acciones.accion(f"paq.{catalogo.operacion}").icono
        acciones.accion("paq.simular").texto = f"&Simular «{plan.TEXTO[catalogo.operacion].lower()}»"

    def vista_cambiada():
        for n, *_r in VISTAS:
            acciones.marcar(f"ver.pagina.{n}", n == espacio.vista)
        disponibilidad()

    def opciones_cambiadas():
        acciones.marcar("paq.forzar", catalogo.forzar)
        acciones.marcar("paq.detallado", catalogo.detallado)
        ajustes.detallado = catalogo.detallado
        disponibilidad()

    def barra_estado():
        espacio.fijarResumen(catalogo.resumen)
        espacio.fijarContexto(cambios.contexto)

    espacio.vistaCambiada.connect(vista_cambiada)
    catalogo.operacionCambiada.connect(opciones_cambiadas)
    catalogo.paginaCambiada.connect(disponibilidad)
    catalogo.cambiado.connect(barra_estado)
    catalogo.terminado.connect(lambda _o, _c: cambios.recargar())          # instalar o adoptar cambian el repo
    cambios.cambiado.connect(barra_estado)
    cambios.cambiado.connect(disponibilidad)
    cambios.filaCambiada.connect(disponibilidad)
    cambios.terminado.connect(lambda _c: catalogo.recargar())
    seguridad.cambiado.connect(disponibilidad)
    sistema.terminado.connect(lambda _n, _c: (catalogo.recargar(), cambios.recargar()))
    tareas.cambiada.connect(disponibilidad)
    vista_cambiada()
    barra_estado()

    piezas = dict(consola=consola, tareas=tareas, interfaz=interfaz, ajustes=ajustes, espacio=espacio, catalogo=catalogo,
                  cambios=cambios, seguridad=seguridad, guia=guia, sistema=sistema, acciones=acciones)
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
