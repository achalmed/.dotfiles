"""studio/tests/test_modelos_controladores.py — los modelos (funciones puras) y los controladores de Dotfiles Studio
sobre el repo y el HOME falsos: la portada y la página de un paquete (filtros, búsqueda, plan, comparación, la
simulación real de `main.sh --dry-run`, la aplicación real de instalar y quitar enlaces con su verificación), la tabla
de cambios con la diferencia lado a lado y la confirmación por ruta, el escáner, la guía, el sistema y los ajustes.
QSettings en temporal: nada toca al autor."""
from __future__ import annotations

import time

import pytest

from conftest import requiere_binding

from dotfiles_app import estado as est
from dotfiles_app.modelos import cambios as mc


# ----------------------------------------------------------------------------------------------- modelos (sin Qt)

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
    from dotfiles_app.controladores.catalogo import Catalogo
    from dotfiles_app.controladores.espacio import Espacio
    from dotfiles_app.controladores.guia import Guia
    from dotfiles_app.controladores.seguridad import Seguridad
    from dotfiles_app.controladores.sistema import Sistema
    consola = Consola()
    tareas = Tareas(consola)
    ajustes = Ajustes()
    espacio = Espacio(consola, ajustes)
    p = dict(repo=falso[0], casa=falso[1], consola=consola, tareas=tareas, ajustes=ajustes, espacio=espacio,
             catalogo=Catalogo(espacio, consola, tareas), cambios=Cambios(espacio, consola, tareas), guia=Guia(espacio),
             seguridad=Seguridad(consola, tareas), sistema=Sistema(espacio, consola, tareas))
    yield p
    tareas.esperar()


@requiere_binding
def test_espacio_paginas_y_barra(app, piezas):
    e = piezas["espacio"]
    assert e.repo == str(piezas["repo"]) and e.nombreRepo == "dotfiles"
    assert [v["nombre"] for v in e.vistas] == ["paquetes", "cambios", "seguridad", "sistema", "guia"]
    assert e.vista == "paquetes" and e.indiceVista == 0
    e.fijarVista("guia")
    assert e.vista == "guia" and e.indiceVista == 4 and e.textoVista == "Guía"
    e.fijarVista("otra")
    assert e.vista == "guia"
    e.fijarResumen("x"); e.fijarContexto("y")
    assert e.resumen == "x" and e.contexto == "y"


