"""studio/tests/conftest.py — un repo y un HOME FALSOS para cada prueba: nunca se tocan los enlaces reales.

Dos clases de prueba:
- en proceso (servicio, modelos, controladores): con el binding del Python que corre pytest (basta QtCore) y
  `QT_QPA_PLATFORM=offscreen`; `DOTFILES_DIR` y `HOME` apuntan al repo y la casa falsos (`falso`);
- en un proceso hijo (cada componente QML, `main.py --smoke`): con el Python del sistema (`/usr/bin/python3`), el
  único cuyo Qt trae Kirigami, y un `XDG_CONFIG_HOME` temporal: QSettings y la caché no tocan la configuración del autor.

El temporal va al disco (`run.sh` fija `--basetemp` en ~/.cache; aquí también, por si se llama a pytest a mano).
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

STUDIO = Path(__file__).resolve().parents[1]
REPO = STUDIO.parent
CASA_REAL = Path.home()          # antes de que una prueba cambie HOME: el sitio de usuario de pip cuelga de ella
BASETEMP = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "pytest" / "dotfiles-studio" / "basetemp"

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))

import dotfiles_app  # noqa: E402,F401  (localiza gui_comun: instalado o GUI_COMUN_DIR)

HAY_BINDING = importlib.util.find_spec("PySide6") is not None or importlib.util.find_spec("PyQt6") is not None
HAY_GUI_COMUN = importlib.util.find_spec("gui_comun") is not None
requiere_binding = pytest.mark.skipif(not (HAY_BINDING and HAY_GUI_COMUN), reason="sin PySide6/PyQt6 o sin gui_comun")


def _python_del_sistema() -> str | None:
    candidato = "/usr/bin/python3"
    if not Path(candidato).is_file():
        return None
    r = subprocess.run([candidato, "-c", "import importlib.util as u; print(bool((u.find_spec('PySide6') or u.find_spec('PyQt6')) and u.find_spec('gui_comun')))"],
                       capture_output=True, text=True, env=entorno_base())
    return candidato if r.stdout.strip() == "True" else None


def entorno_base() -> dict:
    env = dict(os.environ)
    # con un HOME falso, Python ya no ve ~/.local/lib/python3.x/site-packages (donde pip --user deja gui-comun)
    env.setdefault("PYTHONUSERBASE", str(CASA_REAL / ".local"))
    gui = os.environ.get("GUI_COMUN_DIR")
    if gui and os.path.isdir(os.path.join(gui, "gui_comun")):
        env["PYTHONPATH"] = gui + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


PYTHON_SISTEMA = _python_del_sistema()
requiere_sistema = pytest.mark.skipif(PYTHON_SISTEMA is None, reason="sin binding de Qt con Kirigami o sin gui_comun en /usr/bin/python3")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.basetemp:
        return
    args = [Path(a.split("::")[0]).resolve() for a in (config.args or [])]
    if args and all(REPO in a.parents or a == REPO for a in args):
        BASETEMP.parent.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(BASETEMP)


def _git(raiz: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(raiz), *args], check=True, capture_output=True, env={**os.environ, **ENTORNO_GIT})


ENTORNO_GIT = {"GIT_AUTHOR_NAME": "Prueba", "GIT_AUTHOR_EMAIL": "prueba@ejemplo.org", "GIT_COMMITTER_NAME": "Prueba",
               "GIT_COMMITTER_EMAIL": "prueba@ejemplo.org", "GIT_CONFIG_GLOBAL": "/dev/null"}


def crear_falso(raiz: Path) -> tuple[Path, Path]:
    """Repo con el gestor real (main.sh, config.sh, lib/, docs/) y dos paquetes: git enlazado y shell con un conflicto
    (.zshrc real en HOME) y un pendiente (starship.toml solo en el repo); kde queda ausente."""
    repo, casa = raiz / "dotfiles", raiz / "casa"
    repo.mkdir(parents=True)
    casa.mkdir()
    for n in ("main.sh", "config.sh", ".gitignore", "README.md"):   # .gitignore: .logs/ y .backups/ los ignora el real
        shutil.copy2(REPO / n, repo / n)
    shutil.copytree(REPO / "lib", repo / "lib")
    shutil.copytree(REPO / "docs", repo / "docs")
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
    return repo, casa


@pytest.fixture
def falso(tmp_path, monkeypatch):
    repo, casa = crear_falso(tmp_path)
    monkeypatch.setenv("DOTFILES_DIR", str(repo))
    monkeypatch.setenv("HOME", str(casa))
    for k, v in ENTORNO_GIT.items():
        monkeypatch.setenv(k, v)
    return repo, casa


def entorno_gui(tmp_path: Path, repo: Path | None = None, casa: Path | None = None, **extra: str) -> dict:
    """Entorno de un proceso hijo con GUI: sin pantalla, QSettings y cachés en temporal, el repo y el HOME falsos."""
    env = entorno_base()
    env.update({"QT_QPA_PLATFORM": "offscreen", "XDG_CONFIG_HOME": str(tmp_path / "config"), "XDG_CACHE_HOME": str(tmp_path / "cache"),
                "XDG_STATE_HOME": str(tmp_path / "state"), "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C.UTF-8", **ENTORNO_GIT})
    if repo is not None:
        env["DOTFILES_DIR"] = str(repo)
    if casa is not None:
        env["HOME"] = str(casa)
    env.update(extra)
    return env


def correr_python(guion: str, env: dict, *args: str, plazo: int = 120) -> subprocess.CompletedProcess:
    """Corre `guion` con el Python del sistema (el de Kirigami); argv[1] es la carpeta studio/."""
    return subprocess.run([PYTHON_SISTEMA or sys.executable, "-c", guion, str(STUDIO), *args], env=env, capture_output=True,
                          text=True, timeout=plazo)


@pytest.fixture(scope="session")
def app():
    """Una QGuiApplication offscreen para las pruebas en proceso."""
    from gui_comun.qt import QGuiApplication
    instancia = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])
    yield instancia
