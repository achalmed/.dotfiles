"""servicios/plan.py — lo que `main.sh` hará con cada archivo de un paquete, antes de hacerlo.

Reproduce, archivo por archivo, las decisiones de `lib/stow_ops.sh` para cada operación:

| estado | instalar | adoptar | actualizar | quitar enlaces |
|---|---|---|---|---|
| activo | rehace el enlace | ya enlazado | rehace el enlace | quita el enlace |
| conflicto | se salta, o con `--force` respalda y reemplaza | pregunta qué versión conservar (terminal) | **borra el archivo real sin respaldo** (bloqueado) | no se toca |
| pendiente | crea el enlace | crea el enlace | crea el enlace | no se toca |
| local | se salta (no está en el repo) | mueve el archivo al repo y lo enlaza | se salta | no se toca |
| ausente | se salta | se salta | se salta | no se toca |

`actualizar` es `ln -sfn` sobre cada archivo del repo: con un archivo real (o una carpeta) en HOME lo borraría sin
respaldo, así que el plan la bloquea y propone instalar con «Reemplazar» (que respalda) o adoptar. Sin terminal,
`main.sh` toma la opción segura cuando pregunta (saltar); el plan lo dice y pide la terminal donde hace falta.

    p = plan("instalar", paquete, forzar=True)
    p["archivos"]      # [{rel, estado, accion, detalle, nivel, cambia}]
    p["consecuencias"] # «Instalar kde: 2 enlaces nuevos; 1 archivo real reemplazado (queda en .backups/)…»
"""

from __future__ import annotations

from pathlib import Path

from dotfiles_app import estado as est

OPERACIONES = ("instalar", "adoptar", "actualizar", "eliminar")
TEXTO = {"instalar": "Instalar", "adoptar": "Adoptar", "actualizar": "Actualizar", "eliminar": "Quitar enlaces"}
QUE_HACE = {
    "instalar": "Crea los enlaces de HOME hacia el repo. Antes, respaldo de lo que toca en .backups/.",
    "adoptar": "Lleva al repo los archivos que solo están en HOME y deja el enlace en su lugar.",
    "actualizar": "Rehace los enlaces de todo lo que está en el repo, sin respaldo.",
    "eliminar": "Quita los enlaces de HOME; el repo no cambia y la aplicación pierde esa configuración hasta instalar.",
}
# el estado de la operación en gui-comun (Acciones.OPERACIONES)
ESTADO_OPERACION = {"instalar": "instalacion", "adoptar": "escritura", "actualizar": "instalacion", "eliminar": "eliminacion"}


def _fila(a: est.Archivo, accion: str, detalle: str = "", nivel: str = "", cambia: bool = False) -> dict:
    return {"rel": a.rel, "estado": a.estado, "accion": accion, "detalle": detalle, "nivel": nivel, "cambia": cambia,
            "hibrido": a.hibrido}


