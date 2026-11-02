"""dotfiles_app/controladores/catalogo.py — la portada de paquetes y la página de cada uno, como en un gestor de paquetes.

La portada: una tarjeta por paquete (aplicación, estado, enlaces, híbridos, cambios sin confirmar y la acción que
pide), filtrada por categoría y por búsqueda. La página: el paquete abierto con sus archivos, la aplicación de la que
depende, las rutas que comparte con otro paquete, los huérfanos del repo y, sobre todo, **la operación elegida con su
plan por archivo (`servicios/plan.py`), la orden exacta y la comparación del archivo elegido (`servicios/comparar.py`)
antes de simular o aplicar**. Simular corre `main.sh … --dry-run` y guarda su salida para la pestaña Simulación;
aplicar lo hace de verdad (o abre una terminal si `main.sh` va a preguntar) y después comprueba que el estado nuevo es
el que el plan anunciaba.
"""

from __future__ import annotations

import re

from gui_comun.qt import QObject, Property, Signal, Slot

from dotfiles_app import estado as est
from dotfiles_app.servicios import comparar, seguridad
from dotfiles_app.servicios import plan as planes

# nombre, texto, icono
FILTROS = (("todos", "Todos los paquetes", "view-list-icons"), ("atencion", "Piden atención", "dialog-warning"),
           ("activos", "Enlazados", "emblem-symbolic-link"), ("cambios", "Con cambios sin confirmar", "vcs-locally-modified"))
# estado del paquete → (texto, nivel semántico, la operación que pide)
ESTADO = {"activo": ("Enlazado", "positivo", ""), "parcial": ("Parcial", "neutro", "instalar"),
          "conflicto": ("Archivo real en HOME", "negativo", "adoptar"), "pendiente": ("Sin enlazar", "neutro", "instalar"),
          "local": ("Solo en HOME", "neutro", "adoptar"), "ausente": ("Sin configuración aún", "", ""), "sin config": ("Sin archivos", "", "")}
