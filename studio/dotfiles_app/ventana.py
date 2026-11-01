"""La ventana de Dotfiles Studio: el marco común de los studios (gui-comun) sobre `main.sh`.

Inicio (paquetes, enlaces, cambios y commits sin subir), Paquetes (una tarjeta por paquete: simular, instalar, adoptar,
eliminar), Cambios (el diff entero de cada archivo; confirmar por ruta tras el escáner; subir), Seguridad, Sistema
(fuentes, dependencias, respaldo) y Guía (docs/). Toda orden que cambia algo se simula o se confirma antes.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QInputDialog, QLabel, QListWidget, QListWidgetItem,
                               QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QSplitter, QStackedWidget,
                               QTextBrowser, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo, variante
from gui_comun.theming import aplicar_tema, disenador_de
from gui_comun.widgets.console_dock import ConsoleDock
from gui_comun.widgets.marco import montar_studio
from gui_comun.widgets.paleta import Comando
from gui_comun.widgets.tarjetas import Cifra, ListaConVacio, Tarjeta, encabezado, pagina_desplazable, rejilla_pareja
from gui_comun.workers.process_worker import ProcessWorker

from dotfiles_app import estado as est

APP_VERSION = "1.0.0"
ACENTO = "indigo"
LOGO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#888888" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/>'
        '<path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>')
ICONO_ESTADO = {"activo": "verificar", "parcial": "info", "conflicto": "quitar", "pendiente": "cargando",
                "ausente": "quitar", "sin config": "info"}
EXPLICA = {"activo": "enlazado al repo", "conflicto": "archivo real en HOME: adoptar lo devuelve al repo",
           "pendiente": "en el repo, sin enlace: instalar", "ausente": "ni en el repo ni en HOME"}


class Ajustes:
    def __init__(self) -> None:
        from PySide6.QtCore import QSettings
        self.q = QSettings()

    def theme(self) -> str:
        return str(self.q.value("ui/tema", "sistema"))

    def set_theme(self, tema: str) -> None:
        self.q.setValue("ui/tema", tema)


def _main_sh(*args: str) -> list[str]:
    return ["bash", str(est.repo() / "main.sh"), *args]


class TarjetaPaquete(Tarjeta):
    """Un paquete: el estado de cada archivo y sus órdenes (siempre por `main.sh`, con `-p paquete`)."""

    def __init__(self, ventana, paquete: est.Paquete):
        super().__init__()
        self.ventana, self.p = ventana, paquete
        cabeza = QHBoxLayout()
        icono = QLabel()
        icono.setPixmap(icono_trazo("paquete").pixmap(20, 20))
        cabeza.addWidget(icono)
        titulo = QLabel(paquete.nombre)
        titulo.setStyleSheet("font-weight: 600; font-size: 14px;")
        cabeza.addWidget(titulo, 1)
        self.etiqueta = clase(QLabel(), "tenue")
        cabeza.addWidget(self.etiqueta)
        self.cuerpo.addLayout(cabeza)
        self.detalle = clase(QLabel(), "suave")
        self.detalle.setWordWrap(True)
        self.detalle.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.cuerpo.addWidget(self.detalle)
        if paquete.nombre in est.SUSTITUYEN:
            n = clase(QLabel(f"{paquete.nombre} sustituye el enlace por un archivo real al guardar: «Adoptar» lo repone."),
                      "tenue")
            n.setWordWrap(True)
            self.cuerpo.addWidget(n)
        botones = QHBoxLayout()
        botones.addStretch(1)
        for texto, orden, aplicar in (("Simular", "instalar", False), ("Instalar", "instalar", True),
                                      ("Adoptar", "adoptar", True), ("Eliminar", "eliminar", True)):
            b = QPushButton(texto)
            if texto == "Instalar":
                variante(b, "primario")
            b.clicked.connect(lambda _=False, o=orden, a=aplicar: self.ventana.orden_paquete(self.p.nombre, o, a))
            botones.addWidget(b)
        self.cuerpo.addLayout(botones)
        self.pintar(paquete)

    def pintar(self, paquete: est.Paquete) -> None:
        self.p = paquete
        partes = [f"{paquete.cuenta(e)} {e}" for e in est.ESTADOS if paquete.cuenta(e)]
        self.etiqueta.setText(f"{paquete.estado} · " + " · ".join(partes))
        malos = [f"{a.rel} — {EXPLICA[a.estado]}" for a in paquete.archivos if a.estado != "activo"]
        self.detalle.setText("\n".join(malos) if malos else "\n".join(a.rel for a in paquete.archivos))


class Ventana:
    """Envoltorio de la QMainWindow con la forma que `gui_comun.widgets.marco.montar_studio` espera."""

    def __init__(self) -> None:
        app = QApplication.instance()
        self.settings = Ajustes()
        disenador = disenador_de(app) or aplicar_tema(app, self.settings.theme(), acento=ACENTO)
        self.paquetes = est.paquetes()
        self.ui = QMainWindow()
        self.ui.setWindowTitle(f"Dotfiles Studio {APP_VERSION}")
        central = QWidget()
        fila = QHBoxLayout(central)
        self.ui.sidebar = QListWidget()
        self.ui.stack = QStackedWidget()
        fila.addWidget(self.ui.sidebar)
        fila.addWidget(self.ui.stack, 1)
        self.ui.setCentralWidget(central)
        self.ui.statusbar = self.ui.statusBar()
        self.console = ConsoleDock(self.ui)
        self.ui.addDockWidget(Qt.BottomDockWidgetArea, self.console)
        self._workers: list = []

        self.controllers: dict[str, SimpleNamespace] = {}
        self._page_order: list[str] = []
        self._pagina("dashboard", "Inicio", "inicio", self._crear_inicio())
        self._pagina("paquetes", "Paquetes", "paquete", self._crear_paquetes())
        self._pagina("cambios", "Cambios", "subir", self._crear_cambios())
        self._pagina("seguridad", "Seguridad", "verificar", self._crear_seguridad())
        self._pagina("sistema", "Sistema", "sistema", self._crear_sistema())
        self._pagina("guia", "Guía", "documento", self._crear_guia())
        self.ui.sidebar.currentRowChanged.connect(self._al_cambiar)
        self.ui.sidebar.setCurrentRow(0)

        self.marco = montar_studio(self, nombre="Dotfiles Studio", subtitulo="La configuración de la máquina",
                                   logo_svg=LOGO, disenador=disenador, primarios={}, peligro=())
        for p in self.paquetes:
            self.marco.comandos_extra.append(Comando(f"Paquete {p.nombre}", lambda: self.navigate("paquetes"),
                                                     grupo="Paquetes", icono=icono_trazo("paquete")))
        self.refrescar()

    # ----------------------------------------------------------------------------------------------- páginas
    def _crear_inicio(self) -> QWidget:
        contenido = QWidget()
        raiz = QVBoxLayout(contenido)
        raiz.setSpacing(14)
        raiz.addWidget(encabezado("Inicio", "La configuración de esta máquina, enlazada archivo por archivo desde el "
                                            "repo. Nada se cambia sin simular o confirmar antes."))
        cifras = rejilla_pareja(4)
        self.c_paq = Cifra("Paquetes", "—", "")
        self.c_enl = Cifra("Enlaces", "—", "")
        self.c_cam = Cifra("Cambios", "—", "sin confirmar")
        self.c_sub = Cifra("Commits", "—", "sin subir")
        for i, c in enumerate((self.c_paq, self.c_enl, self.c_cam, self.c_sub)):
            cifras.addWidget(c, 0, i)
        raiz.addLayout(cifras)
        t = Tarjeta("Lo que pide atención")
        self.atencion = ListaConVacio("Todo enlazado y sin cambios: nada que hacer.")
        self.atencion.lista.itemDoubleClicked.connect(lambda it: self.navigate(it.data(Qt.UserRole)))
        t.cuerpo.addWidget(self.atencion, 1)
        t.setMinimumHeight(300)
        raiz.addWidget(t, 1)
        return pagina_desplazable(contenido)

    def _crear_paquetes(self) -> QWidget:
        contenido = QWidget()
        raiz = QVBoxLayout(contenido)
        raiz.setSpacing(12)
        raiz.addWidget(encabezado("Paquetes", "«Simular» muestra qué enlaces crearía; «Instalar» los crea (con "
                                              "respaldo); «Adoptar» lleva al repo lo que hay en HOME; «Eliminar» quita "
                                              "los enlaces sin tocar el repo."))
        rejilla = rejilla_pareja(2)
        self.tarjetas: dict[str, TarjetaPaquete] = {}
        for i, p in enumerate(self.paquetes):
            t = TarjetaPaquete(self, p)
            self.tarjetas[p.nombre] = t
            rejilla.addWidget(t, i // 2, i % 2)
        raiz.addLayout(rejilla)
        raiz.addStretch(1)
        return pagina_desplazable(contenido)

    def _crear_cambios(self) -> QWidget:
        w = QWidget()
        raiz = QVBoxLayout(w)
        raiz.addWidget(encabezado("Cambios", "Se lee el diff entero de cada archivo antes de confirmarlo; los híbridos "
                                             "cambian solos al usar su aplicación. Se confirma por ruta, tras el escáner "
                                             "de credenciales; nunca todo de una vez."))
        partir = QSplitter(Qt.Horizontal)
        self.lista_cam = ListaConVacio("Sin cambios: el repo está al día.")
        self.lista_cam.lista.currentItemChanged.connect(self._mostrar_diff)
        partir.addWidget(self.lista_cam)
        self.visor_diff = QPlainTextEdit()
        self.visor_diff.setReadOnly(True)
        self.visor_diff.setFont(QFont("monospace"))
        self.visor_diff.setLineWrapMode(QPlainTextEdit.NoWrap)
        partir.addWidget(self.visor_diff)
        partir.setSizes([300, 700])
        raiz.addWidget(partir, 1)
        botones = QHBoxLayout()
        self.lbl_rama = clase(QLabel(), "tenue")
        botones.addWidget(self.lbl_rama, 1)
        self.b_confirmar = variante(QPushButton(icono_trazo("verificar"), " Confirmar este archivo…"), "primario")
        self.b_confirmar.clicked.connect(self._confirmar)
        botones.addWidget(self.b_confirmar)
        self.b_subir = QPushButton(icono_trazo("subir"), " Subir")
        self.b_subir.clicked.connect(self._subir)
        botones.addWidget(self.b_subir)
        raiz.addLayout(botones)
        return w

    def _crear_seguridad(self) -> QWidget:
        contenido = QWidget()
        raiz = QVBoxLayout(contenido)
        raiz.setSpacing(12)
        raiz.addWidget(encabezado("Seguridad", "El repo es público: el escáner busca credenciales en lo versionado. No "
                                               "ve rutas ni nombres en una lista de recientes: eso se mira en el diff."))
        t = Tarjeta("Escáner de datos sensibles")
        fila = QHBoxLayout()
        fila.addStretch(1)
        b = variante(QPushButton(icono_trazo("verificar"), " Escanear"), "primario")
        b.clicked.connect(lambda: self.correr(_main_sh("seguridad"), "Escáner de datos sensibles"))
        fila.addWidget(b)
        t.cuerpo.addLayout(fila)
        raiz.addWidget(t)
        raiz.addStretch(1)
        return pagina_desplazable(contenido)

    def _crear_sistema(self) -> QWidget:
        contenido = QWidget()
        raiz = QVBoxLayout(contenido)
        raiz.setSpacing(12)
        raiz.addWidget(encabezado("Sistema", "Lo que no son enlaces: fuentes de usuario, dependencias de la distro y "
                                             "el respaldo de las configuraciones actuales."))
        rejilla = rejilla_pareja(2)
        for i, (titulo, texto, orden) in enumerate((
                ("Fuentes de usuario", "Instala en ~/.local/share/fonts las fuentes de USER_FONTS (sin sudo).",
                 "instalar-fuentes"),
                ("Dependencias", "Los paquetes de la distro que el repo necesita (y gui-comun, opcional).",
                 "instalar-deps"),
                ("Respaldo", "Copia las configuraciones actuales a .backups/ antes de un cambio grande.", "backup"))):
            t = Tarjeta(titulo)
            l = clase(QLabel(texto), "tenue")
            l.setWordWrap(True)
            t.cuerpo.addWidget(l)
            fila = QHBoxLayout()
            fila.addStretch(1)
            sim = QPushButton("Simular")
            sim.clicked.connect(lambda _=False, o=orden, n=titulo: self.correr(_main_sh(o, "--dry-run"), f"{n} (simulación)"))
            fila.addWidget(sim)
            ap = variante(QPushButton("Aplicar"), "primario")
            ap.clicked.connect(lambda _=False, o=orden, n=titulo: self._aplicar_sistema(o, n))
            fila.addWidget(ap)
            t.cuerpo.addLayout(fila)
            rejilla.addWidget(t, i // 2, i % 2)
        raiz.addLayout(rejilla)
        raiz.addStretch(1)
        return pagina_desplazable(contenido)

    def _crear_guia(self) -> QWidget:
        w = QWidget()
        raiz = QVBoxLayout(w)
        raiz.addWidget(encabezado("Guía", "El uso, los paquetes, la arquitectura, los atajos de KDE y las decisiones."))
        self.docs = QComboBox()
        for nombre, archivo in (("Uso", "README.md"), ("Paquetes", "docs/paquetes.md"),
                                ("Arquitectura", "docs/arquitectura.md"), ("Atajos de KDE", "docs/atajos-kde.md"),
                                ("Decisiones", "docs/decisiones.md")):
            self.docs.addItem(nombre, archivo)
        self.docs.currentIndexChanged.connect(self._mostrar_doc)
        raiz.addWidget(self.docs)
        self.lector = QTextBrowser()
        self.lector.setOpenExternalLinks(True)
        raiz.addWidget(self.lector, 1)
        self._mostrar_doc()
        return w

    # ----------------------------------------------------------------------------------------------------- API
    def show(self) -> None:
        self.ui.show()

    def navigate(self, page_id: str) -> None:
        if page_id in self._page_order:
            self.ui.sidebar.setCurrentRow(self._page_order.index(page_id))

    def correr(self, argv: list[str], nombre: str) -> ProcessWorker:
        worker = ProcessWorker(argv, cwd=str(est.repo()), description=nombre)
        self.console.attach_process_worker(worker, nombre)
        self.console.show()
        worker.finished_with_code.connect(lambda _c: self.refrescar())
        self._workers.append(worker)
        worker.start()
        return worker

    def run_function_worker(self, worker, nombre: str) -> None:   # lo pide el marco
        self.console.attach_function_worker(worker, nombre)
        self._workers.append(worker)
        worker.start()

    def orden_paquete(self, paquete: str, orden: str, aplicar: bool) -> None:
        if not aplicar:
            self.correr(_main_sh(orden, "-p", paquete, "--dry-run", "--verbose"), f"{orden} {paquete} (simulación)")
            return
        que = {"instalar": "crea los enlaces de", "adoptar": "lleva al repo los archivos reales de",
               "eliminar": "quita los enlaces de (el repo no cambia)"}[orden]
        if QMessageBox.question(self.ui, f"{orden.capitalize()} {paquete}",
                                f"«{orden}» {que} {paquete}. Antes se hace un respaldo en .backups/.\n\n¿Seguir?") \
                != QMessageBox.Yes:
            return
        extra = ["--force"] if orden == "eliminar" else []    # main.sh vuelve a preguntar por la terminal; aquí ya se preguntó
        self.correr(_main_sh(orden, "-p", paquete, *extra), f"{orden} {paquete}")

    def refrescar(self) -> None:
        try:
            self.paquetes = est.paquetes()
        except RuntimeError as e:
            self.marco.avisar("No se pudo leer config.sh", str(e), "error")
            return
        for p in self.paquetes:
            if p.nombre in self.tarjetas:
                self.tarjetas[p.nombre].pintar(p)
        archivos = [a for p in self.paquetes for a in p.archivos]
        activos = sum(a.estado == "activo" for a in archivos)
        self.c_paq.poner(str(len(self.paquetes)), f"{sum(p.estado == 'activo' for p in self.paquetes)} del todo enlazados")
        self.c_enl.poner(f"{activos}/{len(archivos)}", "enlazados al repo")
        g = est.estado_git()
        self.c_cam.poner(str(len(g.cambios)), "sin confirmar")
        self.c_sub.poner(str(g.adelante), "sin subir" + (f" · {g.atras} por bajar" if g.atras else ""))
        self.lbl_rama.setText(f"rama {g.rama} · {g.adelante} commit(s) sin subir")
        self.b_subir.setEnabled(g.adelante > 0)
        # lo que pide atención
        lista = self.atencion.lista
        lista.clear()
        for a in archivos:
            if a.estado != "activo":
                it = QListWidgetItem(icono_trazo(ICONO_ESTADO[a.estado]), f"{a.paquete}: {a.rel}\n{EXPLICA[a.estado]}")
                it.setData(Qt.UserRole, "paquetes")
                lista.addItem(it)
        for c in g.cambios:
            it = QListWidgetItem(icono_trazo("texto"), f"{c.ruta}\nsin confirmar" + (" · híbrido" if c.hibrido else ""))
            it.setData(Qt.UserRole, "cambios")
            lista.addItem(it)
        self.atencion.actualizar()
        # cambios
        actual = self.lista_cam.lista.currentItem().data(Qt.UserRole) if self.lista_cam.lista.currentItem() else None
        self.lista_cam.lista.clear()
        for c in g.cambios:
            it = QListWidgetItem(icono_trazo("info" if c.hibrido else "texto"),
                                 f"{c.ruta}\n{'nuevo' if c.nuevo else 'modificado'}" + (" · híbrido" if c.hibrido else ""))
            it.setData(Qt.UserRole, c.ruta)
            self.lista_cam.lista.addItem(it)
            if c.ruta == actual:
                self.lista_cam.lista.setCurrentItem(it)
        self.lista_cam.actualizar()
        self.b_confirmar.setEnabled(bool(g.cambios))

    # -------------------------------------------------------------------------------------------------- privado
    def _mostrar_diff(self, actual, _previo=None) -> None:
        self.visor_diff.setPlainText(est.diff(actual.data(Qt.UserRole)) if actual else "")

    def _confirmar(self) -> None:
        it = self.lista_cam.lista.currentItem()
        if it is None:
            self.marco.avisar("Elige un archivo", "Se confirma de uno en uno, con su diff a la vista.", "aviso")
            return
        ruta = it.data(Qt.UserRole)
        paquete = ruta.split("/", 1)[0]
        mensaje, ok = QInputDialog.getText(self.ui, "Confirmar " + ruta,
                                           "Mensaje del commit, en español (¿qué cambió y por qué?):",
                                           text=f"{paquete}: ")
        if not ok or not mensaje.strip() or mensaje.strip() == f"{paquete}:":
            return
        self.correr(est.orden_confirmar(ruta, mensaje.strip()), f"Confirmar {ruta}")

    def _subir(self) -> None:
        g = est.estado_git()
        if QMessageBox.question(self.ui, "Subir", f"¿Subir {g.adelante} commit(s) de {g.rama} a GitHub? El repo es "
                                "público.") == QMessageBox.Yes:
            self.correr(["git", "-C", str(est.repo()), "push"], "Subir a GitHub")

    def _aplicar_sistema(self, orden: str, nombre: str) -> None:
        if QMessageBox.question(self.ui, nombre, f"¿Aplicar «{nombre}»? (Simular primero muestra qué haría.)") \
                == QMessageBox.Yes:
            self.correr(_main_sh(orden), nombre)

    def _mostrar_doc(self) -> None:
        ruta = est.repo() / self.docs.currentData()
        texto = ruta.read_text(encoding="utf-8") if ruta.is_file() else f"No está {ruta.name}."
        if texto.startswith("---\n"):
            texto = texto.split("\n---\n", 1)[-1]
        self.lector.setMarkdown(texto)

    def _pagina(self, id_: str, nombre: str, icono: str, widget) -> None:
        self.controllers[id_] = SimpleNamespace(widget=widget)
        self._page_order.append(id_)
        self.ui.stack.addWidget(widget)
        self.ui.sidebar.addItem(QListWidgetItem(icono_trazo(icono), nombre))

    def _al_cambiar(self, fila: int) -> None:
        self.ui.stack.setCurrentIndex(fila)

    def _open_preferences(self) -> None:
        self.navigate("sistema")

    def _about(self) -> None:
        QMessageBox.about(self.ui, "Acerca de Dotfiles Studio",
                          f"<b>Dotfiles Studio</b> {APP_VERSION}<br><br>La configuración de la máquina, enlazada archivo "
                          "por archivo desde el repo. Cada botón corre <code>main.sh</code>; confirmar es por ruta y "
                          "tras el escáner de credenciales.")
