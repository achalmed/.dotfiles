"""servicios/comparar.py — la comparación de un archivo de un paquete antes de operar con él, lado a lado.

Qué se compara depende del estado del archivo (la pregunta que el usuario tiene delante):

| estado | izquierda | derecha | para decidir |
|---|---|---|---|
| conflicto | el repo | HOME | adoptar (gana HOME) o instalar con «Reemplazar» (gana el repo) |
| activo | el último commit | el repo (= HOME, por el enlace) | qué reescribió la aplicación desde el último commit (`git diff`, con el filtro `clean`) |
| pendiente | — | el repo | lo que HOME verá al instalar |
| local | — | HOME | lo que entraría al repo (público) al adoptar |

Una carpeta entera se compara por su lista de archivos (tamaño y huella de contenido). Las líneas con un secreto se
enmascaran DESPUÉS de comparar (así una contraseña distinta a cada lado sigue viéndose como un cambio, sin mostrarse).
Devuelve el diccionario que pinta `VistaDiferencia` (las filas de `diferencias.analizar`) más el modo y las notas.
"""

from __future__ import annotations

import difflib
import hashlib
import subprocess
from pathlib import Path

from dotfiles_app import estado as est
from dotfiles_app.servicios import diferencias, seguridad

MAX_BYTES = 1_000_000
FILTRADOS = {"texstudio.ini": "lib/filtros/texstudio_ini.sh"}     # los que git compara tras su filtro clean (.gitattributes)
APLICACION_HIBRIDO = {"kdeglobals": "Plasma", "kwinrc": "KWin", "konsolerc": "Konsole", "texstudio.ini": "TeXstudio"}


def _leer(p: Path) -> tuple[list[str] | None, bool]:
    """(líneas, binario). None si no existe o no se puede leer."""
    try:
        with p.open("rb") as f:
            datos = f.read(MAX_BYTES)
    except OSError:
        return None, False
    if b"\0" in datos[:8192]:
        return [], True
    return datos.decode("utf-8", "replace").splitlines(), False


def _listado(carpeta: Path) -> list[str]:
    """Una carpeta como lista de «ruta · tamaño · huella»: dos carpetas se comparan como dos textos."""
    salida = []
    for f in sorted(carpeta.rglob("*")):
        if f.is_file():
            try:
                h = hashlib.sha256(f.read_bytes()[:MAX_BYTES]).hexdigest()[:8]
                salida.append(f"{f.relative_to(carpeta)}  ·  {f.stat().st_size} B  ·  {h}")
            except OSError:
                salida.append(f"{f.relative_to(carpeta)}  ·  (no se puede leer)")
    return salida


def _contenido(p: Path) -> tuple[list[str] | None, bool]:
    if p.is_dir():
        return _listado(p), False
    return _leer(p)


def _unificado(izq: list[str], der: list[str], nombre_izq: str, nombre_der: str) -> str:
    return "\n".join(difflib.unified_diff(izq, der, nombre_izq, nombre_der, n=3, lineterm=""))


def _git(raiz: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, timeout=30)
    return r.stdout if r.returncode == 0 else ""


def enmascarar_filas(d: dict, patrones) -> int:
    """Enmascara las filas en su sitio; devuelve cuántas tenían un secreto."""
    if not patrones:
        return 0
    n = 0
    for f in d["filas"]:
        for lado in ("izq", "der"):
            limpio = seguridad.enmascarar(f[lado], patrones)
            if limpio != f[lado]:
                f[lado] = limpio
                n += 1
    return n


def comparar(paquete: str, archivo: est.Archivo, *, raiz: Path | None = None, casa: Path | None = None,
             patrones=None) -> dict:
    raiz, casa = raiz or est.repo(), casa or est.home()
    en_repo, en_casa = raiz / paquete / archivo.rel, casa / archivo.rel
    nombre = Path(archivo.rel).name
    notas: list[str] = []
    izquierda, derecha, texto, binario = "", "", "", False
    carpeta = est.es_carpeta(paquete, archivo.rel, raiz, casa)

    if archivo.estado == "conflicto":
        izquierda, derecha = "Repositorio", "HOME (archivo real)"
        a, ba = _contenido(en_repo)
        b, bb = _contenido(en_casa)
        binario = ba or bb
        if not binario and a is not None and b is not None:
            texto = _unificado(a, b, f"repo/{paquete}/{archivo.rel}", f"~/{archivo.rel}")
            notas.append("Idénticos: adoptar o instalar no cambia el contenido, solo deja el enlace." if not texto else
                         "Adoptar conserva la versión de HOME (a la derecha); instalar con «Reemplazar», la del repo (a la izquierda).")
    elif archivo.estado == "activo":
        izquierda, derecha = "Último commit", "Repositorio = HOME (enlazado)"
        rel = f"{paquete}/{archivo.rel}"
        texto = _git(raiz, "diff", "--no-color", "--", rel)
        if not texto and _git(raiz, "status", "--porcelain", "--", rel).startswith("??"):
            c, binario = _contenido(en_repo)
            if c is not None and not binario:
                texto = _unificado([], c, "/dev/null", rel)
            notas.append("Nuevo en el repo, aún sin confirmar.")
        if not texto and not binario:
            notas.append("Sin cambios desde el último commit.")
        if nombre in FILTRADOS:
            notas.append(f"git lo compara tras su filtro clean ({FILTRADOS[nombre]}), que quita el estado volátil: "
                         "esta es la diferencia que se confirmaría.")
    elif archivo.estado == "pendiente":
        izquierda, derecha = "HOME (no existe)", "Repositorio"
        c, binario = _contenido(en_repo)
        if c is not None and not binario:
            texto = _unificado([], c, "/dev/null", f"repo/{paquete}/{archivo.rel}")
        notas.append("Instalar crea el enlace: HOME verá este contenido.")
    elif archivo.estado == "local":
        izquierda, derecha = "Repositorio (no existe)", "HOME"
        c, binario = _contenido(en_casa)
        if c is not None and not binario:
            texto = _unificado([], c, "/dev/null", f"~/{archivo.rel}")
        notas.append("Adoptar lo mueve al repo, que es público: esto es lo que se publicaría al confirmarlo.")
    else:
        notas.append("No existe en el repo ni en HOME: la aplicación aún no lo creó o no está instalada.")

    if archivo.hibrido:
        notas.insert(0, f"Híbrido: {APLICACION_HIBRIDO.get(nombre, 'la aplicación')} lo reescribe al usarse "
                        "(preferencias y estado en el mismo archivo); lea la diferencia entera antes de confirmar.")
    if carpeta:
        notas.append("Es una carpeta enlazada entera: se compara su lista de archivos (tamaño y huella del contenido).")

    d = diferencias.analizar(texto)
    ocultas = enmascarar_filas(d, patrones)
    if ocultas:
        notas.append(f"{ocultas} línea(s) con un posible secreto, oculto (el escáner de Seguridad dice dónde).")
    trozos = len(d["trozos"])
    return {"ruta": archivo.rel, "paquete": paquete, "estado": archivo.estado, "izquierda": izquierda, "derecha": derecha,
            "filas": d["filas"], "trozos": trozos, "anadidas": d["anadidas"], "quitadas": d["quitadas"],
            "binario": binario, "recortado": d["recortado"], "vacia": not d["filas"], "nuevo": False,
            "hibrido": archivo.hibrido, "carpeta": carpeta, "notas": notas, "ocultas": ocultas}
