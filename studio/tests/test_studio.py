"""studio/tests/test_studio.py — Dotfiles Studio (QML + Kirigami sobre gui-comun 3.x) abre su ventana sin pantalla con el
Python del sistema sobre el repo y el HOME falsos:

- la ventana principal se carga y se cierra con `QT_QPA_PLATFORM=offscreen`, y `studio/main.py --smoke` sale con 0;
- las operaciones de docs/reingenieria.md §3 están registradas una vez, con su estado de operación y su confirmación,
  y los atajos no se repiten;
- cada componente QML del studio se instancia sin errores; ningún color propio; ninguna marca dentro; controles con
  nombre accesible; nada de QtWidgets ni de los widgets congelados; el lanzador y main.py con /usr/bin/python3;
- el repo no conoce ~/Documents: gui_comun se importa instalado o por GUI_COMUN_DIR, nunca subiendo carpetas.
"""
from __future__ import annotations

import json
import re
import subprocess

import pytest

from conftest import PYTHON_SISTEMA, REPO, STUDIO, correr_python, crear_falso, entorno_gui, requiere_sistema

QML = STUDIO / "dotfiles_app" / "qml"

ABRIR = """
import sys, json; sys.path.insert(0, sys.argv[1])
from dotfiles_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("dotfiles-studio", "Dotfiles Studio", version="prueba", nombre_ajustes="DotfilesStudio")
piezas = aplicacion.construir(app); app.exponer("descripcionStudio", "prueba")
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
ok = app.cargar(aplicacion.QML_DIR / "Main.qml")
raiz = app.motor.rootObjects()[0] if ok else None
titulo = raiz.property("title") if raiz else ""
a = piezas["acciones"]
portada = {"aplicar": a.accion("paq.aplicar").habilitada, "portada": a.accion("ver.portada").habilitada}
piezas["catalogo"].abrir("shell")                            # la página: Aplicar dice la operación y pide confirmación
pagina = {"aplicar": a.accion("paq.aplicar").textoPlano, "simular": a.accion("paq.simular").textoPlano,
          "habilitada": a.accion("paq.aplicar").habilitada, "indice": raiz.property("indice") if raiz else -1}
piezas["espacio"].fijarVista("cambios")
cambios = a.accion("paq.aplicar").textoPlano
operaciones = {n: [a.accion(n).operacion, a.accion(n).requiereConfirmacion] for n in a.nombres() if a.accion(n).operacion}
consecuencias = a.accion("paq.adoptar").consecuencias
QTimer.singleShot(600, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "titulo": titulo, "errores": errores, "acciones": a.nombres(), "menus": [m["titulo"] for m in a.menus],
                  "barra": a.barra, "portada": portada, "pagina": pagina, "cambios": cambios, "operaciones": operaciones,
                  "consecuencias": consecuencias, "tarjetas": len(piezas["catalogo"].tarjetas)}))
"""

COMPONENTE = """
import sys, json, os; sys.path.insert(0, sys.argv[1])
from dotfiles_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("dotfiles-studio", "Dotfiles Studio", version="prueba", nombre_ajustes="DotfilesStudio")
aplicacion.construir(app); app.exponer("descripcionStudio", "prueba")
app.motor.addImportPath(str(aplicacion.QML_DIR))
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
nombre, carpeta = sys.argv[2], sys.argv[3]
ruta = os.path.join(os.environ["XDG_CACHE_HOME"], "Prueba_" + nombre + ".qml")
os.makedirs(os.path.dirname(ruta), exist_ok=True)
open(ruta, "w").write('import QtQuick\\nimport GuiComun\\nimport "file://%s/%s"\\nVentanaBase { id: ventana; acciones: studio.acciones; tareas: studio.tareas; consola: studio.consola; visible: false; %s { id: objeto } }\\n' % (str(aplicacion.QML_DIR), carpeta, nombre))
ok = app.cargar(ruta)
QTimer.singleShot(400, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores}))
"""

GRAVES = ("TypeError", "ReferenceError", "is not a type", "Cannot assign", "is not defined", "Unable to assign")


def _graves(errores: list[str]) -> list[str]:
    """Los avisos del QML propio o del marco; los del estilo Breeze (qrc:/qt/qml/org/kde/breeze) son de KDE, no nuestros."""
    return [e for e in errores if any(g in e for g in GRAVES) and "org/kde/breeze" not in e]


@pytest.fixture
def falso_gui(tmp_path):
    repo, casa = crear_falso(tmp_path / "falso")
    return entorno_gui(tmp_path, repo, casa)


