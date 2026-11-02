"""studio/tests/test_modelos_controladores.py — los modelos (funciones puras) y los controladores de Dotfiles Studio
sobre el repo y el HOME falsos: el árbol de paquetes con sus filtros, la selección y la operación (la orden, la
simulación real de `main.sh --dry-run`, la aplicación real de instalar y eliminar), la tabla de cambios con el diff y
la confirmación por ruta, la guía, el sistema y los ajustes. QSettings en temporal: nada toca al autor."""
from __future__ import annotations

import time

import pytest

from conftest import requiere_binding

from dotfiles_app import estado as est
from dotfiles_app.modelos import cambios as mc
from dotfiles_app.modelos import paquetes as mp


# ----------------------------------------------------------------------------------------------- modelos (sin Qt)

def test_nodos_del_arbol_y_filtros(falso):
    paquetes = est.paquetes()
    raices = mp.nodos(paquetes)
    por = {n["paquete"]: n for n in raices}
    assert [n["paquete"] for n in raices][:2] == ["git", "shell"]
    assert por["git"]["valores"] == ["git", "activo", "1/1 enlazados"] and por["git"]["nivel"] == "positivo"
    assert por["git"]["icono"][1] == "vcs-normal" and por["git"]["rel"] is None
    assert por["shell"]["nivel"] == "negativo" and por["shell"]["valores"][1] == "conflicto"
    hijos = {h["rel"]: h for h in por["shell"]["hijos"]}
    assert hijos[".zshrc"]["estado"] == "conflicto" and "adoptar" in hijos[".zshrc"]["valores"][2]
    assert hijos[".config/starship.toml"]["nivel"] == "activo" and hijos[".config/starship.toml"]["icono"][1] == "vcs-update-required"
    assert por["kde"]["nivel"] == "inactivo" and por["kde"]["estado"] == "ausente"
    assert [n["paquete"] for n in mp.nodos(paquetes, "activos")] == ["git"]
    assert "git" not in [n["paquete"] for n in mp.nodos(paquetes, "atencion")] and "shell" in [n["paquete"] for n in mp.nodos(paquetes, "atencion")]
    # el texto casa con el nombre del paquete (todos sus archivos) o con un archivo (solo los que casan)
    assert [n["paquete"] for n in mp.nodos(paquetes, "todos", "star")] == ["shell"]
    assert [h["rel"] for h in mp.nodos(paquetes, "todos", "star")[0]["hijos"]] == [".config/starship.toml"]
    assert len(mp.nodos(paquetes, "todos", "shell")[0]["hijos"]) == 2
    c = mp.contadores(paquetes)
    assert c["todos"] == len(paquetes) and c["activos"] == 1 and c["atencion"] == len(paquetes) - 1
    assert c["enlaces"] == 1 and c["conflictos"] == 1 and c["pendientes"] == 1
    assert mp.resumen(c).startswith(f"{len(paquetes)} paquetes · 1 activos · ")


def test_filas_de_cambios(falso):
    repo, _ = falso
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    (repo / "shell" / ".config" / "kwinrc").write_text("[Effect]\n", encoding="utf-8")     # nuevo dentro de un paquete seguido
    (repo / "kde").mkdir()
    (repo / "kde" / "kdeglobals").write_text("[General]\n", encoding="utf-8")           # una carpeta nueva: git la muestra como «kde/»
    (repo / "docs" / "nuevo.md").write_text("x\n", encoding="utf-8")
    g = est.estado_git()
    filas = {f["ruta"]: f for f in mc.filas(g)}
    assert filas["git/.gitconfig"]["estado"] == "modificado" and filas["git/.gitconfig"]["paquete"] == "git" and filas["git/.gitconfig"]["nivel"] == "neutro"
    assert filas["shell/.config/kwinrc"]["estado"] == "nuevo" and filas["shell/.config/kwinrc"]["hibrido"] and "híbrido" in filas["shell/.config/kwinrc"]["nota"]
    assert filas["kde/"]["paquete"] == "kde" and filas["kde/"]["nivel"] == "positivo"
    assert filas["docs/nuevo.md"]["paquete"] == "(repo)"
    assert mc.contexto(g) == "rama main · 4 cambios sin confirmar · 0 sin subir"
    assert mc.tipo("D ")[0] == "eliminado" and mc.tipo("??")[0] == "nuevo" and mc.tipo("UU")[1] == "negativo"


