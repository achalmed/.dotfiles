"""studio/tests/test_estado.py — el servicio `estado.py` (sin Qt): el mapa de config.sh por Bash, el estado de cada
archivo como `main.sh estado`, git y el diff entero, confirmar por ruta, y las consultas nuevas de la fase QML
(destino del enlace, las órdenes de main.sh, cuándo hace falta una terminal, los documentos)."""
from __future__ import annotations

import os
import subprocess

import pytest

from conftest import ENTORNO_GIT

from dotfiles_app import estado as est


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
    assert est.destino_enlace(".config/starship.toml") == str(ajeno)
    assert est.destino_enlace(".gitconfig") == str(repo / "git" / ".gitconfig")
    assert est.destino_enlace(".zshrc") == ""           # un archivo real no es un enlace


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
    assert est.diff("kde/kwinrc").startswith("(archivo nuevo)")


def test_confirmar_lleva_solo_esa_ruta(falso):
    repo, _ = falso
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Otra\n", encoding="utf-8")
    (repo / "shell" / ".zshrc").write_text("export EDITOR=vim\n", encoding="utf-8")
    r = subprocess.run(est.orden_confirmar("git/.gitconfig", "git: otro nombre"), cwd=repo, capture_output=True,
                       text=True, timeout=120, env={**os.environ, **ENTORNO_GIT})
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    g = est.estado_git()
    assert [c.ruta for c in g.cambios] == ["shell/.zshrc"]     # lo otro sigue sin confirmar
    ultimo = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%s"], capture_output=True, text=True).stdout
    assert ultimo.strip() == "git: otro nombre"


def test_las_ordenes_de_main_sh(falso):
    assert est.orden_main("seguridad") == ["bash", "main.sh", "seguridad"]
    assert est.orden_paquetes("instalar", ["kate"], simular=True) == ["bash", "main.sh", "instalar", "-p", "kate", "--dry-run", "--verbose"]
    assert est.orden_paquetes("instalar", ["kate", "kde"], detallado=False) == ["bash", "main.sh", "instalar", "-p", "kate,kde"]
    assert est.orden_paquetes("instalar", ["kate"], detallado=False, forzar=True)[-1] == "--force"
    assert est.orden_paquetes("adoptar", ["kate"], detallado=False, forzar=True) == ["bash", "main.sh", "adoptar", "-p", "kate"]   # adoptar no fuerza
    assert est.orden_paquetes("eliminar", ["kate"], simular=True, detallado=False) == ["bash", "main.sh", "eliminar", "-p", "kate", "--dry-run", "--force"]
    try:
        est.orden_paquetes("borrar", ["kate"])
        assert False, "una operación desconocida debe fallar"
    except ValueError:
        pass
    por = {p.nombre: p for p in est.paquetes()}
    assert est.necesita_terminal("adoptar", [por["shell"]])            # .zshrc existe en los dos lados: main.sh pregunta
    assert not est.necesita_terminal("adoptar", [por["git"]])
    assert not est.necesita_terminal("instalar", [por["shell"]])
    assert est.orden_push()[:3] == ["git", "-C", str(falso[0])]


def _archivos(*raices):
    """{ruta: mtime} de los archivos y enlaces (no carpetas) bajo las raíces, sin .git ni .logs."""
    return {p: p.lstat().st_mtime_ns for r in raices for p in r.rglob("*")
            if ".git" not in p.parts and ".logs" not in p.parts and not (p.is_dir() and not p.is_symlink())}


def test_la_simulacion_de_main_sh_no_escribe(falso):
    """`main.sh instalar -p shell --dry-run` (lo que hace F5) deja los archivos del HOME y del repo como estaban."""
    repo, casa = falso
    antes = _archivos(casa, repo)
    r = subprocess.run(est.orden_paquetes("instalar", ["shell"], simular=True), cwd=repo, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    assert "dry-run" in r.stdout
    assert _archivos(casa, repo) == antes
    assert (casa / ".zshrc").is_file() and not (casa / ".zshrc").is_symlink()
    assert not (casa / ".config" / "starship.toml").exists()


def test_la_simulacion_tampoco_crea_carpetas(falso):
    """2026-11-02: `_create_symlink` mira DRY_RUN antes del `mkdir -p` de la carpeta padre (antes era xfail)."""
    repo, casa = falso
    carpetas = {p for p in casa.rglob("*") if p.is_dir()}
    subprocess.run(est.orden_paquetes("instalar", ["shell"], simular=True), cwd=repo, capture_output=True, text=True, timeout=60)
    assert {p for p in casa.rglob("*") if p.is_dir()} == carpetas


def test_adoptar_simulado_no_crea_carpetas_en_el_repo(falso):
    """2026-11-02: tampoco `adoptar --dry-run` (`_ensure_repo_dir` y la carpeta del paquete miran DRY_RUN)."""
    repo, casa = falso
    rel = est.mapa(repo)["kde"][0]
    (casa / rel).parent.mkdir(parents=True, exist_ok=True)
    (casa / rel).write_text("[General]\n", encoding="utf-8")         # solo en HOME: adoptar lo llevaría al repo
    antes = {p for p in repo.rglob("*")}
    r = subprocess.run(est.orden_paquetes("adoptar", ["kde"], simular=True), cwd=repo, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert {p for p in repo.rglob("*") if ".logs" not in p.parts and ".backups" not in p.parts} == {p for p in antes if ".logs" not in p.parts and ".backups" not in p.parts}
    assert not (casa / rel).is_symlink()


def test_los_documentos_de_la_guia(falso):
    docs = est.documentos()
    assert [d["texto"] for d in docs] == ["Uso", "Paquetes", "Arquitectura", "Atajos de KDE", "Decisiones"]
    assert docs[0]["ruta"] == "README.md" and docs[0]["existe"]
    meta, cuerpo = est.leer_documento("docs/paquetes.md")
    assert meta["tipo"] == "doc" and meta["estado"] == "activo" and meta["titulo"].startswith("Paquetes")
    assert cuerpo.startswith("# Paquetes") and "---" not in cuerpo[:3]
    assert est.leer_documento("docs/no-existe.md") == ({}, "No está docs/no-existe.md.")