@requiere_sistema
def test_abre_y_cierra_su_ventana(falso_gui):
    r = correr_python(ABRIR, falso_gui)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    assert datos["titulo"] == "dotfiles — Dotfiles Studio"
    assert not _graves(datos["errores"]), "\n".join(_graves(datos["errores"]))
    # las operaciones de reingenieria.md §3, cada una registrada una sola vez
    for n in ("archivo.dolphin", "archivo.abrir", "archivo.terminal", "archivo.copiar", "editar.buscar",
              "ver.pagina.paquetes", "ver.pagina.cambios", "ver.pagina.seguridad", "ver.pagina.sistema", "ver.pagina.guia", "ver.portada",
              "ver.salida", "paq.simular", "paq.aplicar", "paq.instalar", "paq.adoptar", "paq.actualizar", "paq.eliminar", "paq.forzar",
              "paq.detallado", "paq.cancelar", "repo.releer", "repo.subir", "seg.escanear", "seg.main", "seg.copiar",
              "sistema.fuentes", "sistema.dependencias", "sistema.respaldo", "guia.abrir", "ayuda.manual",
              "ventana.paleta", "ventana.pantalla_completa", "app.ajustes", "app.acerca", "app.salir"):
        assert n in datos["acciones"], n
    assert "ventana.navegacion" not in datos["acciones"]          # VentanaBase: sin los paneles de VentanaStudio
    assert datos["menus"] == ["&Archivo", "&Editar", "&Ver", "&Paquete", "&Repositorio", "&Sistema", "A&justes", "Ay&uda"]
    assert datos["barra"] == ["repo.releer", "|", "paq.simular", "paq.aplicar", "|", "seg.escanear"]
    # estados de operación: lo que escribe en HOME o publica pide confirmación con sus consecuencias
    op = datos["operaciones"]
    assert op["paq.instalar"] == ["instalacion", True] and op["paq.actualizar"] == ["instalacion", True]
    assert op["paq.adoptar"] == ["escritura", True] and op["paq.eliminar"] == ["eliminacion", True]
    assert op["repo.subir"] == ["publicacion", True] and op["paq.simular"] == ["simulacion", False]
    assert op["seg.escanear"] == ["lectura", False] and op["sistema.dependencias"] == ["instalacion", True]
    assert "Adoptar shell" in datos["consecuencias"] and "Orden: ./main.sh adoptar -p shell" in datos["consecuencias"]
    assert datos["portada"] == {"aplicar": False, "portada": False}
    assert datos["pagina"]["aplicar"] == "Adoptar" and datos["pagina"]["simular"] == "Simular «adoptar»"
    assert datos["pagina"]["habilitada"] and datos["pagina"]["indice"] == 1
    assert datos["cambios"] == "Confirmar este archivo"
    assert datos["tarjetas"] >= 3                                  # los paquetes del config.sh real sobre el HOME falso


@requiere_sistema
def test_main_smoke(falso_gui, tmp_path):
    r = subprocess.run([PYTHON_SISTEMA, str(STUDIO / "main.py"), "--smoke"], env=falso_gui, capture_output=True, text=True, timeout=120, cwd=tmp_path)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    ruido = [l for l in r.stderr.splitlines() if any(g in l for g in GRAVES)]
    assert not ruido, "\n".join(ruido)


