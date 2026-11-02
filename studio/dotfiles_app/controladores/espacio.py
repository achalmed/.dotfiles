"""dotfiles_app/controladores/espacio.py — lo transversal de la ventana: la página activa (Paquetes · Cambios ·
Seguridad · Sistema · Guía), el repo y su nombre (el título de la ventana), el resumen y el contexto de la barra de
estado, las acciones sobre una ruta (mostrarla en Dolphin con `Escritorio`, terminal, portapapeles) y la terminal para
lo que `main.sh` pregunta por la consola (adoptar con conflictos, `sudo` de las dependencias).
"""

from __future__ import annotations

import os
import shutil
import subprocess

from gui_comun.qt import QGuiApplication, QObject, Property, Signal, Slot

from dotfiles_app import estado as est

# nombre, texto, icono
VISTAS = (("paquetes", "Paquetes", "package-x-generic"), ("cambios", "Cambios", "vcs-locally-modified"),
          ("seguridad", "Seguridad", "security-high"), ("sistema", "Sistema", "preferences-system"), ("guia", "Guía", "help-contents"))
NOMBRES = tuple(v[0] for v in VISTAS)


class Espacio(QObject):
    vistaCambiada = Signal()
    resumenCambiado = Signal()
    contextoCambiado = Signal()
    aviso = Signal(str, str)                 # texto, tipo (informacion · positivo · aviso · error)

    def __init__(self, consola, ajustes=None, escritorio=None, parent=None):
        super().__init__(parent)
        self.consola, self.ajustes, self.escritorio = consola, ajustes, escritorio
        self._vista = NOMBRES[0]
        self._resumen = ""
        self._contexto = ""

    # ------------------------------------------------------------------ el repo
    @Property(str, constant=True)
    def repo(self) -> str:
        return str(est.repo())

    @Property(str, constant=True)
    def nombreRepo(self) -> str:
        return est.repo().name

    # ------------------------------------------------------------------ la vista
    @Property("QVariantList", constant=True)
    def vistas(self) -> list:
        return [{"nombre": n, "texto": t, "icono": i} for n, t, i in VISTAS]

    @Property(str, notify=vistaCambiada)
    def vista(self) -> str:
        return self._vista

    @Property(int, notify=vistaCambiada)
    def indiceVista(self) -> int:
        return NOMBRES.index(self._vista)

    @Property(str, notify=vistaCambiada)
    def textoVista(self) -> str:
        return next(t for n, t, _i in VISTAS if n == self._vista)

    @Slot(str)
    def fijarVista(self, nombre: str) -> None:
        if nombre in NOMBRES and nombre != self._vista:
            self._vista = nombre
            self.vistaCambiada.emit()

    @Slot(int)
    def fijarVistaPorIndice(self, i: int) -> None:
        if 0 <= i < len(NOMBRES):
            self.fijarVista(NOMBRES[i])

    # ------------------------------------------------------------------ la barra de estado
    @Property(str, notify=resumenCambiado)
    def resumen(self) -> str:
        return self._resumen

    @Slot(str)
    def fijarResumen(self, texto: str) -> None:
        if texto != self._resumen:
            self._resumen = texto
            self.resumenCambiado.emit()

    @Property(str, notify=contextoCambiado)
    def contexto(self) -> str:
        return self._contexto

    @Slot(str)
    def fijarContexto(self, texto: str) -> None:
        if texto != self._contexto:
            self._contexto = texto
            self.contextoCambiado.emit()

    # ------------------------------------------------------------------ sobre una ruta (vacía: el repo)
    def _ruta(self, ruta: str) -> str:
        return ruta or str(est.repo())

    @Slot(str)
    def abrirDolphin(self, ruta: str) -> None:
        """Dolphin con el archivo señalado (`dolphin --select`); sin Dolphin, su carpeta con el gestor del escritorio."""
        ruta = self._ruta(ruta)
        if not os.path.exists(ruta) and not os.path.islink(ruta):
            ruta = os.path.dirname(ruta)
        if self.escritorio is not None:
            self.escritorio.mostrarEnDolphin(ruta)
        elif os.path.isdir(ruta if os.path.isdir(ruta) else os.path.dirname(ruta)):
            subprocess.Popen(["xdg-open", ruta if os.path.isdir(ruta) else os.path.dirname(ruta)])

    @Slot(str)
    def abrirConAplicacion(self, ruta: str) -> None:
        """El archivo con la aplicación que el escritorio asocia a su tipo (Kate para un .ini, por ejemplo)."""
        if ruta and self.escritorio is not None:
            self.escritorio.abrirConAplicacion(ruta)

    @Slot(str)
    def abrirTerminal(self, ruta: str) -> None:
        ruta = self._ruta(ruta)
        carpeta = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        if not os.path.isdir(carpeta):
            return
        terminal = self._terminal()
        if terminal == "konsole":
            subprocess.Popen(["konsole", "--workdir", carpeta])
        elif terminal:
            subprocess.Popen([terminal], cwd=carpeta)
        else:
            self.aviso.emit("No se encontró un emulador de terminal (konsole).", "aviso")

    @Slot(str)
    def copiarRuta(self, ruta: str) -> None:
        ruta = self._ruta(ruta)
        QGuiApplication.clipboard().setText(ruta)
        self.consola.registrar("info", f"Ruta copiada: {ruta}")

    # ------------------------------------------------------------------ una orden que necesita responder
    def _terminal(self) -> str:
        preferido = (self.ajustes.terminal if self.ajustes is not None else "konsole") or "konsole"
        for candidato in (preferido, "konsole", "x-terminal-emulator"):
            if shutil.which(candidato):
                return candidato
        return ""

    def enTerminal(self, argv: list[str], titulo: str = "") -> bool:
        """Corre `argv` en una terminal que queda abierta al terminar, con el repo como carpeta: lo que `main.sh`
        pregunta por /dev/tty o pide `sudo` no puede responderse desde la ventana. Devuelve si pudo abrirla."""
        terminal = self._terminal()
        if not terminal:
            self.aviso.emit("Esta operación pregunta por la terminal y no se encontró ninguna (konsole).", "error")
            return False
        if terminal == "konsole":
            orden = ["konsole", "--workdir", str(est.repo()), "--hold"] + (["-p", f"tabtitle={titulo}"] if titulo else []) + ["-e", *argv]
        else:
            orden = [terminal, "-e", *argv]
        subprocess.Popen(orden, cwd=str(est.repo()))
        self.consola.escribir("$ " + " ".join(argv) + "   (en una terminal)", "cmd")
        self.consola.registrar("info", f"Abierta en una terminal: {titulo or ' '.join(argv)}")
        return True
