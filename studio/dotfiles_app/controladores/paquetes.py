"""dotfiles_app/controladores/paquetes.py — la vista Paquetes: el árbol paquete › archivo (`ModeloArbol`) con su filtro
de estado y de texto, la selección (paquetes o archivos) y sus datos para el panel de detalles, la operación marcada
(instalar · adoptar · eliminar) con sus opciones, y su simulación (F5: `--dry-run`) o aplicación (Ctrl+Intro) por
`main.sh` en una tarea cuya salida va al panel inferior. Toda orden la construye `estado.orden_paquetes`.
"""

from __future__ import annotations

import os

from gui_comun.modelos import ModeloArbol
from gui_comun.qt import QObject, Property, Signal, Slot

from dotfiles_app import estado as est
from dotfiles_app.modelos import paquetes as mp

OPERACIONES = ("instalar", "adoptar", "eliminar")
DESCRIBE = {"instalar": "crea los enlaces de HOME hacia el repo (antes, respaldo en .backups/); un archivo real en HOME se salta, salvo con «Reemplazar»",
            "adoptar": "lleva al repo los archivos reales de HOME y deja el enlace (antes, respaldo); si el archivo existe en los dos lados, main.sh pregunta cuál conservar",
            "eliminar": "quita los enlaces de HOME; el repo no cambia"}


