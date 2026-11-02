"""services/diferencias.py — la diferencia unificada de git convertida en filas lado a lado, por trozos.

Puro (sin git ni Qt): recibe el texto de `git diff` de un archivo y devuelve
- `cabecera`: las líneas `diff --git`, `index`, `---`, `+++` (para rehacer el parche de un trozo);
- `trozos`: cada `@@ -a,b +c,d @@` con sus líneas originales (para prepararlo, quitarlo o descartarlo con `git apply`);
- `filas`: lo que pinta la vista lado a lado: a la izquierda lo de antes, a la derecha lo de después; una línea
  quitada y una añadida contiguas se emparejan en la misma fila (como Sublime Merge o Meld). Cada fila:
  {tipo: trozo · igual · cambio · quitada · anadida · aviso, trozo, izqNum, izq, izqTipo, derNum, der, derTipo}.

    d = analizar(texto)
    parche = parche_de_trozo(d, 0)        # para `git apply --cached`
"""

from __future__ import annotations

import re

_TROZO = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
MAX_FILAS = 6000


def analizar(texto: str, max_filas: int = MAX_FILAS) -> dict:
    cabecera: list[str] = []
    trozos: list[dict] = []
    filas: list[dict] = []
    binario = False
    actual: dict | None = None
    izq = der = 0
    quitadas: list[tuple[int, str]] = []
    anadidas: list[tuple[int, str]] = []
    recortado = False

    def volcar():
        """Empareja las quitadas y añadidas pendientes en filas lado a lado."""
        nonlocal quitadas, anadidas
        n = max(len(quitadas), len(anadidas))
        for k in range(n):
            q = quitadas[k] if k < len(quitadas) else None
            a = anadidas[k] if k < len(anadidas) else None
            tipo = "cambio" if q and a else ("quitada" if q else "anadida")
            filas.append({"tipo": tipo, "trozo": len(trozos) - 1,
                          "izqNum": q[0] if q else 0, "izq": q[1] if q else "", "izqTipo": "quitada" if q else "vacia",
                          "derNum": a[0] if a else 0, "der": a[1] if a else "", "derTipo": "anadida" if a else "vacia"})
        quitadas, anadidas = [], []

    for linea in (texto or "").splitlines():
        if actual is None and not linea.startswith("@@"):
            if linea.startswith("Binary files") or linea.startswith("GIT binary patch"):
                binario = True
            cabecera.append(linea)
            continue
        m = _TROZO.match(linea)
        if m:
            volcar()
            izq, der = int(m.group(1)), int(m.group(3))
            actual = {"indice": len(trozos), "cabecera": linea, "lineas": [], "titulo": m.group(5).strip(),
                      "izq": izq, "der": der}
            trozos.append(actual)
            filas.append({"tipo": "trozo", "trozo": actual["indice"], "izqNum": 0, "izq": linea, "izqTipo": "trozo",
                          "derNum": 0, "der": m.group(5).strip(), "derTipo": "trozo"})
            continue
        if actual is None:
            continue
        actual["lineas"].append(linea)
        if len(filas) >= max_filas:
            recortado = True
            continue
        if linea.startswith("-"):
            quitadas.append((izq, linea[1:]))
            izq += 1
        elif linea.startswith("+"):
            anadidas.append((der, linea[1:]))
            der += 1
        elif linea.startswith("\\"):
            volcar()
            filas.append({"tipo": "aviso", "trozo": actual["indice"], "izqNum": 0, "izq": linea[2:], "izqTipo": "aviso",
                          "derNum": 0, "der": "", "derTipo": "aviso"})
        else:
            volcar()
            contenido = linea[1:] if linea.startswith(" ") else linea
            filas.append({"tipo": "igual", "trozo": actual["indice"], "izqNum": izq, "izq": contenido, "izqTipo": "igual",
                          "derNum": der, "der": contenido, "derTipo": "igual"})
            izq += 1
            der += 1
    volcar()
    return {"cabecera": cabecera, "trozos": trozos, "filas": filas, "binario": binario, "recortado": recortado,
            "anadidas": sum(1 for f in filas if f["derTipo"] == "anadida"),
            "quitadas": sum(1 for f in filas if f["izqTipo"] == "quitada")}


def parche_de_trozo(diferencia: dict, indice: int) -> str:
    """El parche de un solo trozo (cabecera del archivo + el trozo), listo para `git apply` por la entrada estándar."""
    trozos = diferencia["trozos"]
    if not 0 <= indice < len(trozos):
        return ""
    cabecera = [l for l in diferencia["cabecera"] if l.startswith(("diff --git", "--- ", "+++ ", "new file", "deleted file",
                                                                     "old mode", "new mode", "index "))]
    t = trozos[indice]
    return "\n".join(cabecera + [t["cabecera"]] + t["lineas"]) + "\n"
