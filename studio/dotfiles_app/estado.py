"""El estado de los paquetes y del repo (sin Qt, se prueba solo; solo lee).

Los paquetes y sus archivos salen de `config.sh` (`STOW_PACKAGES`, `PACKAGE_FILES`), leídos por Bash para no tener
una segunda copia del mapa. El estado de cada archivo sigue la leyenda de `main.sh estado` (`lib/stow_ops.sh`):
activo (enlace al repo), conflicto (archivo real en HOME: adoptar), pendiente (en el repo, sin enlace) y ausente.
"""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# Los híbridos (preferencias y estado en el mismo archivo) cambian solos al usar la aplicación: su diff se lee entero
# antes de confirmar (CLAUDE.md, «Detalles que cuesta redescubrir»).
HIBRIDOS = ("kdeglobals", "kwinrc", "konsolerc", "texstudio.ini")
# calibre y KOReader escriben de forma atómica: sustituyen el enlace por un archivo real (se repone con adoptar).
SUSTITUYEN = ("calibre", "koreader")
ESTADOS = ("activo", "conflicto", "pendiente", "ausente")
# qué significa cada estado de archivo y qué orden lo arregla (la leyenda de `main.sh estado`)
EXPLICA = {"activo": "enlazado al repo", "conflicto": "archivo real en HOME: adoptar lo devuelve al repo",
           "pendiente": "en el repo, sin enlace: instalar", "ausente": "ni en el repo ni en HOME"}
# los documentos de la Guía: (texto, ruta relativa al repo)
DOCUMENTOS = (("Uso", "README.md"), ("Paquetes", "docs/paquetes.md"), ("Arquitectura", "docs/arquitectura.md"),
              ("Atajos de KDE", "docs/atajos-kde.md"), ("Decisiones", "docs/decisiones.md"))


def repo() -> Path:
    return Path(os.environ.get("DOTFILES_DIR") or REPO)


def home() -> Path:
    return Path(os.environ.get("HOME") or Path.home())


@dataclass(frozen=True)
class Archivo:
    paquete: str
    rel: str
    estado: str

    @property
    def hibrido(self) -> bool:
        return Path(self.rel).name in HIBRIDOS


@dataclass
class Paquete:
    nombre: str
    archivos: list[Archivo] = field(default_factory=list)

    def cuenta(self, estado: str) -> int:
        return sum(a.estado == estado for a in self.archivos)

    @property
    def estado(self) -> str:
        """El del paquete, con las palabras de `main.sh estado`: activo, parcial (algo enlazado y algo no), conflicto,
        pendiente o ausente."""
        if not self.archivos:
            return "sin config"
        activos = self.cuenta("activo")
        if activos == len(self.archivos):
            return "activo"
        if activos:
            return "parcial"
        for e in ("conflicto", "pendiente"):
            if self.cuenta(e):
                return e
        return "ausente"


def mapa(raiz: Path | None = None) -> dict[str, list[str]]:
    """{paquete: [ruta relativa al HOME]} en el orden de STOW_PACKAGES, leído de config.sh por Bash."""
    raiz = raiz or repo()
    guion = ('source ./config.sh >/dev/null 2>&1 || exit 3\n'
             'for p in "${STOW_PACKAGES[@]}"; do printf "%s\\t%s\\n" "$p" "${PACKAGE_FILES[$p]:-}"; done')
    r = subprocess.run(["bash", "-c", guion], cwd=raiz, capture_output=True, text=True, timeout=30,
                       env={**os.environ, "DOTFILES_DIR": str(raiz)})
    if r.returncode != 0:
        raise RuntimeError(f"no se pudo leer config.sh ({r.returncode}): {r.stderr.strip()[:300]}")
    out: dict[str, list[str]] = {}
    for linea in r.stdout.splitlines():
        nombre, _, lista = linea.partition("\t")
        out[nombre] = [f for f in (x.strip() for x in lista.split("|")) if f]
    return out


def estado_de(paquete: str, rel: str, raiz: Path | None = None, casa: Path | None = None) -> str:
    raiz, casa = raiz or repo(), casa or home()
    en_casa, en_repo = casa / rel, raiz / paquete / rel
    if en_casa.is_symlink():
        try:
            if Path(os.path.realpath(en_casa)).is_relative_to(raiz.resolve()):
                return "activo"
        except OSError:
            pass
    if en_casa.exists() and en_repo.exists():
        return "conflicto"
    if en_repo.exists() and not en_casa.exists():
        return "pendiente"
    return "ausente"


def paquetes(raiz: Path | None = None, casa: Path | None = None) -> list[Paquete]:
    raiz = raiz or repo()
    return [Paquete(p, [Archivo(p, f, estado_de(p, f, raiz, casa)) for f in fs]) for p, fs in mapa(raiz).items()]


# --- git --------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Cambio:
    ruta: str
    codigo: str          # las dos letras de `git status --porcelain`

    @property
    def nuevo(self) -> bool:
        return self.codigo == "??"

    @property
    def hibrido(self) -> bool:
        return Path(self.ruta).name in HIBRIDOS


@dataclass(frozen=True)
class EstadoGit:
    rama: str
    adelante: int
    atras: int
    cambios: tuple[Cambio, ...]


