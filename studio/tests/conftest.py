"""studio/tests/conftest.py — un repo y un HOME FALSOS para cada prueba: nunca se tocan los enlaces reales.

El temporal va al disco (XDG_CACHE_HOME), no a /tmp (tmpfs: es RAM).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BASETEMP = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "pytest" / "dotfiles-studio" / "basetemp"


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.basetemp:
        return
    args = [Path(a.split("::")[0]).resolve() for a in (config.args or [])]
    if args and all(REPO in a.parents or a == REPO for a in args):
        BASETEMP.parent.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(BASETEMP)


def _git(raiz: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(raiz), *args], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "Prueba", "GIT_AUTHOR_EMAIL": "prueba@ejemplo.org",
                        "GIT_COMMITTER_NAME": "Prueba", "GIT_COMMITTER_EMAIL": "prueba@ejemplo.org"})


@pytest.fixture
def falso(tmp_path, monkeypatch):
    """Repo con el gestor real (main.sh, config.sh, lib/) y dos paquetes: git enlazado y shell con un conflicto."""
    repo, casa = tmp_path / "dotfiles", tmp_path / "casa"
    repo.mkdir()
    casa.mkdir()
    for n in ("main.sh", "config.sh", ".gitignore"):   # .gitignore: .logs/ y .backups/ los ignora el real
        shutil.copy2(REPO / n, repo / n)
    shutil.copytree(REPO / "lib", repo / "lib")
    (repo / "git").mkdir()
    (repo / "git" / ".gitconfig").write_text("[user]\n\tname = Prueba\n", encoding="utf-8")
    (repo / "shell" / ".config").mkdir(parents=True)
    (repo / "shell" / ".zshrc").write_text("export EDITOR=kate\n", encoding="utf-8")
    (repo / "shell" / ".config" / "starship.toml").write_text("add_newline = false\n", encoding="utf-8")
    (casa / ".gitconfig").symlink_to(repo / "git" / ".gitconfig")      # activo
    (casa / ".zshrc").write_text("# un archivo real\n", encoding="utf-8")  # conflicto
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "inicio")
    monkeypatch.setenv("DOTFILES_DIR", str(repo))
    monkeypatch.setenv("HOME", str(casa))
    return repo, casa