@requiere_binding
def test_catalogo_portada_filtros_y_busqueda(app, piezas):
    c = piezas["catalogo"]
    total = len(c.tarjetas)
    assert c.error == "" and total == c.cifras["paquetes"] and c.cifras["activos"] == 1
    por = {t["nombre"]: t for t in c.tarjetas}
    assert por["git"]["textoEstado"] == "Enlazado" and por["git"]["nivel"] == "positivo" and por["git"]["pide"] == ""
    assert por["shell"]["estado"] == "conflicto" and por["shell"]["pide"] == "adoptar" and por["shell"]["textoPide"] == "Adoptar"
    assert por["kate"]["aplicacion"] == "Kate" and por["kate"]["icono"] == "kate"
    assert [f["nombre"] for f in c.filtros] == ["todos", "atencion", "activos", "cambios"]
    c.fijarFiltro("activos")
    assert [t["nombre"] for t in c.tarjetas] == ["git"]
    c.fijarFiltro("atencion")
    assert "shell" in [t["nombre"] for t in c.tarjetas] and "git" not in [t["nombre"] for t in c.tarjetas]
    c.fijarFiltro("todos")
    c.buscar("star")                                         # una ruta de archivo también encuentra su paquete
    assert [t["nombre"] for t in c.tarjetas] == ["shell"]
    c.buscar("")
    (piezas["repo"] / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    c.recargar()
    c.fijarFiltro("cambios")
    assert [t["nombre"] for t in c.tarjetas] == ["git"] and c.tarjetas[0]["cambios"] == 1
    assert c.resumen.startswith(f"1/{total} paquetes enlazados")


@requiere_binding
def test_catalogo_pagina_plan_orden_y_comparacion(app, piezas):
    c = piezas["catalogo"]
    c.abrir("shell")
    assert c.abierto == "shell" and c.operacion == "adoptar" and c.archivo == ".zshrc"
    pg = c.pagina
    assert pg["aplicacion"] == "Zsh y Starship" and [a["rel"] for a in pg["archivos"]] == [".zshrc", ".config/starship.toml"]
    assert pg["dependencias"][0]["nombre"] == "Zsh y Starship" and pg["compartidas"] == [] and pg["huerfanos"] == []
    assert c.plan["terminal"] and c.ordenAplicar == "./main.sh adoptar -p shell --verbose"
    assert c.comparacion["izquierda"] == "Repositorio" and c.filaPlan["accion"] == "pregunta qué versión conservar"
    c.fijarOperacion("instalar")
    assert c.ordenSimular == "./main.sh instalar -p shell --dry-run --verbose" and c.plan["cambian"] == 1
    c.forzar = True
    assert c.ordenAplicar.endswith("--force") and c.filaPlan["accion"] == "reemplaza por el enlace"
    assert "1 archivo real reemplazado" in c.consecuencias("instalar") and "Orden: ./main.sh instalar -p shell" in c.consecuencias("instalar")
    ops = {o["nombre"]: o for o in c.operaciones}
    assert ops["instalar"]["habilitada"] and not ops["actualizar"]["habilitada"] and "sin respaldo" in ops["actualizar"]["motivo"]
    assert not ops["eliminar"]["habilitada"] and c.puede("instalar") and not c.puede("actualizar")
    c.fijarArchivo(".config/starship.toml")
    assert c.comparacion["derecha"] == "Repositorio" and c.comparacion["anadidas"] == 1
    c.cerrar()
    assert c.abierto == "" and c.pagina == {}


@requiere_binding
def test_catalogo_simular_no_escribe_y_aplicar_instala_y_verifica(app, piezas):
    c, tareas, casa = piezas["catalogo"], piezas["tareas"], piezas["casa"]
    verificadas, terminadas = [], []
    tareas.verificada.connect(lambda n, ok, d: verificadas.append((ok, d)))
    c.terminado.connect(lambda o, cod: terminadas.append((o, cod)))
    c.abrir("shell")
    c.fijarOperacion("instalar")
    c.simular()
    _esperar(app, tareas)
    assert terminadas == [("instalar", 0)] and not (casa / ".config").exists()
    assert any("starship.toml" in l for l in c.salida) and c.salidaDe.endswith("(simulación)")
    assert not any(str(casa) in l for l in c.salida)                  # rutas de la máquina, acortadas
    c.aplicar("instalar")
    _esperar(app, tareas)
    for _ in range(20):
        app.processEvents()
    assert terminadas[-1] == ("instalar", 0) and (casa / ".config" / "starship.toml").is_symlink()
    assert not (casa / ".zshrc").is_symlink()                          # sin «Reemplazar», el archivo real se salta
    assert verificadas and verificadas[-1][0] and "como el plan decía" in verificadas[-1][1]


@requiere_binding
def test_catalogo_quitar_enlaces_y_actualizar_bloqueado(app, piezas):
    c, tareas, casa = piezas["catalogo"], piezas["tareas"], piezas["casa"]
    avisos = []
    c.aviso.connect(lambda t, k: avisos.append((t, k)))
    c.abrir("shell")
    c.aplicar("actualizar")                                            # bloqueado: borraría .zshrc sin respaldo
    assert avisos and "sin respaldo" in avisos[-1][0] and not tareas.activa and not (casa / ".zshrc").is_symlink()
    c.abrir("git")
    assert c.operacion == "instalar" and c.plan_de("eliminar")["cambian"] == 1
    c.aplicar("eliminar")
    _esperar(app, tareas)
    assert not (casa / ".gitconfig").exists() and (piezas["repo"] / "git" / ".gitconfig").is_file()


@requiere_binding
def test_catalogo_sin_paquete_avisa(app, piezas):
    c = piezas["catalogo"]
    avisos = []
    c.aviso.connect(lambda t, k: avisos.append((t, k)))
    c.simular()
    assert avisos and "Abra un paquete" in avisos[0][0] and not piezas["tareas"].activa


@requiere_binding
def test_cambios_tabla_diferencia_y_confirmar(app, piezas):
    from gui_comun.qt import Qt
    repo, c, tareas = piezas["repo"], piezas["cambios"], piezas["tareas"]
    assert not c.hayCambios and c.rama == "main" and c.cuantos == 0 and c.contexto == "rama main · 0 cambios sin confirmar · 0 sin subir"
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    (repo / "shell" / ".zshrc").write_text("export EDITOR=vim\n", encoding="utf-8")
    c.recargar()
    assert c.hayCambios and c.cuantos == 2 and c.filaActual == -1 and c.diferencia == "" and c.comparacion == {}
    assert c.confirmar("x").startswith("Elige un archivo")
    c.modelo.ordenar(0, False)
    fila = next(i for i in range(c.modelo.rowCount()) if c.modelo.data(c.modelo.index(i, 0), Qt.ItemDataRole.DisplayRole) == "git/.gitconfig")
    c.fijarFila(fila)
    assert c.ruta == "git/.gitconfig" and "+\tname = Otra" in c.diferencia and c.mensajeSugerido == "git: "
    lados = [(f["izq"], f["der"]) for f in c.comparacion["filas"] if f["tipo"] == "cambio"]
    assert lados == [("\tname = Prueba", "\tname = Otra")] and c.comparacion["izquierda"] == "Último commit"
    assert c.datos["paquete"] == "git" and c.rutaSeleccionada == str(repo / "git" / ".gitconfig")
    assert c.confirmar("git: ").startswith("Escribe el mensaje")
    codigos = []
    c.terminado.connect(codigos.append)
    assert c.confirmar("git: otro nombre") == ""
    _esperar(app, tareas)
    assert codigos == [0] and c.cuantos == 1 and [f["ruta"] for f in c._filas] == ["shell/.zshrc"]
    assert c.adelante == 0 and not c.hayParaSubir               # sin remoto, git no cuenta commits adelante
    assert c.ruta == ""                                          # el confirmado ya no está


@requiere_binding
def test_cambios_ocultan_un_secreto_y_marcan_el_hibrido(app, piezas):
    repo, c = piezas["repo"], piezas["cambios"]
    # dentro de una carpeta seguida, git lo lista como archivo (una carpeta nueva entera saldría como «kde/»)
    (repo / "shell" / ".config" / "kdeglobals").write_text("[General]\napi_" + "key = " + "abcdefgh" * 3 + "\n", encoding="utf-8")
    c.recargar()
    fila = next(i for i, f in enumerate(c._filas) if f["ruta"].endswith("kdeglobals"))
    c.fijarFila(fila)
    comp = c.comparacion
    assert comp["hibrido"] and comp["ocultas"] == 1 and "abcdefgh" * 3 not in repr(comp["filas"])
    assert any("Híbrido" in n for n in comp["notas"])


@requiere_binding
def test_seguridad_escanea_sin_mostrar_el_valor(app, piezas):
    s, tareas, repo, consola = piezas["seguridad"], piezas["tareas"], piezas["repo"], piezas["consola"]
    assert "contraseña en una URL" in s.tipos and "archivo .env versionado" in s.tipos and s.orden == "./main.sh seguridad"
    s.escanear()
    _esperar(app, tareas)
    for _ in range(10):
        app.processEvents()
    assert s.escaneado and s.cuantos == 0
    clave = "super" + "secreta"                                 # armada al vuelo (ver test_servicios.py)
    (repo / "git" / ".gitconfig").write_text("[user]\n\tpass" + "word = " + clave + "\n", encoding="utf-8")
    s.escanear()
    _esperar(app, tareas)
    for _ in range(10):
        app.processEvents()
    assert s.cuantos == 1 and s.hallazgos[0]["archivo"] == "git/.gitconfig" and s.hallazgos[0]["linea"] == 2
    assert clave not in repr(s.hallazgos) and clave not in consola.registro.texto and clave not in consola.salida.texto


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
def test_sistema_simulaciones_y_dependencias(app, piezas):
    s, tareas, repo = piezas["sistema"], piezas["tareas"], piezas["repo"]
    info = s.info("dependencias")
    assert info["sudo"] and info["simulable"] and info["orden"] == "./main.sh instalar-deps" and info["operacion"] == "instalacion"
    assert s.info("respaldo")["operacion"] == "escritura"
    assert [d["nombre"] for d in s.dependencias][:2] == ["git", "zsh"] and "sudo" in s.consecuencias("dependencias")
    resultados = []
    s.terminado.connect(lambda n, c: resultados.append((n, c)))
    antes = sorted(x.name for x in repo.iterdir())
    s.correr("respaldo", True)
    _esperar(app, tareas)
    fuera = (".backups", ".logs")                                 # lo que main.sh deja siempre (ignorado por git)
    assert resultados[-1] == ("respaldo", 0) and [x for x in sorted(y.name for y in repo.iterdir()) if x not in fuera] == [a for a in antes if a not in fuera]
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
