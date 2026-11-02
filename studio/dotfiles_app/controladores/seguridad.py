"""dotfiles_app/controladores/seguridad.py — la página Seguridad: el escáner de credenciales sobre lo que subiría un
`git add .`, con los patrones de `config.sh` (los mismos que `main.sh seguridad`). Cada hallazgo es archivo, línea,
tipo y huella; **el valor no llega a la interfaz, ni a la consola, ni al informe** (`servicios/seguridad.py`). El
escaneo es de lectura y corre en una tarea; también puede correrse el de `main.sh` tal cual, con su salida.
"""

from __future__ import annotations

from gui_comun.qt import QGuiApplication, QObject, Property, Signal, Slot

from dotfiles_app import estado as est
from dotfiles_app.servicios import seguridad as seg


class Seguridad(QObject):
    cambiado = Signal()
    terminado = Signal(int)            # hallazgos (−1 si falló)
    aviso = Signal(str, str)

    def __init__(self, consola, tareas, parent=None):
        super().__init__(parent)
        self.consola, self.tareas = consola, tareas
        self._hallazgos: list[dict] = []
        self._escaneado = False
        self._patrones: list[str] = []
        try:
            self._patrones = [n for n, _p in seg.cargar(est.repo())]
        except RuntimeError as e:
            self.consola.registrar("error", f"Escáner: {e}")

    @Property("QVariantList", constant=True)
    def tipos(self) -> list:
        """Lo que el escáner reconoce (los nombres de config.sh y la regla de los .env)."""
        return self._patrones + ["archivo .env versionado"]

    @Property("QVariantList", notify=cambiado)
    def hallazgos(self) -> list:
        return self._hallazgos

    @Property(int, notify=cambiado)
    def cuantos(self) -> int:
        return len(self._hallazgos)

    @Property(int, notify=cambiado)
    def archivos(self) -> int:
        return len({h["archivo"] for h in self._hallazgos})

    @Property(bool, notify=cambiado)
    def escaneado(self) -> bool:
        return self._escaneado

    @Property(str, constant=True)
    def orden(self) -> str:
        return "./main.sh seguridad"

    @Slot()
    def escanear(self) -> None:
        if self.tareas.activa:
            self.aviso.emit("Hay una operación en curso; espere a que termine.", "informacion")
            return
        raiz = est.repo()

        def trabajo(progress_cb=None, cancel_cb=None, message_cb=None):
            return seg.escanear(raiz, cancelado=cancel_cb)

        self.tareas.funcion("Escanear credenciales", trabajo, operacion="lectura", al_terminar=self._fin)

    def _fin(self, hallazgos) -> None:
        self._hallazgos = list(hallazgos or [])
        self._escaneado = True
        self.cambiado.emit()
        n = len(self._hallazgos)
        # al registro va el recuento y los sitios, nunca el valor
        self.consola.registrar("warn" if n else "info", f"Escáner: {n} posible(s) dato(s) sensible(s)"
                               + (": " + ", ".join(f"{h['archivo']}:{h['linea']} ({h['tipo']})" for h in self._hallazgos[:10]) if n else ""))
        self.terminado.emit(n)
        self.aviso.emit("Escáner: sin datos sensibles en lo que se subiría." if not n else
                        f"Escáner: {n} posible(s) dato(s) sensible(s) en {self.archivos} archivo(s). No confirme hasta revisarlos.",
                        "positivo" if not n else "aviso")

    @Slot()
    def escanearConMainSh(self) -> None:
        """El escáner de la terminal, con su salida en la consola (archivo, línea y tipo; tampoco imprime el valor)."""
        if self.tareas.activa:
            return
        self.tareas.proceso("main.sh seguridad", est.orden_main("seguridad"), cwd=str(est.repo()), operacion="lectura",
                            error=False, al_terminar=lambda c: self.aviso.emit(
                                "main.sh seguridad: sin hallazgos." if c == 0 else "main.sh seguridad encontró posibles datos sensibles (salida en la consola).",
                                "positivo" if c == 0 else "aviso"))

    @Slot()
    def copiarInforme(self) -> None:
        QGuiApplication.clipboard().setText(seg.informe(self._hallazgos))
        self.aviso.emit("Informe copiado (archivo, línea, tipo y huella; sin los valores).", "informacion")

    @Slot(str, result=str)
    def rutaDe(self, rel: str) -> str:
        return str(est.repo() / rel)