def plan(operacion: str, paquete: est.Paquete, *, forzar: bool = False, raiz: Path | None = None,
         casa: Path | None = None, compartidas: dict[str, list[str]] | None = None) -> dict:
    if operacion not in OPERACIONES:
        raise ValueError(f"operación desconocida: {operacion}")
    raiz = raiz or est.repo()
    filas: list[dict] = []
    terminal = respaldo = False
    bloqueo = ""
    en_repo = (raiz / paquete.nombre).is_dir()

    for a in paquete.archivos:
        carpeta = est.es_carpeta(paquete.nombre, a.rel, raiz, casa)
        if operacion == "instalar":
            if a.estado in ("local", "ausente"):
                filas.append(_fila(a, "se salta", "no está en el repo", "neutro"))
            elif a.estado == "activo":
                filas.append(_fila(a, "rehace el enlace", "ya enlazado: no cambia nada"))
            elif a.estado == "conflicto":
                if forzar:
                    filas.append(_fila(a, "reemplaza por el enlace", f"{'la carpeta' if carpeta else 'el archivo'} de HOME queda en .backups/",
                                       "negativo", True))
                else:
                    filas.append(_fila(a, "se salta", "hay un archivo real en HOME: marque «Reemplazar» o adopte", "neutro"))
            else:
                filas.append(_fila(a, "crea el enlace", "", "positivo", True))
        elif operacion == "adoptar":
            if a.estado == "activo":
                filas.append(_fila(a, "ya enlazado", "no cambia nada"))
            elif a.estado == "local":
                filas.append(_fila(a, "lo mueve al repo y lo enlaza", "el archivo entra al repo: confírmelo después en Cambios", "positivo", True))
            elif a.estado == "conflicto":
                terminal = respaldo = True
                filas.append(_fila(a, "pregunta qué versión conservar", "está en HOME y en el repo: se responde en una terminal (antes, respaldo)",
                                   "neutro", True))
            elif a.estado == "pendiente":
                filas.append(_fila(a, "crea el enlace", "", "positivo", True))
            else:
                filas.append(_fila(a, "se salta", "no existe en HOME ni en el repo", "neutro"))
        elif operacion == "actualizar":
            if a.estado in ("local", "ausente"):
                filas.append(_fila(a, "se salta", "no está en el repo", "neutro"))
            elif a.estado == "conflicto":
                bloqueo = ("Hay archivos reales en HOME que «actualizar» borraría sin respaldo (ln -sfn). "
                           "Use Instalar con «Reemplazar», que respalda, o Adoptar.")
                filas.append(_fila(a, "lo borraría sin respaldo", "bloqueado: use Instalar con «Reemplazar» o Adoptar", "negativo"))
            elif a.estado == "activo":
                filas.append(_fila(a, "rehace el enlace", "ya enlazado: no cambia nada"))
            else:
                filas.append(_fila(a, "crea el enlace", "", "positivo", True))
        else:  # eliminar
            if a.estado == "activo":
                filas.append(_fila(a, "quita el enlace", "la aplicación pierde esta configuración hasta instalar; el repo no cambia",
                                   "negativo", True))
            else:
                filas.append(_fila(a, "no se toca", est.EXPLICA.get(a.estado, "")))
        if compartidas and a.rel in compartidas:
            otros = [p for p in compartidas[a.rel] if p != paquete.nombre]
            filas[-1]["detalle"] = (filas[-1]["detalle"] + " · " if filas[-1]["detalle"] else "") + f"también la reclama {', '.join(otros)}"

    huerfanos = est.huerfanos(paquete.nombre, [a.rel for a in paquete.archivos], raiz) if operacion == "adoptar" else []
    if operacion == "instalar":
        respaldo = True
        if not en_repo:
            bloqueo = f"El paquete {paquete.nombre} no está en el repo: adóptelo primero."
    if operacion == "eliminar" and not any(f["cambia"] for f in filas):
        bloqueo = "Ningún archivo de este paquete está enlazado: no hay enlaces que quitar."
    if not paquete.archivos:
        bloqueo = f"{paquete.nombre} no tiene archivos en PACKAGE_FILES (config.sh)."

    cambian = sum(f["cambia"] for f in filas)
    return {"operacion": operacion, "texto": TEXTO[operacion], "queHace": QUE_HACE[operacion], "paquete": paquete.nombre,
            "archivos": filas, "cambian": cambian, "saltan": sum(f["accion"] == "se salta" for f in filas),
            "terminal": terminal, "respaldo": respaldo, "bloqueo": bloqueo, "huerfanos": huerfanos,
            "hayQueHacer": cambian > 0 and not bloqueo, "estadoOperacion": ESTADO_OPERACION[operacion],
            "resumen": resumen(operacion, filas, huerfanos, respaldo, terminal),
            "consecuencias": consecuencias(operacion, paquete.nombre, filas, huerfanos, respaldo, terminal)}


def _cuenta(filas: list[dict], accion: str) -> int:
    return sum(f["accion"] == accion for f in filas)


def resumen(operacion: str, filas: list[dict], huerfanos: list[str], respaldo: bool, terminal: bool) -> str:
    """Una línea: «2 enlaces nuevos · 1 se salta»."""
    partes = []
    for accion, singular, plural in (("crea el enlace", "enlace nuevo", "enlaces nuevos"),
                                     ("reemplaza por el enlace", "archivo real reemplazado", "archivos reales reemplazados"),
                                     ("lo mueve al repo y lo enlaza", "archivo al repo", "archivos al repo"),
                                     ("pregunta qué versión conservar", "conflicto por resolver", "conflictos por resolver"),
                                     ("quita el enlace", "enlace quitado", "enlaces quitados"),
                                     ("lo borraría sin respaldo", "archivo real en juego", "archivos reales en juego"),
                                     ("se salta", "se salta", "se saltan")):
        n = _cuenta(filas, accion)
        if n:
            partes.append(f"{n} {singular if n == 1 else plural}")
    if huerfanos:
        partes.append(f"{len(huerfanos)} huérfano{'s' if len(huerfanos) != 1 else ''} en el repo")
    if not partes:
        partes.append("nada cambia")
    return " · ".join(partes)


def consecuencias(operacion: str, nombre: str, filas: list[dict], huerfanos: list[str], respaldo: bool, terminal: bool) -> str:
    """El texto del diálogo de confirmación: qué cambia en HOME y en el repo, el respaldo y lo que queda fuera."""
    texto = f"{TEXTO[operacion]} {nombre}: {resumen(operacion, filas, huerfanos, respaldo, terminal)}."
    if operacion == "instalar":
        texto += " Antes se guarda un respaldo de lo que se toca en .backups/."
    if operacion == "eliminar":
        texto += " Las aplicaciones afectadas pierden esa configuración hasta volver a instalar; el repo no cambia."
    if operacion == "adoptar" and any(f["accion"] == "lo mueve al repo y lo enlaza" for f in filas):
        texto += " Los archivos movidos aparecen después en Cambios, para confirmarlos (el repo es público)."
    if terminal:
        texto += " Hay archivos en los dos lados: main.sh pregunta cuál conservar, así que se abre en una terminal."
    if huerfanos:
        texto += " main.sh preguntará si borra del repo los huérfanos; sin respuesta, se conservan."
    return texto
