"""El plan de cada operación, la comparación repo ⟷ HOME y el escáner de credenciales (sin Qt), sobre el repo y el HOME
falsos de `conftest.py`. Los secretos de prueba se arman al vuelo: escritos enteros en este archivo, el escáner del repo
los encontraría aquí."""
from __future__ import annotations

import subprocess

from dotfiles_app import estado as est
from dotfiles_app.servicios import comparar, plan, seguridad

# secretos falsos, partidos para que el código no case ningún patrón
TOKEN_GITHUB = "gh" + "p_" + "A1b2C3d4" * 5
CLAVE_AWS = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
URL_CON_CLAVE = "https://" + "usuario:" + "clavesecreta" + "@ejemplo.org/repo.git"


def _paquete(nombre):
    return next(p for p in est.paquetes() if p.nombre == nombre)


def test_el_estado_local_y_la_aplicacion(falso):
    repo, casa = falso
    rel = est.mapa(repo)["kde"][0]
    assert est.estado_de("kde", rel) == "ausente"
    (casa / rel).parent.mkdir(parents=True, exist_ok=True)
    (casa / rel).write_text("[General]\n", encoding="utf-8")
    assert est.estado_de("kde", rel) == "local"
    assert _paquete("kde").cuenta("local") == 1
    app = est.aplicacion("kate")
    assert app["nombre"] == "Kate" and app["icono"] == "kate" and isinstance(app["instalada"], bool)
    assert est.aplicacion("desconocido")["icono"] == "package-x-generic"


def test_rutas_compartidas_y_huerfanos(falso):
    repo, _casa = falso
    assert est.rutas_compartidas({"a": [".x", ".config/app"], "b": [".config/app/archivo"]}) == {".config/app/archivo": ["b", "a"]}
    assert est.rutas_compartidas(est.mapa(repo)) == {}
    (repo / "shell" / "viejo.conf").write_text("x\n", encoding="utf-8")
    assert est.huerfanos("shell", est.mapa(repo)["shell"], repo) == ["viejo.conf"]


def test_plan_de_instalar(falso):
    shell = _paquete("shell")                            # .zshrc conflicto, starship.toml pendiente
    p = plan.plan("instalar", shell)
    acciones = {f["rel"]: f["accion"] for f in p["archivos"]}
    assert acciones == {".zshrc": "se salta", ".config/starship.toml": "crea el enlace"}
    assert p["respaldo"] and not p["terminal"] and not p["bloqueo"] and p["cambian"] == 1
    assert p["estadoOperacion"] == "instalacion"
    f = plan.plan("instalar", shell, forzar=True)
    assert {x["rel"]: x["accion"] for x in f["archivos"]}[".zshrc"] == "reemplaza por el enlace"
    assert "1 archivo real reemplazado" in f["resumen"] and ".backups/" in f["consecuencias"]
    assert "adóptelo" in plan.plan("instalar", _paquete("kde"))["bloqueo"]


def test_plan_de_adoptar_actualizar_y_eliminar(falso):
    shell, git = _paquete("shell"), _paquete("git")
    a = plan.plan("adoptar", shell)
    assert a["terminal"] and {x["rel"]: x["accion"] for x in a["archivos"]}[".zshrc"] == "pregunta qué versión conservar"
    assert a["estadoOperacion"] == "escritura"
    u = plan.plan("actualizar", shell)
    assert "sin respaldo" in u["bloqueo"] and not u["hayQueHacer"]
    assert not plan.plan("actualizar", git)["bloqueo"]
    e = plan.plan("eliminar", git)
    assert e["cambian"] == 1 and e["estadoOperacion"] == "eliminacion" and "pierden" in e["consecuencias"]
    assert "no hay enlaces" in plan.plan("eliminar", shell)["bloqueo"]


def test_el_plan_coincide_con_la_simulacion_de_main_sh(falso):
    """Lo que el plan dice que pasa es lo que `main.sh --dry-run` anuncia (la ventana no inventa)."""
    repo, _casa = falso
    r = subprocess.run(est.orden_paquetes("instalar", ["shell"], simular=True), cwd=repo, capture_output=True, text=True, timeout=60)
    salida = r.stdout + r.stderr
    assert "starship.toml" in salida and "Saltado: .zshrc" in salida
    r = subprocess.run(est.orden_paquetes("instalar", ["shell"], simular=True, forzar=True), cwd=repo, capture_output=True, text=True, timeout=60)
    assert "instalado (repo): .zshrc" in r.stdout + r.stderr