def _git(*args: str, raiz: Path | None = None) -> str:
    r = subprocess.run(["git", "-C", str(raiz or repo()), *args], capture_output=True, text=True, timeout=30)
    return r.stdout if r.returncode == 0 else ""


def estado_git(raiz: Path | None = None) -> EstadoGit:
    salida = _git("status", "--porcelain=v1", "-b", raiz=raiz).splitlines()
    rama, adelante, atras = "—", 0, 0
    cambios = []
    for l in salida:
        if l.startswith("## "):
            rama = l[3:].split("...")[0]
            m = re.search(r"ahead (\d+)", l)
            adelante = int(m.group(1)) if m else 0
            m = re.search(r"behind (\d+)", l)
            atras = int(m.group(1)) if m else 0
        elif len(l) > 3:
            cambios.append(Cambio(l[3:].strip('"'), l[:2]))
    return EstadoGit(rama, adelante, atras, tuple(cambios))


def diff(ruta: str, raiz: Path | None = None) -> str:
    """El diff ENTERO de un archivo (o su contenido, si es nuevo): se lee antes de confirmar."""
    raiz = raiz or repo()
    texto = _git("diff", "--no-color", "--", ruta, raiz=raiz)
    if texto:
        return texto
    p = raiz / ruta
    if p.is_file():
        try:
            return "(archivo nuevo)\n" + p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return "(no se pudo leer)"
    return "(sin diferencias)"


def orden_confirmar(ruta: str, mensaje: str) -> list[str]:
    """Escanear credenciales y, si sale limpio, confirmar SOLO esa ruta (regla del repo: nunca `git add .`).
    Corre en la raíz del repo (el `cwd` del worker)."""
    guion = ('set -euo pipefail\n'
             './main.sh seguridad\n'
             'git add -- "$1"\n'
             'git commit -m "$2" -- "$1"')
    return ["bash", "-c", guion, "confirmar", ruta, mensaje]


# --- consultas nuevas (2026-11-02, Dotfiles Studio en QML) ------------------------------------------------------------

def destino_enlace(rel: str, casa: Path | None = None) -> str:
    """A dónde apunta el enlace de HOME (vacío si no es un enlace)."""
    p = (casa or home()) / rel
    try:
        return os.readlink(p) if p.is_symlink() else ""
    except OSError:
        return ""


def orden_main(*args: str) -> list[str]:
    """La orden de `main.sh` para un proceso hijo con `cwd` en la raíz del repo (sin rutas absolutas en la salida)."""
    return ["bash", "main.sh", *args]


def orden_paquetes(operacion: str, paquetes: list[str], *, simular: bool = False, detallado: bool = True,
                   forzar: bool = False) -> list[str]:
    """`main.sh instalar|adoptar|eliminar -p a,b [--dry-run] [--verbose] [--force]`.

    `--force` va siempre con eliminar: `confirm_action` lee la entrada estándar, que en un proceso hijo de la ventana no
    responde (y la ventana ya preguntó); con instalar solo si se pide (reemplaza los archivos reales de HOME, con
    respaldo); adoptar no lo usa (pregunta por /dev/tty: ver `necesita_terminal`)."""
    if operacion not in ("instalar", "adoptar", "eliminar"):
        raise ValueError(f"operación desconocida: {operacion}")
    args = [operacion, "-p", ",".join(paquetes)]
    if simular:
        args.append("--dry-run")
    if detallado:
        args.append("--verbose")
    if operacion == "eliminar" or (operacion == "instalar" and forzar):
        args.append("--force")
    return orden_main(*args)


def necesita_terminal(operacion: str, paquetes: list[Paquete]) -> bool:
    """Adoptar un archivo que existe en HOME y en el repo pregunta por /dev/tty (`_resolve_conflict`): sin terminal,
    `main.sh` lo salta en silencio. La ventana lo abre entonces en una terminal."""
    return operacion == "adoptar" and any(a.estado == "conflicto" for p in paquetes for a in p.archivos)


def orden_push(raiz: Path | None = None) -> list[str]:
    return ["git", "-C", str(raiz or repo()), "push"]


def documentos(raiz: Path | None = None) -> list[dict]:
    """La Guía: [{texto, ruta, existe}] en el orden de DOCUMENTOS."""
    raiz = raiz or repo()
    return [{"texto": t, "ruta": r, "existe": (raiz / r).is_file()} for t, r in DOCUMENTOS]


def leer_documento(rel: str, raiz: Path | None = None) -> tuple[dict, str]:
    """(frontmatter como dict de cadenas, cuerpo sin el frontmatter) de un documento del repo."""
    p = (raiz or repo()) / rel
    if not p.is_file():
        return {}, f"No está {rel}."
    texto = p.read_text(encoding="utf-8", errors="replace")
    meta: dict[str, str] = {}
    if texto.startswith("---\n") and "\n---\n" in texto:
        cabecera, texto = texto[4:].split("\n---\n", 1)
        for linea in cabecera.splitlines():
            clave, sep, valor = linea.partition(":")
            if sep and not linea.startswith(" "):
                meta[clave.strip()] = valor.strip().strip("'\"")
    return meta, texto.lstrip("\n")
