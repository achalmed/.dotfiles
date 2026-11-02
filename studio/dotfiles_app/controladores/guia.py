"""dotfiles_app/controladores/guia.py — la vista Guía: los documentos del repo (`README.md`, `docs/*.md`) para leerlos
sin salir de la ventana: la lista para la navegación, el elegido, su cuerpo sin el frontmatter y sus metadatos."""

from __future__ import annotations

import subprocess

from gui_comun.qt import QObject, Property, Signal, Slot

from dotfiles_app import estado as est


class Guia(QObject):
    cambiado = Signal()

    def __init__(self, espacio, parent=None):
        super().__init__(parent)
        self.espacio = espacio
        self._actual = est.DOCUMENTOS[0][1]
        self._meta: dict = {}
        self._texto = ""
        self.recargar()

    @Property("QVariantList", constant=True)
    def documentos(self) -> list:
        """Las filas de la navegación: {nombre: "doc:<ruta>", texto, icono, ruta}."""
        return [{"nombre": f"doc:{d['ruta']}", "texto": d["texto"], "icono": "text-markdown" if d["existe"] else "emblem-question", "ruta": d["ruta"]}
                for d in est.documentos()]

    @Property(str, notify=cambiado)
    def actual(self) -> str:
        return self._actual

    @Property(str, notify=cambiado)
    def nombreActual(self) -> str:
        return f"doc:{self._actual}"

    @Slot(str)
    def fijarDocumento(self, ruta: str) -> None:
        ruta = ruta.removeprefix("doc:")
        if ruta in (r for _t, r in est.DOCUMENTOS) and ruta != self._actual:
            self._actual = ruta
            self.recargar()

    @Slot()
    def recargar(self) -> None:
        self._meta, self._texto = est.leer_documento(self._actual)
        self.cambiado.emit()

    @Property(str, notify=cambiado)
    def texto(self) -> str:
        return self._texto

    @Property(str, notify=cambiado)
    def titulo(self) -> str:
        return self._meta.get("titulo") or next((t for t, r in est.DOCUMENTOS if r == self._actual), self._actual)

    @Property(str, notify=cambiado)
    def tipo(self) -> str:
        return self._meta.get("tipo", "")

    @Property(str, notify=cambiado)
    def estadoDoc(self) -> str:
        return self._meta.get("estado", "")

    @Property(str, notify=cambiado)
    def rutaAbsoluta(self) -> str:
        return str(est.repo() / self._actual)

    @Slot()
    def abrir(self) -> None:
        """El documento con la aplicación del sistema (xdg-open)."""
        if (est.repo() / self._actual).is_file():
            subprocess.Popen(["xdg-open", self.rutaAbsoluta])