NIVEL_ARCHIVO = {"activo": "positivo", "conflicto": "negativo", "pendiente": "neutro", "local": "neutro", "ausente": ""}
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class Catalogo(QObject):
    cambiado = Signal()               # se releyó el disco o cambió el filtro o la búsqueda
    paginaCambiada = Signal()         # otro paquete abierto (o ninguno)
    operacionCambiada = Signal()      # la operación, «Reemplazar» o el detalle
    archivoCambiado = Signal()        # otro archivo elegido en la página
    salidaCambiada = Signal()
    terminado = Signal(str, int)      # operación, código
    aviso = Signal(str, str)

    def __init__(self, espacio, consola, tareas, detallado: bool = True, parent=None):
        super().__init__(parent)
        self.espacio, self.consola, self.tareas = espacio, consola, tareas
        self._paquetes: list[est.Paquete] = []
        self._compartidas: dict[str, list[str]] = {}
        self._con_cambios: dict[str, int] = {}
        self._error = ""
        self._filtro = "todos"
        self._texto = ""
        self._abierto = ""
        self._archivo = ""
        self._operacion = "instalar"
        self._forzar = False
        self._detallado = detallado
        self._salida: list[str] = []
        self._salida_de = ""
        self._patrones = None
        self._comparacion: dict = {}
        self.recargar()

    # ------------------------------------------------------------------ datos
    @Slot()
    def recargar(self) -> None:
        """Relee config.sh, los enlaces de HOME y git (lo que hace `main.sh estado`) sin cerrar la página abierta."""
        try:
            self._paquetes = est.paquetes()
            self._compartidas = est.rutas_compartidas(est.mapa())
            self._error = ""
        except RuntimeError as e:
            self._paquetes, self._compartidas, self._error = [], {}, str(e)
            self.aviso.emit(f"No se pudo leer config.sh: {e}", "error")
        self._con_cambios = {}
        for c in est.estado_git().cambios:
            primero = c.ruta.split("/", 1)[0]
            self._con_cambios[primero] = self._con_cambios.get(primero, 0) + 1
        if self._abierto and not self.paquete(self._abierto):
            self._abierto = ""
        self._comparar()
        self.cambiado.emit()
        self.paginaCambiada.emit()
        self.operacionCambiada.emit()
        self.archivoCambiado.emit()

    def paquete(self, nombre: str) -> est.Paquete | None:
        return next((p for p in self._paquetes if p.nombre == nombre), None)

    def patrones(self):
        if self._patrones is None:
            try:
                self._patrones = seguridad.cargar(est.repo())
            except RuntimeError:
                self._patrones = []
        return self._patrones

    @Property(str, notify=cambiado)
    def error(self) -> str:
        return self._error

    def _atencion(self, p: est.Paquete) -> bool:
        return p.estado in ("parcial", "conflicto", "pendiente", "local")

    def _en(self, filtro: str, p: est.Paquete) -> bool:
        return {"todos": True, "atencion": self._atencion(p), "activos": p.estado == "activo",
                "cambios": p.nombre in self._con_cambios}[filtro]

    @Property("QVariantList", notify=cambiado)
    def filtros(self) -> list:
        return [{"nombre": n, "texto": t, "icono": i, "contador": sum(self._en(n, p) for p in self._paquetes)} for n, t, i in FILTROS]

    @Property(str, notify=cambiado)
    def filtro(self) -> str:
        return self._filtro

    @Slot(str)
    def fijarFiltro(self, nombre: str) -> None:
        if nombre in (f[0] for f in FILTROS) and nombre != self._filtro:
            self._filtro = nombre
            self.cambiado.emit()

    @Property(str, notify=cambiado)
    def texto(self) -> str:
        return self._texto

    @Slot(str)
    def buscar(self, texto: str) -> None:
        if texto != self._texto:
            self._texto = texto
            self.cambiado.emit()

    def _tarjeta(self, p: est.Paquete) -> dict:
        app = est.aplicacion(p.nombre)
        texto, nivel, pide = ESTADO.get(p.estado, (p.estado, "", ""))
        return {"nombre": p.nombre, "aplicacion": app["nombre"], "icono": app["icono"], "descripcion": app["descripcion"],
                "instalada": app["instalada"], "estado": p.estado, "textoEstado": texto, "nivel": nivel,
                "enlazados": p.cuenta("activo"), "total": len(p.archivos), "hibridos": sum(a.hibrido for a in p.archivos),
                "cambios": self._con_cambios.get(p.nombre, 0), "pide": pide,
                "textoPide": planes.TEXTO.get(pide, ""), "sustituye": p.nombre in est.SUSTITUYEN}

    @Property("QVariantList", notify=cambiado)
    def tarjetas(self) -> list:
        """Las tarjetas de la portada, con el filtro y la búsqueda (nombre, aplicación o ruta de un archivo)."""
        t = self._texto.strip().lower()
        salida = []
        for p in self._paquetes:
            if not self._en(self._filtro, p):
                continue
            tarjeta = self._tarjeta(p)
            if t and t not in p.nombre.lower() and t not in tarjeta["aplicacion"].lower() and not any(t in a.rel.lower() for a in p.archivos):
                continue
            salida.append(tarjeta)
        return salida

    @Property("QVariantMap", notify=cambiado)
    def cifras(self) -> dict:
        archivos = [a for p in self._paquetes for a in p.archivos]
        return {"paquetes": len(self._paquetes), "activos": sum(p.estado == "activo" for p in self._paquetes),
                "atencion": sum(self._atencion(p) for p in self._paquetes), "enlaces": sum(a.estado == "activo" for a in archivos),
                "archivos": len(archivos), "conCambios": len([p for p in self._paquetes if p.nombre in self._con_cambios])}

    @Property(str, notify=cambiado)
    def resumen(self) -> str:
        c = self.cifras
        texto = f"{c['activos']}/{c['paquetes']} paquetes enlazados · {c['enlaces']}/{c['archivos']} enlaces"
        return texto + (f" · {c['atencion']} piden atención" if c["atencion"] else "")

    # ------------------------------------------------------------------ la página de un paquete
    @Property(str, notify=paginaCambiada)
    def abierto(self) -> str:
        return self._abierto

    @Slot(str)
    def abrir(self, nombre: str) -> None:
        """Abre la página del paquete, con la operación que pide y su primer archivo que no está al día elegido."""
        p = self.paquete(nombre)
        if not p:
            return
        self._abierto = nombre
        # la operación que pide su estado; uno al día abre en «Instalar», cuyo plan dice que nada cambia
        self._operacion = ESTADO.get(p.estado, ("", "", ""))[2] or "instalar"
        self._forzar = False
        primero = next((a for a in p.archivos if a.estado != "activo"), p.archivos[0] if p.archivos else None)
        self._archivo = primero.rel if primero else ""
        if self._salida_de != nombre:
            self._salida, self._salida_de = [], ""
            self.salidaCambiada.emit()
        self._comparar()
        self.paginaCambiada.emit()
        self.operacionCambiada.emit()
        self.archivoCambiado.emit()

    @Slot()
    def cerrar(self) -> None:
        if self._abierto:
            self._abierto = ""
            self.paginaCambiada.emit()

    @Property("QVariantMap", notify=paginaCambiada)
    def pagina(self) -> dict:
        p = self.paquete(self._abierto)
        if not p:
            return {}
        t = self._tarjeta(p)
        dependencias = [{"nombre": t["aplicacion"], "detalle": f"«{est.aplicacion(p.nombre)['binario']}»",
                         "ok": t["instalada"], "texto": "instalada" if t["instalada"] else "no se encuentra: el paquete no tendrá quién lo lea"}]
        if p.nombre == "shell":                                # starship es opcional: el .zshrc aún no lo inicia
            hay = est.instalado("starship")
            dependencias.append({"nombre": "Starship (opcional)", "detalle": "«starship»", "ok": hay,
                                 "texto": "instalada" if hay else "no instalada: starship.toml queda inactivo"})
        compartidas = [{"ruta": r, "paquetes": [x for x in ps if x != p.nombre]} for r, ps in self._compartidas.items()
                       if p.nombre in ps]
        notas = []
        if t["sustituye"]:
            notas.append(f"{t['aplicacion']} guarda de forma atómica: sustituye el enlace por un archivo real. "
                         "Adoptar lo devuelve al repo.")
        if t["hibridos"]:
            notas.append("Tiene archivos híbridos (preferencias y estado juntos): la aplicación los reescribe al usarse "
                         "y aparecen en Cambios; lea su diferencia entera antes de confirmar.")
        if p.nombre == "systemd":
            notas.append("Tras instalar, la unidad se habilita con «systemctl --user enable audio-sesion-local.service».")
        archivos = [{"rel": a.rel, "estado": a.estado, "explicacion": est.EXPLICA.get(a.estado, ""), "hibrido": a.hibrido,
                     "nivel": NIVEL_ARCHIVO.get(a.estado, ""), "destino": self._corta(est.destino_enlace(a.rel)),
                     "carpeta": est.es_carpeta(p.nombre, a.rel)} for a in p.archivos]
        return {**t, "archivos": archivos, "dependencias": dependencias, "compartidas": compartidas,
                "huerfanos": est.huerfanos(p.nombre, [a.rel for a in p.archivos]), "notas": notas,
                "rutaRepo": str(est.repo() / p.nombre)}

    def _corta(self, ruta: str) -> str:
        """Una ruta para la pantalla: el repo como «repo/» y HOME como «~» (nada de rutas de la máquina en capturas)."""
        if not ruta:
            return ""
        repo, casa = str(est.repo()), str(est.home())
        return ruta.replace(repo + "/", "repo/").replace(casa, "~")

    # ------------------------------------------------------------------ la operación
    @Property(str, notify=operacionCambiada)
    def operacion(self) -> str:
        return self._operacion

    @Slot(str)
    def fijarOperacion(self, nombre: str) -> None:
        if nombre in planes.OPERACIONES and nombre != self._operacion:
            self._operacion = nombre
            self.operacionCambiada.emit()
            self.archivoCambiado.emit()          # la columna «qué pasa» de cada archivo cambia

    def _forzar_get(self) -> bool:
        return self._forzar

    def _forzar_set(self, v: bool) -> None:
        if bool(v) != self._forzar:
            self._forzar = bool(v)
            self.operacionCambiada.emit()

    forzar = Property(bool, _forzar_get, _forzar_set, notify=operacionCambiada)

    def _detallado_get(self) -> bool:
        return self._detallado

    def _detallado_set(self, v: bool) -> None:
        if bool(v) != self._detallado:
            self._detallado = bool(v)
            self.operacionCambiada.emit()

    detallado = Property(bool, _detallado_get, _detallado_set, notify=operacionCambiada)

    def plan_de(self, operacion: str) -> dict:
        p = self.paquete(self._abierto)
        if not p:
            return {}
        return planes.plan(operacion, p, forzar=self._forzar if operacion == "instalar" else False, compartidas=self._compartidas)

    @Property("QVariantMap", notify=operacionCambiada)
    def plan(self) -> dict:
        return self.plan_de(self._operacion)

    @Property("QVariantList", notify=operacionCambiada)
    def operaciones(self) -> list:
        """Las cuatro operaciones para el selector de la página: si pueden hacerse con este paquete y por qué no."""
        salida = []
        for n in planes.OPERACIONES:
            pl = self.plan_de(n)
            motivo = pl.get("bloqueo") or ("" if pl.get("hayQueHacer") or pl.get("terminal") else "Nada cambia con este paquete.")
            salida.append({"nombre": n, "texto": planes.TEXTO[n], "queHace": planes.QUE_HACE[n], "habilitada": bool(pl) and not motivo,
                           "motivo": motivo, "resumen": pl.get("resumen", "")})
        return salida

    def puede(self, operacion: str) -> bool:
        pl = self.plan_de(operacion)
        return bool(pl) and not pl["bloqueo"] and (pl["hayQueHacer"] or pl["terminal"])

    def consecuencias(self, operacion: str) -> str:
        pl = self.plan_de(operacion)
        if not pl:
            return "Abra un paquete."
        texto = pl["consecuencias"] + f"\n\nOrden: {self._texto_orden(operacion, False)}"
        return texto

    def orden(self, operacion: str, simular: bool) -> list[str]:
        return est.orden_paquetes(operacion, [self._abierto or "<paquete>"], simular=simular, detallado=self._detallado,
                                  forzar=self._forzar and operacion == "instalar")

    def _texto_orden(self, operacion: str, simular: bool) -> str:
        return "./" + " ".join(self.orden(operacion, simular)[1:])

    @Property(str, notify=operacionCambiada)
    def ordenSimular(self) -> str:
        return self._texto_orden(self._operacion, True)

    @Property(str, notify=operacionCambiada)
    def ordenAplicar(self) -> str:
        return self._texto_orden(self._operacion, False)

    # ------------------------------------------------------------------ el archivo elegido y su comparación
    @Property(str, notify=archivoCambiado)
    def archivo(self) -> str:
        return self._archivo

    @Slot(str)
    def fijarArchivo(self, rel: str) -> None:
        if rel != self._archivo:
            self._archivo = rel
            self._comparar()
            self.archivoCambiado.emit()

    def _comparar(self) -> None:
        p = self.paquete(self._abierto)
        a = next((x for x in p.archivos if x.rel == self._archivo), None) if p else None
        self._comparacion = comparar.comparar(p.nombre, a, patrones=self.patrones()) if a else {}

    @Property("QVariantMap", notify=archivoCambiado)
    def comparacion(self) -> dict:
        return self._comparacion

    @Property("QVariantMap", notify=archivoCambiado)
    def filaPlan(self) -> dict:
        """Lo que la operación elegida hará con el archivo elegido."""
        return next((f for f in self.plan.get("archivos", []) if f["rel"] == self._archivo), {})

    @Slot(str, result=str)
    def rutaEnHome(self, rel: str) -> str:
        return str(est.home() / rel) if rel else ""

    @Slot(str, result=str)
    def rutaEnRepo(self, rel: str) -> str:
        return str(est.repo() / self._abierto / rel) if rel and self._abierto else str(est.repo())

    # ------------------------------------------------------------------ simular y aplicar
    @Property("QVariantList", notify=salidaCambiada)
    def salida(self) -> list:
        return self._salida

    @Property(str, notify=salidaCambiada)
    def salidaDe(self) -> str:
        return self._salida_de

    def _anotar(self, texto: str, _es_err: bool = False) -> None:
        self._salida.append(self._corta(_ANSI.sub("", texto)).rstrip())
        self.salidaCambiada.emit()

    def _ocupado(self) -> bool:
        if not self._abierto:
            self.aviso.emit("Abra un paquete: la operación se elige en su página.", "informacion")
            return True
        if self.tareas.activa:
            self.aviso.emit("Hay una operación en curso; espere a que termine o cancélela.", "informacion")
            return True
        return False

    @Slot()
    def simular(self) -> None:
        """`main.sh <operación> -p <paquete> --dry-run`: no toca el disco; la salida, en la pestaña Simulación."""
        if self._ocupado():
            return
        op, nombre = self._operacion, self._abierto
        self._salida, self._salida_de = [], f"{planes.TEXTO[op]} {nombre} (simulación)"
        self.salidaCambiada.emit()
        w = self.tareas.proceso(f"Simular «{planes.TEXTO[op].lower()}» de {nombre}", self.orden(op, True), cwd=str(est.repo()),
                                operacion="simulacion", al_terminar=lambda c, o=op: self._fin(o, c, simulado=True))
        w.line.connect(self._anotar)

    @Slot(str)
    def aplicar(self, operacion: str = "") -> None:
        """La operación de verdad, ya confirmada (la confirmación la pide la acción `paq.<operación>`)."""
        op = operacion or self._operacion
        if self._ocupado() or op not in planes.OPERACIONES:
            return
        pl = self.plan_de(op)
        if pl["bloqueo"]:
            self.aviso.emit(pl["bloqueo"], "aviso")
            return
        nombre = self._abierto
        if pl["terminal"]:
            self.espacio.enTerminal(self.orden(op, False), f"{planes.TEXTO[op]} {nombre}")
            return
        esperado = {f["rel"] for f in pl["archivos"] if f["cambia"]}
        self._salida, self._salida_de = [], f"{planes.TEXTO[op]} {nombre}"
        self.salidaCambiada.emit()
        w = self.tareas.proceso(f"{planes.TEXTO[op]} {nombre}", self.orden(op, False), cwd=str(est.repo()),
                                operacion=pl["estadoOperacion"], al_terminar=lambda c, o=op: self._fin(o, c),
                                verificar=lambda _v, o=op, n=nombre, e=esperado: self._verificar(o, n, e),
                                error={"descripcion": f"main.sh no pudo {planes.TEXTO[op].lower()} {nombre}",
                                       "recurso": f"./main.sh {op} -p {nombre}",
                                       "accion": "Lea la salida en la pestaña Simulación de la página del paquete; "
                                                 "el respaldo de lo tocado está en .backups/."})
        w.line.connect(self._anotar)

    def _verificar(self, operacion: str, nombre: str, esperado: set[str]) -> tuple[bool, str]:
        """El éxito de `main.sh` no prueba el resultado: se relee el disco y se mira cada archivo que el plan cambiaba."""
        p = next((x for x in est.paquetes() if x.nombre == nombre), None)
        if p is None:
            return False, "el paquete ya no está en config.sh"
        estados = {a.rel: a.estado for a in p.archivos}
        if operacion == "eliminar":
            malos = [r for r in esperado if estados.get(r) == "activo"]
        else:
            malos = [r for r in esperado if estados.get(r) != "activo"]
        if malos:
            return False, f"{len(malos)} archivo(s) no quedaron como el plan decía: {', '.join(sorted(malos)[:3])}"
        return True, f"{len(esperado)} archivo(s) como el plan decía"

    def _fin(self, operacion: str, codigo: int, simulado: bool = False) -> None:
        self.recargar()
        self.terminado.emit(operacion, codigo)
        if simulado and codigo == 0:
            self.aviso.emit("Simulación terminada: nada cambió en el disco. La salida está en la pestaña Simulación.", "informacion")