def test_comparar_segun_el_estado(falso):
    repo, casa = falso
    shell = _paquete("shell")
    zshrc = next(a for a in shell.archivos if a.rel == ".zshrc")
    c = comparar.comparar("shell", zshrc)
    assert c["izquierda"] == "Repositorio" and c["derecha"].startswith("HOME")
    lados = [(f["izq"], f["der"]) for f in c["filas"] if f["tipo"] == "cambio"]
    assert lados == [("export EDITOR=kate", "# un archivo real")]
    starship = next(a for a in shell.archivos if a.rel == ".config/starship.toml")
    assert comparar.comparar("shell", starship)["anadidas"] == 1
    gitconfig = _paquete("git").archivos[0]
    assert "Sin cambios desde el último commit." in comparar.comparar("git", gitconfig)["notas"]
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    c = comparar.comparar("git", gitconfig)
    assert c["anadidas"] == 1 and c["quitadas"] == 1 and c["izquierda"] == "Último commit"


def test_comparar_oculta_los_secretos(falso):
    repo, casa = falso
    patrones = seguridad.cargar(repo)
    (casa / ".zshrc").write_text(f"export GITHUB_TOKEN={TOKEN_GITHUB}\n", encoding="utf-8")
    zshrc = next(a for a in _paquete("shell").archivos if a.rel == ".zshrc")
    c = comparar.comparar("shell", zshrc, patrones=patrones)
    texto = repr(c)
    assert TOKEN_GITHUB not in texto and "⟨oculto: token de GitHub⟩" in texto and c["ocultas"] == 1


def test_el_escaner_dice_donde_y_que_pero_no_el_valor(falso):
    repo, _casa = falso
    patrones = seguridad.cargar(repo)
    nombres = [n for n, _p in patrones]
    assert len(nombres) >= 16 and "contraseña en una URL" in nombres and "clave de acceso de AWS" in nombres
    (repo / "git" / ".gitconfig").write_text(f"[url]\n\tremoto = {URL_CON_CLAVE}\n[aws]\n\tclave = {CLAVE_AWS}\n", encoding="utf-8")
    (repo / "shell" / ".env").write_text("NADA=1\n", encoding="utf-8")
    (repo / "shell" / ".env.example").write_text("NADA=\n", encoding="utf-8")
    hallazgos = seguridad.escanear(repo, patrones)
    vistos = {(h["archivo"], h["linea"], h["tipo"]) for h in hallazgos}
    assert ("git/.gitconfig", 2, "contraseña en una URL") in vistos
    assert ("git/.gitconfig", 4, "clave de acceso de AWS") in vistos
    assert ("shell/.env", 0, "archivo .env versionado") in vistos
    assert not any(h["archivo"] == "shell/.env.example" for h in hallazgos)
    todo = repr(hallazgos) + seguridad.informe(hallazgos)
    for secreto in (CLAVE_AWS, "clavesecreta", URL_CON_CLAVE):
        assert secreto not in todo
    # la huella correlaciona: el mismo valor en dos sitios da la misma
    assert seguridad.huella(CLAVE_AWS) == seguridad.huella(CLAVE_AWS) != seguridad.huella(CLAVE_AWS + "X")


def test_main_sh_seguridad_informa_tipo_y_linea_sin_el_valor(falso):
    repo, _casa = falso
    (repo / "git" / ".gitconfig").write_text(f"[user]\n\tname = Prueba\n\ttoken = {TOKEN_GITHUB}\n", encoding="utf-8")
    (repo / "shell" / "produccion.env").write_text("NADA=1\n", encoding="utf-8")
    r = subprocess.run(est.orden_main("seguridad"), cwd=repo, capture_output=True, text=True, timeout=60)
    salida = r.stdout + r.stderr
    assert r.returncode != 0
    assert "Posible token de GitHub: git/.gitconfig:3" in salida
    assert "Posible archivo .env versionado: shell/produccion.env" in salida
    assert TOKEN_GITHUB not in salida