class Paquetes(QObject):
    cambiado = Signal()               # el árbol se releyó o se filtró
    seleccionCambiada = Signal()
    opcionesCambiadas = Signal()      # operación, detallado, forzar
    terminado = Signal(int)           # una operación de main.sh acabó (código)
    filaRepuesta = Signal(int)        # tras releer, la fila raíz del paquete que estaba seleccionado (la vista la vuelve a marcar)
    aviso = Signal(str, str)

    def __init__(self, espacio, consola, tareas, detallado: bool = True, parent=None):
        super().__init__(parent)
        self.espacio, self.consola, self.tareas = espacio, consola, tareas
        self._paquetes: list[est.Paquete] = []
        self._error = ""
        self._filtro = "todos"
        self._texto = ""
        self._operacion = "instalar"
        self._detallado = detallado
        self._forzar = False
        self._seleccion: list[dict] = []          # los nodos seleccionados (paquetes o archivos)
        self._actual: dict = {}                   # el nodo con el foco
        self._modelo = ModeloArbol(mp.COLUMNAS, parent=self)
        self.recargar()

    modelo = Property(QObject, lambda self: self._modelo, constant=True)

    # ------------------------------------------------------------------ datos
    @Slot()
    def recargar(self) -> None:
        """Relee config.sh y el disco (lo que hace `main.sh estado`) y repone el árbol con el filtro vigente."""
        try:
            self._paquetes = est.paquetes()
            self._error = ""
        except RuntimeError as e:
            self._paquetes, self._error = [], str(e)
            self.aviso.emit(f"No se pudo leer config.sh: {e}", "error")
        self._repintar()

    def _repintar(self) -> None:
        self._modelo.poner(mp.nodos(self._paquetes, self._filtro, self._texto))
        self._seleccion, self._actual = [], {}
        self.cambiado.emit()
        self._seleccion_cambio()

    def _seleccion_cambio(self) -> None:
        """La selección cambia lo que la operación hará: las órdenes y el texto de confirmación se recalculan."""
        self.seleccionCambiada.emit()
        self.opcionesCambiadas.emit()

    @Property(str, notify=cambiado)
    def error(self) -> str:
        return self._error

    @Property("QVariantMap", notify=cambiado)
    def contadores(self) -> dict:
        return mp.contadores(self._paquetes)

    @Property(str, notify=cambiado)
    def resumen(self) -> str:
        return mp.resumen(mp.contadores(self._paquetes))

    @Property("QVariantList", notify=cambiado)
    def filtros(self) -> list:
        """Las filas de la navegación: cada filtro con su contador."""
        c = mp.contadores(self._paquetes)
        return [{"nombre": f"filtro:{n}", "texto": t, "icono": i, "contador": c[n]} for n, t, i in mp.FILTROS]

    @Property(str, notify=cambiado)
    def filtro(self) -> str:
        return self._filtro

    @Slot(str)
    def fijarFiltro(self, nombre: str) -> None:
        nombre = nombre.removeprefix("filtro:")
        if nombre in (f[0] for f in mp.FILTROS) and nombre != self._filtro:
            self._filtro = nombre
            self._repintar()

    @Property(str, notify=cambiado)
    def texto(self) -> str:
        return self._texto

    @Slot(str)
    def fijarTexto(self, texto: str) -> None:
        if texto != self._texto:
            self._texto = texto
            self._repintar()

    @Slot(str, result=int)
    def filaDe(self, paquete: str) -> int:
        """La fila raíz de un paquete en el árbol (quita el filtro si lo esconde); −1 si no existe."""
        if paquete not in [p.nombre for p in self._paquetes]:
            return -1
        if not any(n["paquete"] == paquete for n in self._modelo.todas()):
            self._filtro, self._texto = "todos", ""
            self._repintar()
        return next((i for i, n in enumerate(self._modelo.todas()) if n["paquete"] == paquete), -1)

    def paquete(self, nombre: str) -> est.Paquete | None:
        return next((p for p in self._paquetes if p.nombre == nombre), None)

    # ------------------------------------------------------------------ selección
    @Slot("QVariantList")
    def seleccionar(self, indices: list) -> None:
        """Los índices seleccionados en el árbol (`ArbolDatos.indicesSeleccionados()`)."""
        self._seleccion = [d for d in (self._modelo.datos(i) for i in indices) if d]
        self._seleccion_cambio()

    @Slot("QVariant")
    def seleccionarActual(self, indice) -> None:
        """La fila con el foco (`ArbolDatos.indiceDe(fila)`): lo que muestra el panel de detalles."""
        self._actual = self._modelo.datos(indice) if indice is not None else {}
        if self._actual and not self._seleccion:
            self._seleccion = [self._actual]
        self._seleccion_cambio()

    @Property(bool, notify=seleccionCambiada)
    def haySeleccion(self) -> bool:
        return bool(self.paquetesSeleccionados)

    @Property("QVariantList", notify=seleccionCambiada)
    def paquetesSeleccionados(self) -> list:
        """Los paquetes sobre los que actúa la operación: los seleccionados y los de los archivos seleccionados, sin repetir."""
        vistos: list[str] = []
        for d in self._seleccion or ([self._actual] if self._actual else []):
            if d.get("paquete") and d["paquete"] not in vistos:
                vistos.append(d["paquete"])
        return vistos

    @Property(str, notify=seleccionCambiada)
    def rutaSeleccionada(self) -> str:
        """La ruta en el repo del archivo o paquete con el foco (para Dolphin, terminal y copiar); vacía si no hay."""
        d = self._actual
        if not d:
            return ""
        base = est.repo() / d["paquete"]
        return str(base / d["rel"]) if d.get("rel") else str(base)

    @Property("QVariantMap", notify=seleccionCambiada)
    def seleccion(self) -> dict:
        """Lo del elemento con el foco, para la pestaña Selección (vacío si no hay)."""
        d = self._actual
        if not d:
            return {}
        p = self.paquete(d["paquete"])
        if not p:
            return {}
        if d.get("rel"):
            a = next((x for x in p.archivos if x.rel == d["rel"]), None)
            if a is None:
                return {}
            destino = est.destino_enlace(a.rel)
            return {"tipo": "archivo", "paquete": p.nombre, "rel": a.rel, "estado": a.estado, "explicacion": est.EXPLICA.get(a.estado, ""),
                    "rutaHome": "~/" + a.rel, "rutaRepo": f"{p.nombre}/{a.rel}", "enRepo": (est.repo() / p.nombre / a.rel).exists(),
                    "destino": destino.replace(str(est.home()), "~") if destino else "", "hibrido": a.hibrido,
                    "sustituye": p.nombre in est.SUSTITUYEN}
        return {"tipo": "paquete", "paquete": p.nombre, "estado": p.estado, "detalle": mp.detalle_paquete(p), "total": len(p.archivos),
                "porEstado": [{"estado": e, "cuantos": p.cuenta(e)} for e in est.ESTADOS if p.cuenta(e)],
                "archivos": [{"rel": a.rel, "estado": a.estado, "explicacion": est.EXPLICA.get(a.estado, "")} for a in p.archivos],
                "sustituye": p.nombre in est.SUSTITUYEN, "rutaRepo": p.nombre}

    @Property(int, notify=seleccionCambiada)
    def conflictosSeleccion(self) -> int:
        return sum(a.estado == "conflicto" for n in self.paquetesSeleccionados for a in (self.paquete(n) or est.Paquete(n)).archivos)

    # ------------------------------------------------------------------ la operación y sus opciones
    @Property(str, notify=opcionesCambiadas)
    def operacion(self) -> str:
        return self._operacion

    @Slot(str)
    def fijarOperacion(self, nombre: str) -> None:
        if nombre in OPERACIONES and nombre != self._operacion:
            self._operacion = nombre
            self.opcionesCambiadas.emit()

    def _detallado_get(self) -> bool:
        return self._detallado

    def _detallado_set(self, v: bool) -> None:
        if bool(v) != self._detallado:
            self._detallado = bool(v)
            self.opcionesCambiadas.emit()

    detallado = Property(bool, _detallado_get, _detallado_set, notify=opcionesCambiadas)

    def _forzar_get(self) -> bool:
        return self._forzar

    def _forzar_set(self, v: bool) -> None:
        if bool(v) != self._forzar:
            self._forzar = bool(v)
            self.opcionesCambiadas.emit()

    forzar = Property(bool, _forzar_get, _forzar_set, notify=opcionesCambiadas)

    @Property(str, notify=opcionesCambiadas)
    def descripcionOperacion(self) -> str:
        return DESCRIBE[self._operacion]

    def orden(self, simular: bool) -> list[str]:
        return est.orden_paquetes(self._operacion, self.paquetesSeleccionados or ["<paquete>"], simular=simular,
                                  detallado=self._detallado, forzar=self._forzar)

    @Property(str, notify=opcionesCambiadas)
    def ordenSimular(self) -> str:
        return "./" + " ".join(self.orden(True)[1:])

    @Property(str, notify=opcionesCambiadas)
    def ordenAplicar(self) -> str:
        return "./" + " ".join(self.orden(False)[1:])

    @Property(bool, notify=opcionesCambiadas)
    def necesitaTerminal(self) -> bool:
        return est.necesita_terminal(self._operacion, [p for n in self.paquetesSeleccionados if (p := self.paquete(n))])

    @Property(str, notify=opcionesCambiadas)
    def textoConfirmacion(self) -> str:
        """Lo que el diálogo de Aplicar dice: paquetes, qué hace y el respaldo."""
        paqs = ", ".join(self.paquetesSeleccionados) or "(nada seleccionado)"
        texto = f"«{self._operacion}» {DESCRIBE[self._operacion]}.\n\nPaquetes: {paqs}."
        if self._operacion == "instalar" and self._forzar:
            texto += "\n\nCon «Reemplazar»: los archivos reales de HOME se sustituyen por el enlace (quedan en .backups/)."
        if self.necesitaTerminal:
            texto += f"\n\n{self.conflictosSeleccion} archivo(s) existen en HOME y en el repo: main.sh preguntará cuál conservar, así que se abre en una terminal."
        return texto

    # ------------------------------------------------------------------ simular y aplicar
    def _puede(self) -> bool:
        if not self.paquetesSeleccionados:
            self.aviso.emit("Selecciona un paquete (o un archivo suyo) en el árbol.", "informacion")
            return False
        if self.tareas.activa:
            self.aviso.emit("Hay una operación en curso; espera a que termine o cancélala.", "informacion")
            return False
        return True

    @Slot()
    def simular(self) -> None:
        """F5: `main.sh <operación> -p … --dry-run`; no toca el disco. La salida, íntegra, al panel inferior."""
        if not self._puede():
            return
        paqs = ", ".join(self.paquetesSeleccionados)
        self.tareas.proceso(f"Simular «{self._operacion}» de {paqs}", self.orden(True), cwd=str(est.repo()), al_terminar=self._fin)

    @Slot()
    def aplicar(self) -> None:
        """Ctrl+Intro, tras el diálogo de confirmación: la operación de verdad (con respaldo en .backups/)."""
        if not self._puede():
            return
        paqs = ", ".join(self.paquetesSeleccionados)
        if self.necesitaTerminal:
            self.espacio.enTerminal(self.orden(False), f"{self._operacion} {paqs}")
            return
        self.tareas.proceso(f"{self._operacion.capitalize()} {paqs}", self.orden(False), cwd=str(est.repo()), al_terminar=self._fin)

    def _fin(self, codigo: int) -> None:
        actual = dict(self._actual)
        self.recargar()
        if actual.get("paquete"):                                  # reencontrar lo que estaba seleccionado
            self._actual = next((n for n in self._modelo.todas() if n["paquete"] == actual["paquete"]), {})
            self._seleccion = [self._actual] if self._actual else []
            self._seleccion_cambio()
            if self._actual:
                self.filaRepuesta.emit(self.filaDe(actual["paquete"]))
        self.terminado.emit(codigo)
        if codigo != 0:
            self.aviso.emit(f"main.sh terminó con código {codigo}: revisa la salida (F4).", "error")

    @Slot(str, result=str)
    def rutaDe(self, paquete: str) -> str:
        return str(est.repo() / paquete) if os.path.isdir(est.repo() / paquete) else str(est.repo())
