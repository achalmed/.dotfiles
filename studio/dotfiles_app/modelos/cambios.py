"""dotfiles_app/modelos/cambios.py — las filas de la tabla de cambios de git para `ModeloTabla` (Archivo · Paquete ·
Estado · Nota), con el nivel semántico en Estado y el emblema del tipo de cambio."""

from __future__ import annotations

from dotfiles_app import estado as est

COLUMNAS = [("Archivo", "ruta"), ("Paquete", "paquete"), ("Estado", "estado"), ("Nota", "nota")]

# código de `git status --porcelain` (cualquiera de las dos columnas) → (texto, nivel, emblema)
_TIPOS = {"?": ("nuevo", "positivo", "vcs-added"), "A": ("añadido", "positivo", "vcs-added"), "M": ("modificado", "neutro", "vcs-locally-modified"),
          "D": ("eliminado", "negativo", "vcs-removed"), "R": ("renombrado", "neutro", "vcs-locally-modified"),
          "U": ("en conflicto", "negativo", "vcs-conflicting"), "T": ("tipo cambiado", "neutro", "vcs-locally-modified")}


def tipo(codigo: str) -> tuple[str, str, str]:
    letras = codigo.strip() or "M"
    for letra in letras:
        if letra in _TIPOS:
            return _TIPOS[letra]
    return ("modificado", "neutro", "vcs-locally-modified")


def paquete_de(ruta: str) -> str:
    """El primer tramo de la ruta si es un paquete del mapa; si no, «(repo)»: lib/, docs/, studio/…"""
    primero = ruta.split("/", 1)[0]
    return primero if "/" in ruta and primero not in ("docs", "lib", "studio") and not primero.startswith(".") else "(repo)"


def fila(c: est.Cambio) -> dict:
    texto, nivel, emblema = tipo(c.codigo)
    nota = "híbrido: su diff se lee entero antes de confirmar" if c.hibrido else ("archivo nuevo: se confirma entero" if c.nuevo else "")
    return {"ruta": c.ruta, "paquete": paquete_de(c.ruta), "estado": texto, "nota": nota, "nivel": nivel,
            "icono": {"ruta": "text-x-generic", "estado": emblema}, "codigo": c.codigo, "hibrido": c.hibrido, "nuevo": c.nuevo}


def filas(g: est.EstadoGit) -> list[dict]:
    return [fila(c) for c in g.cambios]


def contexto(g: est.EstadoGit) -> str:
    """La derecha de la barra de estado: rama · cambios · commits sin subir (y por bajar)."""
    partes = [f"rama {g.rama}", f"{len(g.cambios)} cambios sin confirmar", f"{g.adelante} sin subir"]
    if g.atras:
        partes.append(f"{g.atras} por bajar")
    return " · ".join(partes)
