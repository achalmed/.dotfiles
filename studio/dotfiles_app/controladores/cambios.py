"""dotfiles_app/controladores/cambios.py — la vista Cambios: la tabla de `git status` (`ModeloTabla` filtrado), el
diff entero del archivo elegido, confirmar ESE archivo (escáner → `git add -- ruta` → `git commit -- ruta`, nunca
`git add .`) y subir a GitHub; la rama y los commits adelante y atrás para la barra de estado. Las órdenes son las de
`estado.py` (`orden_confirmar`, `orden_push`) y corren en una tarea con su salida en el panel inferior.
"""

from __future__ import annotations

from gui_comun.modelos import ModeloFiltrado, ModeloTabla
from gui_comun.qt import QObject, Property, Signal, Slot

from dotfiles_app import estado as est
from dotfiles_app.modelos import cambios as mc
from dotfiles_app.servicios import comparar, diferencias, seguridad


class Cambios(QObject):
    cambiado = Signal()
    filaCambiada = Signal()
    terminado = Signal(int)
    aviso = Signal(str, str)

    def __init__(self, espacio, consola, tareas, parent=None):
        super().__init__(parent)
        self.espacio, self.consola, self.tareas = espacio, consola, tareas
        self._patrones = None
        self._estado = est.EstadoGit("—", 0, 0, ())
        self._filas: list[dict] = []
        self._fila = -1
        self._diff = ""
        self._modelo = ModeloTabla(mc.COLUMNAS, parent=self)
        self._filtrado = ModeloFiltrado(self._modelo, parent=self)
        self.recargar()

    modelo = Property(QObject, lambda self: self._filtrado, constant=True)      # el filtrado: QML pasa sus filas por filaOrigen
    tabla = Property(QObject, lambda self: self._modelo, constant=True)

    # ------------------------------------------------------------------ datos
    @Slot()
    def recargar(self) -> None:
        ruta_previa = self.ruta
        self._estado = est.estado_git()
        self._filas = mc.filas(self._estado)
        self._modelo.poner(self._filas)
        self._fila = next((i for i, f in enumerate(self._filas) if f["ruta"] == ruta_previa), -1)
        self._diff = est.diff(self.ruta) if self._fila >= 0 else ""
        self.cambiado.emit()
        self.filaCambiada.emit()

    @Property(str, notify=cambiado)
    def rama(self) -> str:
        return self._estado.rama

    @Property(int, notify=cambiado)
    def adelante(self) -> int:
        return self._estado.adelante

    @Property(int, notify=cambiado)
    def atras(self) -> int:
        return self._estado.atras

    @Property(int, notify=cambiado)
    def cuantos(self) -> int:
        return len(self._filas)

    @Property(int, notify=cambiado)
    def hibridos(self) -> int:
        return sum(f["hibrido"] for f in self._filas)

    @Property(bool, notify=cambiado)
    def hayCambios(self) -> bool:
        return bool(self._filas)

    @Property(bool, notify=cambiado)
    def hayParaSubir(self) -> bool:
        return self._estado.adelante > 0

    @Property(str, notify=cambiado)
    def contexto(self) -> str:
        return mc.contexto(self._estado)

    # ------------------------------------------------------------------ la fila elegida
    @Slot(int)
    def fijarFila(self, fila_visible: int) -> None:
        """La fila elegida en la vista (filtrada); aquí se guarda la del origen."""
        fila = self._filtrado.filaOrigen(fila_visible) if fila_visible >= 0 else -1
        if fila != self._fila:
            self._fila = fila
            self._diff = est.diff(self.ruta) if fila >= 0 else ""
            self.filaCambiada.emit()

    @Property(int, notify=filaCambiada)
    def filaActual(self) -> int:
        return self._fila

    @Property(str, notify=filaCambiada)
    def ruta(self) -> str:
        return self._filas[self._fila]["ruta"] if 0 <= self._fila < len(self._filas) else ""

    @Property(str, notify=filaCambiada)
    def rutaSeleccionada(self) -> str:
        return str(est.repo() / self.ruta) if self.ruta else ""

    @Property("QVariantMap", notify=filaCambiada)
    def datos(self) -> dict:
        return dict(self._filas[self._fila]) if 0 <= self._fila < len(self._filas) else {}

    @Property(str, notify=filaCambiada)
    def diferencia(self) -> str:
        """El diff ENTERO (o el contenido, si es nuevo): se lee antes de confirmar."""
        return self._diff

    @Property("QVariantMap", notify=filaCambiada)
    def comparacion(self) -> dict:
        """El diff del archivo elegido lado a lado (último commit ⟷ repo), con los secretos ocultos y la nota del
        híbrido o del filtro clean."""
        ruta = self.ruta
        if not ruta:
            return {}
        texto = self._diff
        if texto.startswith("(archivo nuevo)\n"):
            texto = "\n".join(comparar.difflib.unified_diff([], texto.split("\n", 1)[1].splitlines(), "/dev/null", ruta, lineterm=""))
        d = diferencias.analizar(texto if texto.startswith(("diff", "---")) else "")
        if self._patrones is None:
            try:
                self._patrones = seguridad.cargar(est.repo())
            except RuntimeError:
                self._patrones = []
        ocultas = comparar.enmascarar_filas(d, self._patrones)
        nombre = ruta.rsplit("/", 1)[-1]
        notas = []
        if nombre in comparar.APLICACION_HIBRIDO:
            notas.append(f"Híbrido: {comparar.APLICACION_HIBRIDO[nombre]} lo reescribe al usarse; lea la diferencia entera: "
                         "puede llevar estado (recientes, geometría) además de preferencias.")
        if nombre in comparar.FILTRADOS:
            notas.append(f"git lo compara tras su filtro clean ({comparar.FILTRADOS[nombre]}): lo que se ve es lo que se confirmaría.")
        if ocultas:
            notas.append(f"{ocultas} línea(s) con un posible secreto, oculto: no lo confirme (página Seguridad).")
        return {"ruta": ruta, "izquierda": "Último commit", "derecha": "Repositorio (lo que se confirmaría)", "filas": d["filas"],
                "trozos": len(d["trozos"]), "anadidas": d["anadidas"], "quitadas": d["quitadas"], "binario": d["binario"],
                "recortado": d["recortado"], "vacia": not d["filas"], "nuevo": self.datos.get("codigo") == "??",
                "hibrido": nombre in comparar.APLICACION_HIBRIDO, "notas": notas, "ocultas": ocultas}

    @Property(str, notify=filaCambiada)
    def mensajeSugerido(self) -> str:
        """El prefijo del mensaje del commit, por paquete («kate: »), como pide el repo."""
        d = self.datos
        return f"{d['paquete']}: " if d and d.get("paquete") and d["paquete"] != "(repo)" else ""

    # ------------------------------------------------------------------ confirmar y subir
    @Slot(str, result=str)
    def confirmar(self, mensaje: str) -> str:
        """Escáner de credenciales y, si sale limpio, `git add` y `git commit` SOLO de esa ruta. Devuelve el error si no
        se puede empezar (sin archivo, sin mensaje, tarea en curso); el resultado llega por `terminado`."""
        ruta = self.ruta
        if not ruta:
            return "Elige un archivo: se confirma de uno en uno, con su diff a la vista."
        mensaje = mensaje.strip()
        if not mensaje or mensaje == self.mensajeSugerido.strip():
            return "Escribe el mensaje del commit, en español: qué cambió y por qué."
        if self.tareas.activa:
            return "Hay una operación en curso; espera a que termine."
        self.tareas.proceso(f"Confirmar {ruta}", est.orden_confirmar(ruta, mensaje), cwd=str(est.repo()), al_terminar=self._fin)
        return ""

    @Slot()
    def subir(self) -> None:
        """`git push` de la rama actual (QML confirma antes: el repo es público)."""
        if self.tareas.activa:
            self.aviso.emit("Hay una operación en curso; espera a que termine.", "informacion")
            return
        self.tareas.proceso(f"Subir {self._estado.adelante} commit(s) de {self._estado.rama} a GitHub", est.orden_push(),
                            cwd=str(est.repo()), al_terminar=self._fin)

    def _fin(self, codigo: int) -> None:
        self.recargar()
        self.terminado.emit(codigo)
        if codigo != 0:
            self.aviso.emit(f"La operación terminó con código {codigo}: revisa la salida (F4).", "error")
