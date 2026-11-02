"""dotfiles_app/modelos/paquetes.py — los nodos del árbol de paquetes (paquete › archivo) para `ModeloArbol`.

Columnas: Paquete / archivo · Estado · Detalle. Cada nodo lleva `valores` (uno por columna), `nivel` (color semántico
solo en Estado), `icono` ({0: del paquete o del archivo, 1: el emblema del estado}) y lo propio del dominio
(`paquete`, `rel`, `estado`), que `ModeloArbol.datos(indice)` devuelve a los controladores.
"""

from __future__ import annotations

from dotfiles_app import estado as est

COLUMNAS = ("Paquete / archivo", "Estado", "Detalle")
FILTROS = (("todos", "Todos", "package-x-generic"), ("atencion", "Piden atención", "dialog-warning"),
           ("activos", "Activos", "vcs-normal"))

# estado → (nivel semántico, emblema del tema)
NIVEL = {"activo": "positivo", "parcial": "neutro", "conflicto": "negativo", "pendiente": "activo",
         "ausente": "inactivo", "sin config": "inactivo"}
EMBLEMA = {"activo": "vcs-normal", "parcial": "vcs-locally-modified", "conflicto": "vcs-conflicting",
           "pendiente": "vcs-update-required", "ausente": "emblem-remove", "sin config": "emblem-question"}


def pide_atencion(p: est.Paquete) -> bool:
    return p.estado != "activo"


def pasa_filtro(p: est.Paquete, filtro: str) -> bool:
    if filtro == "atencion":
        return pide_atencion(p)
    if filtro == "activos":
        return p.estado == "activo"
    return True


def detalle_paquete(p: est.Paquete) -> str:
    if not p.archivos:
        return "sin archivos en PACKAGE_FILES"
    activos = p.cuenta("activo")
    if activos == len(p.archivos):
        return f"{activos}/{len(p.archivos)} enlazados"
    partes = [f"{p.cuenta(e)} {e}" for e in est.ESTADOS if p.cuenta(e)]
    return " · ".join(partes)


def nodo_archivo(a: est.Archivo) -> dict:
    nota = est.EXPLICA.get(a.estado, "")
    if a.hibrido:
        nota += " · híbrido: cambia solo al usar la aplicación"
    return {"valores": [a.rel, a.estado, nota], "nivel": NIVEL.get(a.estado, ""), "icono": {0: "text-x-generic", 1: EMBLEMA.get(a.estado, "")},
            "paquete": a.paquete, "rel": a.rel, "estado": a.estado, "hibrido": a.hibrido}


def nodo_paquete(p: est.Paquete, texto: str = "") -> dict:
    texto = texto.strip().lower()
    archivos = p.archivos
    if texto and texto not in p.nombre.lower():                      # el texto no está en el nombre: solo los archivos que casan
        archivos = [a for a in archivos if texto in a.rel.lower()]
    return {"valores": [p.nombre, p.estado, detalle_paquete(p)], "nivel": NIVEL.get(p.estado, ""),
            "icono": {0: "package-x-generic", 1: EMBLEMA.get(p.estado, "")},
            "paquete": p.nombre, "rel": None, "estado": p.estado, "sustituye": p.nombre in est.SUSTITUYEN,
            "hijos": [nodo_archivo(a) for a in archivos]}


def nodos(paquetes: list[est.Paquete], filtro: str = "todos", texto: str = "") -> list[dict]:
    """Los nodos raíz del árbol: los paquetes que pasan el filtro de estado y el texto (nombre o alguno de sus archivos)."""
    t = texto.strip().lower()
    salida = []
    for p in paquetes:
        if not pasa_filtro(p, filtro):
            continue
        if t and t not in p.nombre.lower() and not any(t in a.rel.lower() for a in p.archivos):
            continue
        salida.append(nodo_paquete(p, texto))
    return salida


def contadores(paquetes: list[est.Paquete]) -> dict:
    """Lo que la navegación y la barra de estado muestran: paquetes por filtro y enlaces activos del total."""
    archivos = [a for p in paquetes for a in p.archivos]
    return {"todos": len(paquetes), "atencion": sum(pide_atencion(p) for p in paquetes),
            "activos": sum(p.estado == "activo" for p in paquetes),
            "enlaces": sum(a.estado == "activo" for a in archivos), "enlacesTotal": len(archivos),
            "conflictos": sum(a.estado == "conflicto" for a in archivos),
            "pendientes": sum(a.estado == "pendiente" for a in archivos),
            "ausentes": sum(a.estado == "ausente" for a in archivos)}


def resumen(c: dict) -> str:
    partes = [f"{c['todos']} paquetes", f"{c['activos']} activos"]
    if c["atencion"]:
        partes.append(f"{c['atencion']} piden atención")
    partes.append(f"{c['enlaces']}/{c['enlacesTotal']} enlaces")
    return " · ".join(partes)
