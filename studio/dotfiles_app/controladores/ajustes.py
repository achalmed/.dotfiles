"""dotfiles_app/controladores/ajustes.py — «Configurar Dotfiles Studio…»: las preferencias (QSettings) como propiedades
que la página de FormCard lee y escribe. `ui/tema` de 1.x deja de ofrecerse (el tema es del escritorio); quedan lo
que las operaciones necesitan: «Detallado» por omisión y la terminal para lo que pregunta por la consola."""

from __future__ import annotations

from gui_comun.qt import QObject, QSettings, Property, Signal, Slot


class Ajustes(QObject):
    cambiado = Signal()
    guardado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._s = QSettings()

    def _detallado_get(self) -> bool:
        v = self._s.value("operaciones/detallado", True)
        return v if isinstance(v, bool) else str(v).lower() in ("true", "1")

    def _detallado_set(self, v: bool) -> None:
        self._s.setValue("operaciones/detallado", bool(v))
        self.cambiado.emit()

    detallado = Property(bool, _detallado_get, _detallado_set, notify=cambiado)

    def _terminal_get(self) -> str:
        return str(self._s.value("sistema/terminal", "konsole") or "konsole")

    def _terminal_set(self, v: str) -> None:
        self._s.setValue("sistema/terminal", v.strip() or "konsole")
        self.cambiado.emit()

    terminal = Property(str, _terminal_get, _terminal_set, notify=cambiado)

    @Slot()
    def guardar(self) -> None:
        self._s.sync()
        self.cambiado.emit()
        self.guardado.emit()
