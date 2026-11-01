"""studio/tests/test_studio.py — Dotfiles Studio (2026-11-01): el estado de los paquetes, el de git, confirmar por
ruta y la ventana. Todo sobre un repo y un HOME falsos (conftest.py)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

STUDIO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDIO))

from dotfiles_app import estado as est  # noqa: E402


def test_el_mapa_sale_de_config_sh(falso):
    m = est.mapa()
    assert m["git"] == [".gitconfig"] and m["shell"] == [".zshrc", ".config/starship.toml"]
    assert list(m)[:2] == ["git", "shell"]          # el orden de STOW_PACKAGES


def test_estado_de_cada_archivo_como_main_sh(falso):
    por = {p.nombre: p for p in est.paquetes()}
    assert por["git"].estado == "activo"
    assert {a.rel: a.estado for a in por["shell"].archivos} == {".zshrc": "conflicto", ".config/starship.toml": "pendiente"}
    assert por["shell"].estado == "conflicto"
    assert por["kde"].estado == "ausente"
    salida = subprocess.run(["bash", "main.sh", "estado"], cwd=falso[0], capture_output=True, text=True, timeout=60).stdout
    assert "git" in salida and "activo" in salida      # la misma lectura que el gestor


def test_un_enlace_a_otra_parte_no_cuenta_como_activo(falso, tmp_path):
    repo, casa = falso
    ajeno = tmp_path / "ajeno.toml"
    ajeno.write_text("x\n", encoding="utf-8")
    (casa / ".config").mkdir()
    (casa / ".config" / "starship.toml").symlink_to(ajeno)
    assert est.estado_de("shell", ".config/starship.toml") == "conflicto"


def test_git_y_diff_entero(falso):
    repo, _ = falso
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    (repo / "kde").mkdir()
    (repo / "kde" / "kwinrc").write_text("[Effect]\n", encoding="utf-8")
    g = est.estado_git()
    rutas = {c.ruta: c for c in g.cambios}
    assert "git/.gitconfig" in rutas and rutas["git/.gitconfig"].codigo.strip() == "M"
    assert any(r.startswith("kde") for r in rutas)
    assert "-\tname = Prueba" in est.diff("git/.gitconfig") and "+\tname = Otra" in est.diff("git/.gitconfig")


def test_confirmar_lleva_solo_esa_ruta(falso):
    repo, _ = falso
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    (repo / "shell" / ".zshrc").write_text("export EDITOR=vim\n", encoding="utf-8")
    entorno = {**os.environ, "GIT_AUTHOR_NAME": "Prueba", "GIT_AUTHOR_EMAIL": "prueba@ejemplo.org",
               "GIT_COMMITTER_NAME": "Prueba", "GIT_COMMITTER_EMAIL": "prueba@ejemplo.org"}
    r = subprocess.run(est.orden_confirmar("git/.gitconfig", "git: otro nombre"), cwd=repo, capture_output=True,
                       text=True, timeout=120, env=entorno)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    g = est.estado_git()
    assert [c.ruta for c in g.cambios] == ["shell/.zshrc"]     # lo otro sigue sin confirmar
    ultimo = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%s"], capture_output=True, text=True).stdout
    assert ultimo.strip() == "git: otro nombre"


def test_la_ventana_sin_red_ni_enlaces_reales(falso):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    QApplication.setOrganizationName("dotfiles-studio-pruebas")
    QApplication.setApplicationName("dotfiles-studio-pruebas")
    app = QApplication.instance() or QApplication([])
    from dotfiles_app.ventana import Ventana
    v = Ventana()
    v.show()
    assert v.tarjetas["shell"].etiqueta.text().startswith("conflicto")
    assert v.c_enl.findChildren(object) is not None
    assert v.atencion.lista.count() >= 2           # el conflicto y lo pendiente de shell
    v.ui.close()
    app.processEvents()


def test_main_smoke(falso, tmp_path):
    entorno = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "XDG_CONFIG_HOME": str(tmp_path / "cfg")}
    r = subprocess.run([sys.executable, str(STUDIO / "main.py"), "--smoke"], env=entorno, capture_output=True,
                       text=True, timeout=90)
    assert r.returncode == 0, r.stderr[-2000:]