@requiere_sistema
def test_sin_gui_comun_lo_dice_y_sale_con_3(tmp_path, falso_gui):
    """Sin gui_comun (ni instalado ni por GUI_COMUN_DIR), main.py explica cómo instalarlo y sale con 3; main.sh no lo necesita."""
    guion = "import sys, runpy; sys.argv = [sys.argv[1], '--smoke']; runpy.run_path(sys.argv[1], run_name='__main__')"
    env = dict(falso_gui)
    env.pop("GUI_COMUN_DIR", None)
    env.pop("PYTHONUSERBASE", None)                                # con el HOME falso, el sitio de usuario de pip desaparece
    env["PYTHONPATH"] = str(tmp_path / "vacio")                   # y un paquete vacío tapa cualquier otro gui_comun
    (tmp_path / "vacio" / "gui_comun").mkdir(parents=True)
    r = subprocess.run([PYTHON_SISTEMA, "-c", "import gui_comun; print(getattr(gui_comun, '__version__', 'vacio'))"], env=env, capture_output=True, text=True)
    if r.stdout.strip() != "vacio":
        pytest.skip("no se pudo tapar gui_comun en este entorno")
    r = subprocess.run([PYTHON_SISTEMA, str(STUDIO / "main.py"), "--smoke"], env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 3 and "gui_comun" in r.stderr and "pip install" in r.stderr


COMPONENTES = sorted((p.parent.name, p.stem) for p in QML.glob("*/*.qml") if p.stem != "Resaltado")


@requiere_sistema
@pytest.mark.parametrize("carpeta,nombre", COMPONENTES, ids=[f"{c}/{n}" for c, n in COMPONENTES])
def test_cada_componente_qml(carpeta, nombre, falso_gui):
    r = correr_python(COMPONENTE, falso_gui, nombre, carpeta)
    assert r.returncode == 0, r.stderr[-3000:]
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    assert not _graves(datos["errores"]), "\n".join(_graves(datos["errores"]))


@requiere_sistema
def test_atajos_sin_repetir(falso_gui):
    """Cada atajo dispara una sola orden (un atajo repetido es ambiguo y Qt no ejecuta ninguna)."""
    guion = """
import sys, json; sys.path.insert(0, sys.argv[1])
from dotfiles_app import aplicacion
from gui_comun.nucleo import Aplicacion
app = Aplicacion("dotfiles-studio", "Dotfiles Studio", version="prueba", nombre_ajustes="DotfilesStudio")
p = aplicacion.construir(app)
a = p["acciones"]
print(json.dumps({n: a[n].atajo for n in a.nombres() if a[n].atajo}))
app.cerrar()
"""
    r = correr_python(guion, falso_gui)
    assert r.returncode == 0, r.stderr[-2000:]
    atajos = json.loads(r.stdout.strip().splitlines()[-1])
    repetidos = {s: [n for n, t in atajos.items() if t == s] for s in set(atajos.values()) if list(atajos.values()).count(s) > 1}
    assert not repetidos, repetidos


def test_sin_colores_propios_en_qml():
    malos = []
    for qml in QML.rglob("*.qml"):
        for n, linea in enumerate(qml.read_text(encoding="utf-8").splitlines(), 1):
            sin_comentario = linea.split("//")[0]
            if re.search(r'"#[0-9a-fA-F]{3,8}"', sin_comentario) or re.search(r'\bfont\.(pointSize|pixelSize|family)\s*:\s*["\d]', sin_comentario):
                malos.append(f"{qml.relative_to(STUDIO)}:{n}: {linea.strip()}")
    assert not malos, "\n".join(malos)


def test_sin_marca_dentro_de_la_ventana():
    """Ningún nombre ni logotipo del studio dentro de la ventana: el título lo pone KWin."""
    for qml in QML.rglob("*.qml"):
        codigo = "\n".join(l.split("//")[0] for l in qml.read_text(encoding="utf-8").splitlines())
        assert "logotipo" not in codigo.lower() and "logo_svg" not in codigo and "marca.svg" not in codigo, qml.name
        assert 'text: "Dotfiles Studio"' not in codigo, qml.name


def test_controles_sin_texto_con_nombre_accesible():
    """Cada ToolButton de solo icono y cada campo del QML propio declaran Accessible.name (o lo hereda de BotonAccion)."""
    malos = []
    for qml in QML.rglob("*.qml"):
        texto = qml.read_text(encoding="utf-8")
        for m in re.finditer(r"QQC2\.(ToolButton|TextField|TextArea|SpinBox|ComboBox) \{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", texto):
            cuerpo = m.group(2)
            if "Accessible.name" not in cuerpo and "Kirigami.FormData.label" not in cuerpo and "text:" not in cuerpo:
                malos.append(f"{qml.relative_to(STUDIO)}: {m.group(1)} sin Accessible.name: {cuerpo.strip()[:60]}")
    assert not malos, "\n".join(malos)


def test_sin_qtwidgets_ni_widgets_congelados_ni_documents():
    """La interfaz es QML: nada de QtWidgets ni de gui_comun.widgets (la QApplication la pone gui-comun 3.0); y no conoce
    ~/Documents ni sube carpetas."""
    malos = []
    for f in STUDIO.rglob("*.py"):
        for n, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if linea.lstrip().startswith(("import ", "from ")) and ("QtWidgets" in linea or "gui_comun.widgets" in linea or "gui_comun.diseno" in linea):
                malos.append(f"{f.relative_to(REPO)}:{n}: {linea.strip()}")
            if "Documents" in linea and "tests" not in f.parts:
                malos.append(f"{f.relative_to(REPO)}:{n}: menciona Documents")
            if re.search(r"parents\[[3-9]\]", linea):
                malos.append(f"{f.relative_to(REPO)}:{n}: {linea.strip()}")
    assert not malos, "\n".join(malos)


def test_lanzador_e_instalador_con_python_del_sistema():
    assert '"/usr/bin/python3"' in (STUDIO / "dotfiles_app" / "aplicacion.py").read_text(encoding="utf-8")
    assert (STUDIO / "main.py").read_text(encoding="utf-8").startswith("#!/usr/bin/python3")
    tools = (REPO / "lib" / "tools.sh").read_text(encoding="utf-8")
    assert "/usr/bin/python3" in tools and "PYTHON_STUDIO" in tools
    assert "@v1.3.0" not in tools                                  # la versión fija de gui-comun es la de dotfiles_app/__init__.py
