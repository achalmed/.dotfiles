"""servicios/seguridad.py — el escáner de credenciales de la ventana: los mismos patrones que `main.sh seguridad`
(`SENSITIVE_PATTERNS` y sus nombres, `SENSITIVE_PATTERN_NAMES`, leídos de `config.sh` por Bash: una sola lista), sobre
los mismos archivos (`git ls-files --cached --others --exclude-standard`, sin la lista blanca ni los binarios), más la
regla de los `.env` versionados.

**El secreto nunca sale de aquí.** Un hallazgo es {archivo, linea, tipo, huella}: la huella es un HMAC-SHA256 del valor
con una clave aleatoria de esta sesión, recortado a 8 cifras hexadecimales, más su longitud. Sirve para ver que dos
hallazgos son el mismo secreto (en dos archivos, o en HOME y en el repo) sin poder recuperarlo ni probar contraseñas
contra ella fuera de esta sesión. `enmascarar(texto)` sustituye cada coincidencia por «⟨oculto: tipo⟩» para que la
comparación de un archivo tampoco lo muestre.

    patrones = cargar(repo)                    # [(nombre, re.Pattern)]
    hallazgos = escanear(repo, patrones)      # [{archivo, linea, tipo, huella}]
    linea_segura = enmascarar(linea, patrones)
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import subprocess
from pathlib import Path

_CLAVE = secrets.token_bytes(32)                   # de la sesión: la huella no vale fuera de ella
ENV_PERMITIDOS = (".env.example", ".env.sample", ".env.template")
MAX_BYTES = 2_000_000                              # un archivo de configuración más grande no se lee entero


def _ere_a_python(patron: str) -> str:
    """Las expresiones de `config.sh` son ERE de grep: la única clase POSIX que usan es [:space:]."""
    return patron.replace("[:space:]", r"\s")


def cargar(raiz: Path) -> list[tuple[str, re.Pattern]]:
    """[(nombre, patrón compilado)] en el orden de `config.sh`, sin mayúsculas ni minúsculas (como `grep -i`)."""
    guion = ('source ./config.sh >/dev/null 2>&1 || exit 3\n'
             'for i in "${!SENSITIVE_PATTERNS[@]}"; do\n'
             '  printf "%s\\0%s\\0" "${SENSITIVE_PATTERN_NAMES[$i]:-patrón $((i + 1))}" "${SENSITIVE_PATTERNS[$i]}"\n'
             'done')
    r = subprocess.run(["bash", "-c", guion], cwd=raiz, capture_output=True, timeout=30,
                       env={**os.environ, "DOTFILES_DIR": str(raiz)})
    if r.returncode != 0:
        raise RuntimeError(f"no se pudieron leer los patrones de config.sh ({r.returncode})")
    partes = r.stdout.decode("utf-8", "replace").split("\0")[:-1]
    return [(partes[i], re.compile(_ere_a_python(partes[i + 1]), re.IGNORECASE)) for i in range(0, len(partes) - 1, 2)]


def lista_blanca(raiz: Path) -> set[str]:
    guion = 'source ./config.sh >/dev/null 2>&1 || exit 3\nprintf "%s\\0" "${SENSITIVE_SCAN_ALLOWLIST[@]}"'
    r = subprocess.run(["bash", "-c", guion], cwd=raiz, capture_output=True, timeout=30,
                       env={**os.environ, "DOTFILES_DIR": str(raiz)})
    return {x for x in r.stdout.decode("utf-8", "replace").split("\0") if x} if r.returncode == 0 else set()


def archivos(raiz: Path) -> list[str]:
    """Lo que subiría un `git add .`: lo rastreado y lo nuevo sin ignorar (lo mismo que mira `main.sh seguridad`)."""
    r = subprocess.run(["git", "-C", str(raiz), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                       capture_output=True, timeout=60)
    return [x for x in r.stdout.decode("utf-8", "replace").split("\0") if x] if r.returncode == 0 else []


def huella(valor: str) -> str:
    """«a1b2c3d4 · 40 car.»: correlaciona sin revelar (HMAC con la clave de la sesión)."""
    h = hmac.new(_CLAVE, valor.encode("utf-8", "replace"), hashlib.sha256).hexdigest()[:8]
    return f"{h} · {len(valor)} car."


def es_env(ruta: str) -> bool:
    base = ruta.rsplit("/", 1)[-1]
    if base in ENV_PERMITIDOS or base.endswith(ENV_PERMITIDOS):
        return False
    return base == ".env" or base.endswith(".env") or base.startswith(".env.")


def _texto(p: Path) -> str | None:
    """El texto del archivo, o None si es binario (como `grep -I`) o no se puede leer."""
    try:
        with p.open("rb") as f:
            datos = f.read(MAX_BYTES)
    except OSError:
        return None
    if b"\0" in datos[:8192]:
        return None
    return datos.decode("utf-8", "replace")


def escanear_texto(texto: str, patrones: list[tuple[str, re.Pattern]], archivo: str = "") -> list[dict]:
    """Cada coincidencia de cada patrón, por línea: {archivo, linea, tipo, huella}. Sin el valor."""
    salida = []
    for n, linea in enumerate(texto.splitlines(), start=1):
        for nombre, patron in patrones:
            for m in patron.finditer(linea):
                salida.append({"archivo": archivo, "linea": n, "tipo": nombre, "huella": huella(m.group(0))})
    return salida


def escanear(raiz: Path, patrones: list[tuple[str, re.Pattern]] | None = None, rutas: list[str] | None = None,
             cancelado=None) -> list[dict]:
    """El escáner sobre el repo (o sobre `rutas`, relativas a él). Ordenado por archivo y línea."""
    patrones = patrones if patrones is not None else cargar(raiz)
    blanca = lista_blanca(raiz)
    salida: list[dict] = []
    for rel in (rutas if rutas is not None else archivos(raiz)):
        if cancelado and cancelado():
            break
        if rel in blanca:
            continue
        p = raiz / rel
        if not p.is_file():
            continue
        if es_env(rel):
            salida.append({"archivo": rel, "linea": 0, "tipo": "archivo .env versionado", "huella": "—"})
        texto = _texto(p)
        if texto is not None:
            salida.extend(escanear_texto(texto, patrones, rel))
    return sorted(salida, key=lambda h: (h["archivo"], h["linea"], h["tipo"]))


def enmascarar(texto: str, patrones: list[tuple[str, re.Pattern]]) -> str:
    """El texto con cada secreto sustituido por «⟨oculto: tipo⟩» (para la comparación y los diffs)."""
    for nombre, patron in patrones:
        texto = patron.sub(f"⟨oculto: {nombre}⟩", texto)
    return texto


def informe(hallazgos: list[dict]) -> str:
    """El informe en Markdown (para copiar o guardar): archivo, línea, tipo y huella; nunca el valor."""
    if not hallazgos:
        return "# Escáner de credenciales\n\nSin hallazgos.\n"
    filas = "\n".join(f"| `{h['archivo']}` | {h['linea'] or '—'} | {h['tipo']} | {h['huella']} |" for h in hallazgos)
    return ("# Escáner de credenciales\n\n"
            f"{len(hallazgos)} posible(s) dato(s) sensible(s). El valor no se muestra; la huella es de esta sesión.\n\n"
            "| archivo | línea | tipo | huella |\n|---|---|---|---|\n" + filas + "\n")