# ---------------------------------------------------------------------------------------------- controladores

def _esperar(app, tareas, plazo=90.0):
    fin = time.time() + plazo
    while tareas.activa and time.time() < fin:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    assert not tareas.activa


@pytest.fixture
def piezas(app, falso, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    from gui_comun.qt import QSettings
    QSettings.setPath(QSettings.Format.NativeFormat, QSettings.Scope.UserScope, str(tmp_path / "config"))
    from gui_comun.consola import Consola
    from gui_comun.tareas import Tareas
    from dotfiles_app.controladores.ajustes import Ajustes
    from dotfiles_app.controladores.cambios import Cambios
    from dotfiles_app.controladores.espacio import Espacio
    from dotfiles_app.controladores.guia import Guia
    from dotfiles_app.controladores.paquetes import Paquetes
    from dotfiles_app.controladores.sistema import Sistema
    consola = Consola()
    tareas = Tareas(consola)
    ajustes = Ajustes()
    espacio = Espacio(consola, ajustes)
    p = dict(repo=falso[0], casa=falso[1], consola=consola, tareas=tareas, ajustes=ajustes, espacio=espacio,
             paquetes=Paquetes(espacio, consola, tareas), cambios=Cambios(espacio, consola, tareas), guia=Guia(espacio),
             sistema=Sistema(espacio, consola, tareas))
    yield p
    tareas.esperar()


@requiere_binding
def test_espacio_vistas_y_barra(app, piezas):
    e = piezas["espacio"]
    assert e.repo == str(piezas["repo"]) and e.nombreRepo == "dotfiles"
    assert [v["nombre"] for v in e.vistas] == ["paquetes", "cambios", "guia"]
    assert e.vista == "paquetes" and e.indiceVista == 0
    e.fijarVista("guia")
    assert e.vista == "guia" and e.indiceVista == 2 and e.textoVista == "Guía"
    e.fijarVistaPorIndice(1)
    assert e.vista == "cambios"
    e.fijarVista("otra")
    assert e.vista == "cambios"
    e.fijarResumen("x"); e.fijarContexto("y")
    assert e.resumen == "x" and e.contexto == "y"


@requiere_binding
def test_paquetes_arbol_filtros_y_seleccion(app, piezas):
    from gui_comun.qt import Qt
    p = piezas["paquetes"]
    m = p.modelo
    assert p.error == "" and m.filas == p.contadores["todos"] and p.contadores["activos"] == 1
    assert p.resumen.startswith(f"{m.filas} paquetes") and [f["nombre"] for f in p.filtros] == ["filtro:todos", "filtro:atencion", "filtro:activos"]
    assert p.filtros[1]["contador"] == m.filas - 1
    shell = m.index(1, 0)
    assert m.data(shell, Qt.ItemDataRole.DisplayRole) == "shell" and m.data(m.index(1, 1), Qt.ItemDataRole.DisplayRole) == "conflicto"
    assert m.rowCount(shell) == 2
    # seleccionar el paquete
    p.seleccionarActual(shell)
    assert p.haySeleccion and p.paquetesSeleccionados == ["shell"] and p.seleccion["tipo"] == "paquete"
    assert p.seleccion["porEstado"] == [{"estado": "conflicto", "cuantos": 1}, {"estado": "pendiente", "cuantos": 1}]
    assert p.rutaSeleccionada == str(piezas["repo"] / "shell") and p.conflictosSeleccion == 1
    # seleccionar un archivo: la operación actúa sobre su paquete
    zshrc = m.index(0, 0, shell)
    p.seleccionar([zshrc])
    p.seleccionarActual(zshrc)
    s = p.seleccion
    assert s["tipo"] == "archivo" and s["rel"] == ".zshrc" and s["estado"] == "conflicto" and s["rutaHome"] == "~/.zshrc"
    assert s["rutaRepo"] == "shell/.zshrc" and s["enRepo"] and s["destino"] == "" and not s["hibrido"]
    assert p.paquetesSeleccionados == ["shell"] and p.rutaSeleccionada == str(piezas["repo"] / "shell" / ".zshrc")
    # varios paquetes a la vez, sin repetir
    p.seleccionar([m.index(0, 0), shell, zshrc])
    assert p.paquetesSeleccionados == ["git", "shell"]
    # filtros y texto
    p.fijarFiltro("filtro:activos")
    assert p.filtro == "activos" and m.filas == 1 and not p.haySeleccion
    p.fijarTexto("star")
    assert m.filas == 0
    p.fijarFiltro("todos")
    assert m.filas == 1 and m.data(m.index(0, 0), Qt.ItemDataRole.DisplayRole) == "shell"
    p.fijarTexto("")
    assert p.filaDe("kde") >= 2 and p.filaDe("inexistente") == -1
    p.fijarFiltro("activos")
    assert p.filaDe("shell") == 1 and p.filtro == "todos"      # el filtro que lo escondía se quita


@requiere_binding
def test_paquetes_operacion_y_ordenes(app, piezas):
    p = piezas["paquetes"]
    p.seleccionarActual(p.modelo.index(1, 0))                    # shell
    assert p.operacion == "instalar" and p.detallado and not p.forzar
    assert p.ordenSimular == "./main.sh instalar -p shell --dry-run --verbose" and p.ordenAplicar == "./main.sh instalar -p shell --verbose"
    assert not p.necesitaTerminal and "Paquetes: shell" in p.textoConfirmacion
    p.forzar = True
    assert p.ordenAplicar.endswith("--force") and "Reemplazar" in p.textoConfirmacion
    p.fijarOperacion("adoptar")
    assert p.necesitaTerminal and "terminal" in p.textoConfirmacion and "--force" not in p.ordenAplicar
    p.fijarOperacion("eliminar")
    p.detallado = False
    assert p.ordenSimular == "./main.sh eliminar -p shell --dry-run --force"
    p.fijarOperacion("borrar")
    assert p.operacion == "eliminar"


@requiere_binding
def test_paquetes_simular_no_escribe_y_aplicar_instala(app, piezas):
    p, tareas, casa = piezas["paquetes"], piezas["tareas"], piezas["casa"]
    p.seleccionarActual(p.modelo.index(1, 0))                    # shell: .zshrc en conflicto, starship pendiente
    p.simular()
    _esperar(app, tareas)
    salida = piezas["consola"].salida.texto
    assert "$ bash main.sh instalar -p shell --dry-run --verbose" in salida and "dry-run" in salida
    assert not (casa / ".config" / "starship.toml").exists() and not (casa / ".zshrc").is_symlink()
    codigos = []
    p.terminado.connect(codigos.append)
    p.aplicar()                                                  # instalar sin --force: el pendiente se enlaza, el conflicto se salta
    _esperar(app, tareas)
    assert codigos == [0]
    assert (casa / ".config" / "starship.toml").is_symlink() and not (casa / ".zshrc").is_symlink()
    por = {n["paquete"]: n for n in p.modelo.todas()}
    assert por["shell"]["valores"][1] == "parcial"
    assert p.paquetesSeleccionados == ["shell"]                  # la selección se reencuentra tras releer
    p.fijarOperacion("eliminar")
    p.aplicar()
    _esperar(app, tareas)
    assert not (casa / ".config" / "starship.toml").exists() and codigos == [0, 0]
    assert any("Termina" in l for l, *_ in piezas["consola"].registro.ultimas(50))


@requiere_binding
def test_paquetes_sin_seleccion_avisa(app, piezas):
    p = piezas["paquetes"]
    avisos = []
    p.aviso.connect(lambda t, k: avisos.append((t, k)))
    p.simular()
    assert avisos and "Selecciona" in avisos[0][0] and not piezas["tareas"].activa


@requiere_binding
def test_cambios_tabla_diff_confirmar(app, piezas):
    from gui_comun.qt import Qt
    repo, c, tareas = piezas["repo"], piezas["cambios"], piezas["tareas"]
    assert not c.hayCambios and c.rama == "main" and c.cuantos == 0 and c.contexto == "rama main · 0 cambios sin confirmar · 0 sin subir"
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    (repo / "shell" / ".zshrc").write_text("export EDITOR=vim\n", encoding="utf-8")
    c.recargar()
    assert c.hayCambios and c.cuantos == 2 and c.filaActual == -1 and c.diferencia == ""
    assert c.confirmar("x").startswith("Elige un archivo")
    c.modelo.ordenar(0, False)
    fila = next(i for i in range(c.modelo.rowCount()) if c.modelo.data(c.modelo.index(i, 0), Qt.ItemDataRole.DisplayRole) == "git/.gitconfig")
    c.fijarFila(fila)
    assert c.ruta == "git/.gitconfig" and "+\tname = Otra" in c.diferencia and c.mensajeSugerido == "git: "
    assert c.datos["paquete"] == "git" and c.rutaSeleccionada == str(repo / "git" / ".gitconfig")
    assert c.confirmar("git: ").startswith("Escribe el mensaje")
    codigos = []
    c.terminado.connect(codigos.append)
    assert c.confirmar("git: otro nombre") == ""
    _esperar(app, tareas)
    assert codigos == [0] and c.cuantos == 1 and [f["ruta"] for f in c._filas] == ["shell/.zshrc"]
    assert c.adelante == 0 and not c.hayParaSubir               # sin remoto, git no cuenta commits adelante
    assert c.ruta == ""                                          # el confirmado ya no está
    assert "seguridad" in piezas["consola"].salida.texto.lower() or "Escaneando" in piezas["consola"].salida.texto


@requiere_binding
def test_guia_documentos(app, piezas):
    g = piezas["guia"]
    assert [d["texto"] for d in g.documentos] == ["Uso", "Paquetes", "Arquitectura", "Atajos de KDE", "Decisiones"]
    assert g.actual == "README.md" and g.nombreActual == "doc:README.md" and g.texto.startswith("# .dotfiles/")
    g.fijarDocumento("doc:docs/decisiones.md")
    assert g.actual == "docs/decisiones.md" and g.tipo == "decision" and g.estadoDoc == "activo" and g.texto.startswith("# Decisiones")
    assert g.rutaAbsoluta == str(piezas["repo"] / "docs" / "decisiones.md")
    g.fijarDocumento("otro.md")
    assert g.actual == "docs/decisiones.md"


@requiere_binding
def test_sistema_escaner_y_simulaciones(app, piezas):
    s, tareas, repo = piezas["sistema"], piezas["tareas"], piezas["repo"]
    info = s.info("dependencias")
    assert info["sudo"] and info["simulable"] and info["orden"] == "./main.sh instalar-deps"
    assert not s.info("seguridad")["simulable"]
    resultados, avisos = [], []
    s.terminado.connect(lambda n, c: resultados.append((n, c)))
    s.aviso.connect(lambda t, k: avisos.append(k))
    s.seguridad()
    _esperar(app, tareas)
    assert resultados == [("seguridad", 0)] and avisos == ["positivo"]
    (repo / "git" / ".gitconfig").write_text("[user]\n\tpassword = supersecreta\n", encoding="utf-8")
    s.seguridad()
    _esperar(app, tareas)
    assert resultados[-1][0] == "seguridad" and resultados[-1][1] != 0 and avisos[-1] == "aviso"
    antes = sorted(x.name for x in repo.iterdir())
    s.correr("respaldo", True)
    _esperar(app, tareas)
    assert resultados[-1] == ("respaldo", 0) and sorted(x.name for x in repo.iterdir() if x.name != ".backups") == [a for a in antes if a != ".backups"]
    assert not list((repo / ".backups").glob("*.tar*")) if (repo / ".backups").is_dir() else True


@requiere_binding
def test_ajustes_en_qsettings_temporal(app, piezas):
    a = piezas["ajustes"]
    assert a.detallado is True and a.terminal == "konsole"
    a.detallado = False
    a.terminal = "  "
    a.guardar()
    assert a.detallado is False and a.terminal == "konsole"
    assert str(piezas["repo"].parent) not in a._s.fileName() or "config" in a._s.fileName()
