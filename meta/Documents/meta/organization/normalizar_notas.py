#!/usr/bin/env python3
"""meta/organization/normalizar_notas.py — normaliza las notas del vault Obsidian a la normativa de archivos (fase M3).

Objetivo: que toda nota de `01 notes`, `05 tasks`, `06 archives` y `07 diary` lleve el
  frontmatter único (`id tipo titulo estado creado tags aliases`), un nombre kebab
  `AAAA-MM-DD-titulo.md` cuando está datada, y que ningún wikilink se rompa al renombrar;
  y que los archivos de los cursos seguidos dentro del vault (`metadata.yml`, `.py`,
  `.tex`) lleven identidad en la línea 1 y nombres kebab o snake.
Método: inventaría las cuatro carpetas con las mismas reglas de recorrido que
  `core/archivos.py` (lo importa: un solo criterio); lee el frontmatter como bloques de
  texto (sin PyYAML, para no perder comentarios ni formato); infiere `tipo` y `estado`
  por las claves que la nota ya trae (Zotero, docflow, Web Clipper, kanban) y, si no,
  por carpeta; migra las claves (`title→titulo`, `created→creado`, `citekey→clave_bibtex`,
  `type→tipo_zotero`, `converter→convertidor`…); calcula el nombre nuevo; reescribe los
  `[[wikilinks]]` y las menciones del nombre en las cuatro carpetas y en `meta/tablero`.
  Simula por defecto; `--aplicar` escribe tras dejar respaldo, `UNDO.sh` y `README.md`.
Fundamento: meta/NORMATIVA_ARCHIVOS.md §1, §2.1, §4, §6.2 «nota del vault», §10, §12 (M3);
  encargo meta/reparaciones/M3-M8_encargos_2026-09-15/M3.md; decision_de_diseno.
Alternativa: un script de Templater en JS. Se descarta: corre desde la terminal, no desde
  Obsidian, y Python es el lenguaje de todas las herramientas de migración del ecosistema.
Entra: las cuatro carpetas del vault y meta/tablero (solo para wikilinks).
Sale: notas normalizadas en su sitio; `registro.json`, `README.md` y `UNDO.sh` en la
  carpeta de respaldo.
Uso: python3 meta/organization/normalizar_notas.py [--aplicar] [--carpeta "07 diary"]
       [--respaldo meta/reparaciones/M3_vault_obsidian_<sello>] [--json]
Depende de: core/env.py (DOCS_ROOT) y core/archivos.py (recorrido, familias, regex).
Límite: no toca `05 tasks/temarios cursos (generado).md` (lo migra M7),
  `05 tasks/sync-data.json`, `respaldos/`, ni los binarios y adjuntos que el validador
  trata como aviso (pdf, png, ods, xlsx, wf1…); no valida: eso es core/archivos.py.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tarfile
import unicodedata
from datetime import datetime
from pathlib import Path


def _raiz():
    for base in (Path(__file__), Path(__file__).resolve()):
        d = base.parent
        while d != d.parent:
            if (d / "core" / "env.py").is_file():
                return d
            d = d.parent
    return Path.home() / "Documents"


sys.path.insert(0, str(_raiz() / "core"))
from env import DOCS_ROOT  # noqa: E402
import archivos  # noqa: E402  (recorrido, familias y regex del validador: un solo criterio)

# --- Ámbito ------------------------------------------------------------------
CARPETAS = ["01 notes", "05 tasks", "06 archives", "07 diary"]
TABLERO = "meta/tablero"
NO_TOCAR = {"05 tasks/temarios cursos (generado).md", "05 tasks/sync-data.json"}
EXT_TEXTO = {".md", ".tex", ".py", ".r", ".txt", ".csv", ".ipynb", ".qmd", ".yml", ".yaml", ".json", ".sh"}
# artefactos y temporales que no llevan identidad y se eliminan (con respaldo): caché de Jupyter,
# un workspace de VS Code con la extensión rota y un .qmd de 0 bytes
CARPETAS_ELIMINAR = {".ipynb_checkpoints"}

# --- Vocabularios (§2.1 y catálogo de meta/docs/02-metadata.md) --------------
TIPOS_GENERADOR = {"idea", "nota", "investigacion", "proyecto", "persona", "libro", "articulo", "paper",
                   "video", "clase", "reunion", "sueno", "reflexion", "decision", "problema", "hipotesis",
                   "experimento", "aprendizaje", "error", "checklist", "objetivo", "rutina", "habito",
                   "bitacora", "tarea", "referencia"}
TIPOS = TIPOS_GENERADOR | {"lectura", "apunte", "original", "tablero", "capturas", "tareas", "plan-diario",
                           "revision-semanal", "revision-mensual", "revision-trimestral", "revision-anual"}
# tipo antiguo → (tipo del catálogo, conservar el antiguo como etiqueta porque el nuevo pierde matiz)
TIPO_ALIAS = {"apuntes_clase": ("apunte", False), "indice_curso_externo": ("apunte", True),
              "manifiesto": ("nota", True), "algun-dia": ("idea", False), "algun_dia": ("idea", False)}
ESTADOS = archivos.ESTADOS
ESTADO_MAP = {"en curso": "activo", "en-curso": "activo", "en_curso": "activo", "migrada": "borrador",
              "espera": "en_espera", "bloqueado": "en_espera", "completada": "hecho", "impartida": "hecho",
              "historico": "archivado", "legacy": "archivado", "deprecado": "retirado", "obsoleto": "retirado",
              "en_preparacion": "borrador", "planeado": "borrador", "experimental": "borrador",
              "operativa": "activo", "vigente": "activo"}
CLAVES_AJENAS = archivos.CLAVES_AJENAS
# Claves que se consumen (se migran a otra clave o al esquema base) y no se copian tal cual
RENOMBRES = {"title": "titulo", "created": "creado", "modified": "modificado", "status": "estado",
             "citekey": "clave_bibtex", "converter": "convertidor", "converted": "convertido",
             "author": "autor", "publication": "publicacion", "published": "publicado",
             "description": "descripcion", "año": "anio", "sueño_horas": "sueno_horas"}
FECHA_NOMBRE = re.compile(r"^(\d{4})[-_ ]?(\d{2})[-_ ]?(\d{2})(?!\d)")
INSTANTE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?)?")
CLAVE = re.compile(r"^([A-Za-z_][\w-]*):(.*)$")
WIKILINK = re.compile(r"(!?\[\[)([^\]|#^]+)((?:[#^][^\]|]*)?(?:\|[^\]]*)?\]\])")
EMOJI = re.compile("[\U0001F000-\U0001FFFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u2190-\u21FF\u2300-\u23FF]")
QUE_PY = {  # el «qué es» de los .py de cursos sin docstring: lo dice su nombre y su carpeta
    "main.py": "programa principal de la práctica 5 (encuestas): lee, valida, transforma, analiza y escribe",
    "_init_.py": "paquete encuestas de la práctica 5 (sic: un solo guion bajo, como lo entregó el curso)",
    "lector.py": "lectura del CSV de encuestas (práctica 5)",
    "validador.py": "validación de filas de la encuesta (práctica 5)",
    "transformador.py": "transformación y limpieza de la encuesta (práctica 5)",
    "analizador.py": "estadísticas de la encuesta (práctica 5)",
    "escritor.py": "escritura de resultados de la encuesta (práctica 5)",
    "code_minsa_analysis.py": "análisis de los datos abiertos del MINSA sobre COVID-19 (sesión 7, dataframes)",
}


# --- Utilidades --------------------------------------------------------------
def kebab(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def snake(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def sin_emoji(s):
    return re.sub(r"\s{2,}", " ", EMOJI.sub("", s)).strip().strip("*").strip()


def escalar(v):
    """Un escalar YAML sin comillas ni comentario en línea."""
    v = re.sub(r"\s+#.*$", "", v.strip())
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def yaml_escalar(v):
    """Escribe un escalar; comillas dobles solo cuando YAML las necesita."""
    v = str(v)
    if v == "":
        return '""'
    if re.search(r'[:#\[\]{}"\'|>&*!%@`,]|^\s|\s$|^-', v) or v.lower() in ("yes", "no", "true", "false", "null", "~"):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return v


def yaml_lista(items):
    return "[" + ", ".join(yaml_escalar(i) for i in items) + "]"


def fecha_de(v):
    """(AAAA-MM-DD, HHMMSS|None) de un escalar de fecha o instante; None si no lo es."""
    m = INSTANTE.match(escalar(v))
    if not m:
        return None
    try:
        datetime.strptime(m.group(1), "%Y-%m-%d")
    except ValueError:
        return None
    hora = f"{m.group(2)}{m.group(3)}{m.group(4) or '00'}" if m.group(2) else None
    return m.group(1), hora


def fecha_en_nombre(stem):
    m = FECHA_NOMBRE.match(stem)
    if not m:
        return None, stem
    f = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    try:
        datetime.strptime(f, "%Y-%m-%d")
    except ValueError:
        return None, stem
    return f, re.sub(r"^[-_ ]+", "", stem[m.end():])


def partir(texto):
    """(bloques del frontmatter | None, cuerpo). Bloque = lista de líneas; el primero lleva la clave."""
    m = re.match(r"^---[ \t]*\r?\n(?:(.*?)\r?\n)?---[ \t]*\r?\n?", texto, re.S)
    if not m:
        return None, texto
    bloques, actual = [], None
    for l in (m.group(1) or "").splitlines():
        k = CLAVE.match(l)
        if k:
            actual = [k.group(1), [l]]
            bloques.append(actual)
        elif actual is not None and l.strip():
            actual[1].append(l)
    return bloques, texto[m.end():]


def lista_de(bloque):
    """Los elementos de una lista YAML (en bloque o en flujo), limpios de comillas y de `#`."""
    lineas = bloque[1]
    primera = CLAVE.match(lineas[0]).group(2).strip()
    items = []
    if primera.startswith("["):
        # flujo: partir por comas fuera de comillas
        items = [x for x in re.findall(r'"(?:[^"\\]|\\.)*"|\'[^\']*\'|[^,\[\]]+', primera)]
    elif primera:
        items = [primera]
    for l in lineas[1:]:
        l = l.strip()
        if l.startswith("- "):
            items.append(l[2:])
    out = []
    for i in items:
        i = escalar(i).lstrip("#").strip()
        if i and i not in out:
            out.append(i)
    return out


def valor_de(bloques, clave):
    for b in bloques:
        if b[0] == clave:
            return escalar(CLAVE.match(b[1][0]).group(2))
    return None


# --- Inferencia (tabla del encargo M3 §«Qué hace», 2) -------------------------
def inferir_tipo(rel, stem, claves):
    """(tipo, motivo) por las claves que la nota ya trae y, si no, por carpeta."""
    if "kanban-plugin" in claves:
        return "tablero", "kanban-plugin"
    if "converter" in claves:
        return "original", "docflow (converter)"
    if "type" in claves or "citekey" in claves:
        return "lectura", "Zotero (type/citekey)"
    partes = rel.split("/")
    top, sub = partes[0], (partes[1] if len(partes) > 2 else "")
    if top == "07 diary":
        return ("sueno" if re.search(r"sue[nñ]o", stem) else "reflexion"), "carpeta 07 diary"
    if top == "05 tasks":
        return ("rutina" if "rutina" in (stem + claves.get("h1", "")).lower() else "tarea"), "carpeta 05 tasks"
    if top == "06 archives":
        return "nota", "carpeta 06 archives"
    if sub.startswith("00-bandeja"):
        return ("idea" if "idea" in claves.get("tags", []) else "nota"), "carpeta 00-bandeja (idea si la etiqueta lo dice)"
    if sub.startswith("10-"):
        return "investigacion", "carpeta 10-investigacion"
    if sub.startswith("20-"):
        return "clase", "carpeta 20-universidad"
    if sub.startswith("30-"):
        return ("reunion" if "reunion" in kebab(stem) else "nota"), "carpeta 30-trabajo-y-negocios"
    if sub.startswith(("40-", "50-")):
        return "apunte", "carpeta 40/50 (cursos, exámenes)"
    if sub.startswith(("60-", "70-", "80-")):
        return "referencia", "carpeta 60/70/80"
    if stem.lower().startswith("proyecto "):
        return "idea", "«proyecto … studio» de la raíz"
    return "nota", "raíz de 01 notes"


def inferir_estado(rel, tipo):
    top = rel.split("/")[0]
    if top == "07 diary":
        return "hecho"
    if top == "06 archives":
        return "archivado"
    if "/00-bandeja/" in rel:
        return "bandeja"
    return "activo"


def migrar_estado(v, tipo):
    v = v.strip().lower()
    if v in ("algun-dia", "algun_dia"):
        return "algun_dia" if tipo in ("idea", "tarea") else "en_espera"
    if v == "siguiente":
        return "siguiente" if tipo == "tarea" else "activo"
    v = ESTADO_MAP.get(v, v)
    return v if v in ESTADOS else None


# --- Nombres ------------------------------------------------------------------
def nombre_valido(nombre):
    return bool(archivos.KEBAB.match(nombre) or archivos.SNAKE.match(nombre))


def nombre_nuevo_md(p):
    if p.name in archivos.EXENTOS_MD or p.name in archivos.NOMBRES_AJENOS or p.name.endswith(".html.md"):
        return None
    fecha, resto = fecha_en_nombre(p.stem)
    if nombre_valido(p.name) and (not fecha or p.stem.startswith(fecha)):
        return None
    if fecha:
        slug = kebab(resto)
        nuevo = f"{fecha}-{slug}.md" if slug else f"{fecha}.md"
    else:
        nuevo = (kebab(p.stem) or p.stem) + ".md"
    return None if nuevo == p.name else nuevo


def nombre_nuevo_otro(p):
    """Nombre kebab (o snake, si ya lo era, o si es Python) para un archivo que A07 rechaza."""
    suf = p.suffix.lower()
    stem = p.name[: -len(p.suffix)] if p.suffix else p.name
    if suf == ".py":
        base = snake(stem)
    elif suf == ".tex":
        base = kebab(stem)
    else:
        base = stem.lower()
        if re.search(r"[^a-z0-9_]", base):
            base = kebab(base)
    nuevo = base + suf
    return None if nuevo == p.name else nuevo


def falla_a07(p, repo):
    inf = archivos.Informe()
    archivos.validar_archivo(p, repo, inf, solo={"A07"})
    return any(h[0] == "fail" for h in inf.hallazgos)


# --- La nota ------------------------------------------------------------------
class Plan:
    """Lo que se hará con un archivo: contenido nuevo, nombre nuevo, o eliminación."""

    def __init__(self, p, rel):
        self.p, self.rel = p, rel
        self.texto_nuevo = None
        self.nombre_nuevo = None
        self.eliminar = False
        self.notas = []          # decisiones tomadas, para el registro


def normalizar_nota(p, rel, texto, ids_usados):
    """Devuelve (texto nuevo, resumen) de una nota .md del vault."""
    bloques, cuerpo = partir(texto)
    fm = bloques if bloques is not None else []
    claves = {b[0]: b for b in fm}
    resumen = {"claves_migradas": [], "tipo_motivo": "", "inline_tags": []}
    stem = p.stem

    # etiquetas: las del frontmatter + las de la primera línea del cuerpo (§6.2: se retiran de ahí)
    tags = lista_de(claves["tags"]) if "tags" in claves else []
    aliases = lista_de(claves["aliases"]) if "aliases" in claves else []
    lineas = cuerpo.split("\n")
    i = 0
    while i < len(lineas) and (not lineas[i].strip() or re.match(r"^\s*(#[^\s#]+\s*)+$", lineas[i])):
        if lineas[i].strip():
            for t in re.findall(r"#([^\s#]+)", lineas[i]):
                if t not in tags:
                    tags.append(t)
                    resumen["inline_tags"].append(t)
        i += 1
    if resumen["inline_tags"]:
        cuerpo = "\n".join(lineas[i:])
        cuerpo = cuerpo.lstrip("\n")

    primera = next((l for l in cuerpo.split("\n") if l.strip()), "")
    h1 = sin_emoji(primera[2:]) if primera.startswith("# ") else ""   # solo si encabeza el cuerpo

    # tipo
    tipo_dado = valor_de(fm, "tipo")
    if tipo_dado:
        tipo, recordar = TIPO_ALIAS.get(tipo_dado, (tipo_dado, False))
        resumen["tipo_motivo"] = f"tipo ya declarado ({tipo_dado})" if tipo == tipo_dado else f"tipo `{tipo_dado}` → `{tipo}`"
        if recordar and tipo_dado not in tags:
            tags.append(tipo_dado)
    else:
        tipo, motivo = inferir_tipo(rel, stem, {**claves, "tags": tags, "h1": h1})
        resumen["tipo_motivo"] = motivo
    if tipo not in TIPOS:
        resumen["tipo_motivo"] += f" (⚠ `{tipo}` no está en el catálogo)"

    # estado
    estado_dado = valor_de(fm, "estado") or valor_de(fm, "status")
    estado = migrar_estado(estado_dado, tipo) if estado_dado else None
    if estado is None:
        estado = inferir_estado(rel, tipo)
        if estado_dado:
            resumen["claves_migradas"].append(f"estado `{estado_dado}` no reconocido → `{estado}`")
    elif estado != estado_dado:
        resumen["claves_migradas"].append(f"estado `{estado_dado}` → `{estado}`")

    # creado e id
    es_zotero = "type" in claves or "citekey" in claves
    candidatos = []
    fecha_nombre, _ = fecha_en_nombre(stem)
    if fecha_nombre:
        candidatos.append((fecha_nombre, None, "nombre"))
    for k in ("creado", "created", "fecha", "fecha_inicio") + (() if es_zotero else ("date",)):
        v = valor_de(fm, k)
        f = fecha_de(v) if v else None
        if f:
            candidatos.append((f[0], f[1], k))
    mtime = datetime.fromtimestamp(p.stat().st_mtime)
    if not candidatos:
        candidatos.append((mtime.strftime("%Y-%m-%d"), mtime.strftime("%H%M%S"), "mtime"))
    creado = candidatos[0][0]
    resumen["creado_fuente"] = candidatos[0][2]
    id_dado = valor_de(fm, "id")
    if id_dado and re.fullmatch(r"\d{14}", id_dado):
        nid = id_dado
    else:
        hora = next((c[1] for c in candidatos if c[0] == creado and c[1]), "000000")
        nid = creado.replace("-", "") + hora
        while nid in ids_usados:
            nid = str(int(nid) + 1)
        resumen["claves_migradas"].append(f"id nuevo {nid} (de {candidatos[0][2]})")
    ids_usados.add(nid)

    # titulo
    titulo_dado = valor_de(fm, "titulo") or valor_de(fm, "title") or ""
    if titulo_dado and titulo_dado.lower() not in (stem.lower(), "index"):
        titulo, tf = titulo_dado, "titulo/title"
    elif h1 and h1.lower() != stem.lower():
        titulo, tf = h1, "H1"
    elif titulo_dado and titulo_dado.lower() != "index":
        titulo, tf = titulo_dado, "title"
    elif stem.lower() == "index":
        _, abuelo = fecha_en_nombre(p.parent.parent.name)
        titulo, tf = f"{p.parent.name} · {abuelo.replace('-', ' ')}", "carpeta"
    else:
        _, resto = fecha_en_nombre(stem)
        titulo, tf = re.sub(r"[-_]+", " ", resto).strip() or stem, "nombre"
    resumen["titulo_fuente"] = tf

    # el resto de claves: renombradas a snake_case, valores de fecha normalizados
    resto = []
    consumidas = {"id", "tipo", "titulo", "title", "estado", "status", "creado", "created", "tags", "aliases",
                  "AutoNoteMover"}
    if not es_zotero:
        consumidas.add("date")   # ya migró a creado (fecha de la nota)
    for b in fm:
        k = b[0]
        if k in consumidas:
            continue
        v_raw = CLAVE.match(b[1][0]).group(2)
        v = escalar(v_raw)
        nk = RENOMBRES.get(k, k)
        if k == "type" and es_zotero:
            nk = "tipo_zotero"
        elif k == "date" and es_zotero:
            nk = "publicado"
        elif k == "source":
            if "converter" in claves:
                nk = "origen"
            elif v == "":
                resumen["claves_migradas"].append("source vacío: se retira")
                continue
            else:
                nk = "url" if re.match(r"https?://", v) else "origen"
        elif k in ("author", "published", "description") and v == "" and len(b[1]) == 1:
            resumen["claves_migradas"].append(f"{k} vacío: se retira")
            continue
        if nk not in CLAVES_AJENAS:
            nk = re.sub(r"-", "_", nk)
        linea = f"{nk}:{v_raw}"
        if nk in ("convertido", "modificado", "publicado", "fecha") and v:
            f = fecha_de(v)
            if f:
                v = f[0] if nk in ("publicado", "fecha") or not f[1] else f"{f[0]}T{f[1][:2]}:{f[1][2:4]}:{f[1][4:6]}"
                linea = f"{nk}: {v}"
        if nk != k:
            resumen["claves_migradas"].append(f"{k} → {nk}")
        resto.append([nk, [linea] + b[1][1:]])

    # etiquetas: la primera es el tipo (§10.4)
    tags = [tipo] + [t for t in tags if t != tipo]
    nuevo_nombre = nombre_nuevo_md(p)
    if nuevo_nombre and stem not in aliases:
        aliases.append(stem)

    fm_lineas = ["---", f"id: {nid}", f"tipo: {tipo}", f"titulo: {yaml_escalar(titulo)}", f"estado: {estado}",
                 f"creado: {creado}", f"tags: {yaml_lista(tags)}", f"aliases: {yaml_lista(aliases)}"]
    if "AutoNoteMover" in claves:
        fm_lineas.append(claves["AutoNoteMover"][1][0].strip())
    for b in resto:
        fm_lineas.extend(b[1])
    fm_lineas.append("---")
    texto_nuevo = "\n".join(fm_lineas) + "\n" + (cuerpo if bloques is not None or cuerpo.startswith("\n") else cuerpo)
    if bloques is None and not cuerpo.startswith("\n"):
        texto_nuevo = "\n".join(fm_lineas) + "\n" + cuerpo
    resumen.update({"id": nid, "tipo": tipo, "estado": estado, "creado": creado, "titulo": titulo,
                    "tags": tags, "nombre_nuevo": nuevo_nombre})
    return texto_nuevo, resumen


# --- Archivos de cursos dentro del vault (encargo M3 §«Qué hace», 5) -----------
def ruta_declarable(rel):
    """El sufijo más largo de la ruta (bajo la carpeta del vault) sin espacios: el validador
    lee la identidad con `[^\\s]+` y `01 notes/…` no la satisface; A02 acepta un sufijo."""
    partes = rel.split("/")[1:]
    for i in range(len(partes)):
        if all(" " not in x for x in partes[i:]):
            return "/".join(partes[i:])
    return partes[-1]


def normalizar_metadata_yml(p, rel, texto):
    lineas = texto.split("\n")
    titulo = escalar(next((l.split(":", 1)[1] for l in lineas if l.startswith("titulo:")), "sesión"))
    numero = escalar(next((l.split(":", 1)[1] for l in lineas if l.startswith("numero:")), ""))
    curso = rel.split("/")[2] if rel.count("/") >= 3 else p.parent.name
    identidad = f"# {ruta_declarable(rel)} — sesión {numero} «{titulo}» del curso {curso}"
    out = []
    for l in lineas:
        if l.startswith("slug:"):
            l = "id:" + l[5:]
        elif re.match(r"^estado:\s*migrada\s*$", l):
            l = "estado: borrador"
        out.append(l)
    if not re.match(r"^#\s*\S+\s+—\s+", out[0]):
        out.insert(0, identidad)
    return "\n".join(out)


def normalizar_py(p, rel, texto, nombre_final):
    cuerpo = texto.split("\n", 1)[1] if texto.startswith("#!") else texto
    cuerpo_sin = re.sub(r"^(\s*#[^\n]*\n)+", "", cuerpo)
    if re.match(r'^\s*(?:r?"""|\'\'\')', cuerpo_sin):
        return None                                   # ya tiene docstring
    que = QUE_PY.get(nombre_final, f"material de la sesión {p.parent.parent.name} del curso")
    rel_final = ruta_declarable(rel[: -len(p.name)] + nombre_final)
    doc = f'"""{rel_final} — {que}."""\n'
    if texto.startswith("#!"):
        sb, resto = texto.split("\n", 1)
        return sb + "\n" + doc + resto
    return doc + texto


def normalizar_tex(p, rel, texto, nombre_final):
    lineas = texto.split("\n")
    rel_final = ruta_declarable(rel[: -len(p.name)] + nombre_final)
    cambiado = False
    identidad = re.compile(r"^%+\s{1,3}\S+\s+—\s+")
    tiene = any(identidad.match(l) for l in lineas[:4])      # el validador mira las 4 primeras
    # sándwich existente sin identidad: la línea 2 pasa a `%  ruta — descripción`
    if tiene:
        pass
    elif re.match(r"^%+\s*=+\s*$", lineas[0]) and len(lineas) > 1 and re.match(r"^%\s+\S", lineas[1]):
        lineas[1] = f"%  {rel_final} — " + re.sub(r"^%\s+", "", lineas[1])
        cambiado = True
    else:
        m = re.search(r"\\title\{([^}]*)\}", texto)
        que = sin_emoji(re.sub(r"\\\\|\\[a-zA-Z]+\{?|\}", " ", m.group(1))) if m else \
            re.sub(r"[-_]+", " ", p.stem)
        lineas.insert(0, f"%% {rel_final} — {que}")
        cambiado = True
    # separadores Unicode → ASCII (§9.3)
    for i, l in enumerate(lineas):
        m = re.match(r"^(\s*%+)\s*[─═]{2,}\s*(.*?)\s*[─═]*\s*$", l)
        if m:
            pre, tit = m.group(1), m.group(2)
            lineas[i] = (f"{pre} --- {tit} " if tit else f"{pre} ").ljust(77, "-")
            cambiado = True
    return "\n".join(lineas) if cambiado else None


# --- Recorrido y enlaces ------------------------------------------------------
def recorrer(carpeta):
    for p in archivos.recorrer(DOCS_ROOT / carpeta):
        yield p, p.relative_to(DOCS_ROOT).as_posix()


def es_texto(p):
    return p.suffix.lower() in EXT_TEXTO


def indice_nombres(extra=()):
    nombres = set()
    for c in CARPETAS + ["meta"]:
        for raiz, _, archs in os.walk(DOCS_ROOT / c, followlinks=True):
            for a in archs:
                nombres.add(a.lower())
                if a.lower().endswith(".md"):
                    nombres.add(a[:-3].lower())
    nombres.update(x.lower() for x in extra)
    return nombres


def enlaces_rotos(textos, nombres):
    """Wikilinks de `textos` (ruta → texto) cuyo destino no es ningún archivo de `nombres`."""
    rotos = []
    for ruta, t in textos.items():
        for m in WIKILINK.finditer(t):
            destino = m.group(2).strip()
            base = destino.rpartition("/")[2].strip().lower()
            if base and base not in nombres and base + ".md" not in nombres:
                rotos.append((ruta, destino))
    return rotos


def reescribir_enlaces(texto, mapa_md, mapa_otros):
    def sust(m):
        destino = m.group(2)
        dirpart, sep, base = destino.rpartition("/")
        b = base.strip().lower()
        nuevo = None
        if b in mapa_md:
            nuevo = mapa_md[b]
        elif b.endswith(".md") and b[:-3] in mapa_md:
            nuevo = mapa_md[b[:-3]] + ".md"
        elif b in mapa_otros:
            nuevo = mapa_otros[b]
        if nuevo is None:
            return m.group(0)
        return m.group(1) + dirpart + sep + nuevo + m.group(3)
    return WIKILINK.sub(sust, texto)


# --- Orquestación -------------------------------------------------------------
def planificar(carpetas):
    repo = archivos.raiz_repo(DOCS_ROOT)
    planes = {}
    ids_usados = set()
    registro = {"notas": {}, "renombres": {}, "eliminados": [], "cursos": [], "enlaces_reescritos": {}}
    # primero los id existentes, para no chocar con ellos
    for c in carpetas:
        for p, rel in recorrer(c):
            if p.suffix == ".md" and rel not in NO_TOCAR:
                lineas = archivos.leer(p)
                fmv = archivos.frontmatter(lineas) or {}
                if re.fullmatch(r"\d{14}", fmv.get("id", "")):
                    ids_usados.add(fmv["id"])
    for c in carpetas:
        for p, rel in recorrer(c):
            if rel in NO_TOCAR or ".ipynb_checkpoints" in rel:
                continue
            plan = Plan(p, rel)
            fam = archivos.familia(p)
            if fam == "markdown" and p.name not in archivos.EXENTOS_MD and not p.name.endswith(".html.md"):
                texto = archivos.leer_todo(p)
                nuevo, resumen = normalizar_nota(p, rel, texto, ids_usados)
                if nuevo != texto:
                    plan.texto_nuevo = nuevo
                plan.nombre_nuevo = resumen.pop("nombre_nuevo")
                registro["notas"][rel] = resumen
            elif fam == "yaml" and p.name == "metadata.yml":
                texto = archivos.leer_todo(p)
                nuevo = normalizar_metadata_yml(p, rel, texto)
                if nuevo != texto:
                    plan.texto_nuevo = nuevo
                    registro["cursos"].append(rel)
            elif fam == "quarto" and p.stat().st_size == 0:
                plan.eliminar = True
                plan.notas.append("qmd de 0 bytes: sin identidad posible; se elimina con respaldo")
            elif p.suffix == ".code workspace" or p.name.endswith(".code workspace"):
                plan.eliminar = True
                plan.notas.append("workspace de VS Code con extensión rota: temporal; se elimina con respaldo")
            if not plan.eliminar and plan.nombre_nuevo is None and fam != "markdown" and falla_a07(p, repo):
                plan.nombre_nuevo = nombre_nuevo_otro(p)
            nombre_final = plan.nombre_nuevo or p.name
            if fam == "python" and not plan.eliminar:
                texto = plan.texto_nuevo or archivos.leer_todo(p)
                nuevo = normalizar_py(p, rel, texto, nombre_final)
                if nuevo:
                    plan.texto_nuevo = nuevo
                    registro["cursos"].append(rel)
            elif fam == "latex" and not plan.eliminar:
                texto = plan.texto_nuevo or archivos.leer_todo(p)
                nuevo = normalizar_tex(p, rel, texto, nombre_final)
                if nuevo:
                    plan.texto_nuevo = nuevo
                    registro["cursos"].append(rel)
            if plan.texto_nuevo is not None or plan.nombre_nuevo or plan.eliminar:
                planes[rel] = plan
    # cachés de Jupyter: carpetas enteras
    for c in carpetas:
        for raiz, dirs, _ in os.walk(DOCS_ROOT / c):
            for d in list(dirs):
                if d in CARPETAS_ELIMINAR:
                    rel = (Path(raiz) / d).relative_to(DOCS_ROOT).as_posix()
                    plan = Plan(Path(raiz) / d, rel)
                    plan.eliminar = True
                    plan.notas.append("caché de Jupyter (artefacto): se elimina con respaldo")
                    planes[rel] = plan
                    dirs.remove(d)
    # mapas de renombre
    mapa_md, mapa_otros = {}, {}
    for rel, plan in planes.items():
        if plan.nombre_nuevo:
            registro["renombres"][rel] = rel[: -len(plan.p.name)] + plan.nombre_nuevo
            if plan.p.suffix == ".md":
                mapa_md[plan.p.stem.lower()] = plan.nombre_nuevo[:-3]
            else:
                mapa_otros[plan.p.name.lower()] = plan.nombre_nuevo
        if plan.eliminar:
            registro["eliminados"].append(rel)
    # wikilinks y menciones, en las cuatro carpetas y en meta/tablero
    ambito = [(p, p.relative_to(DOCS_ROOT).as_posix()) for c in carpetas for p, _ in recorrer(c)]
    ambito += [(p, p.relative_to(DOCS_ROOT).as_posix()) for p in sorted((DOCS_ROOT / TABLERO).glob("*.md"))]
    textos_antes, textos_despues = {}, {}
    for p, rel in ambito:
        if rel in NO_TOCAR or not es_texto(p) or (rel in planes and planes[rel].eliminar):
            continue
        original = archivos.leer_todo(p)
        actual = planes[rel].texto_nuevo if rel in planes and planes[rel].texto_nuevo is not None else original
        nuevo = reescribir_enlaces(actual, mapa_md, mapa_otros)
        top = rel.split("/")[0]
        for viejo, nuevo_n in mapa_otros.items():
            if viejo in nuevo.lower():
                nuevo = re.sub(re.escape(viejo), nuevo_n, nuevo, flags=re.I)
        if nuevo != actual:
            planes.setdefault(rel, Plan(p, rel)).texto_nuevo = nuevo
            registro["enlaces_reescritos"][rel] = registro["enlaces_reescritos"].get(rel, 0) + 1
        if p.suffix == ".md":
            textos_antes[rel] = original
            textos_despues[registro["renombres"].get(rel, rel)] = nuevo
    nombres_antes = indice_nombres()
    nombres_despues = (nombres_antes - {Path(r).name.lower() for r in registro["renombres"]}
                       - {Path(r).stem.lower() for r in registro["renombres"] if r.endswith(".md")}
                       - {Path(r).name.lower() for r in registro["eliminados"]})
    nombres_despues |= {Path(n).name.lower() for n in registro["renombres"].values()}
    nombres_despues |= {Path(n).stem.lower() for n in registro["renombres"].values() if n.endswith(".md")}
    registro["enlaces_rotos_antes"] = enlaces_rotos(textos_antes, nombres_antes)
    registro["enlaces_rotos_despues"] = enlaces_rotos(textos_despues, nombres_despues)
    return planes, registro


def respaldar(planes, destino, sello):
    destino.mkdir(parents=True, exist_ok=True)
    tarball = destino / f"backup_{sello}.tar.gz"
    with tarfile.open(tarball, "w:gz") as tar:
        for rel, plan in sorted(planes.items()):
            tar.add(plan.p, arcname=rel)
    return tarball


def escribir_undo(planes, destino, tarball):
    nuevos = [rel[: -len(plan.p.name)] + plan.nombre_nuevo for rel, plan in planes.items() if plan.nombre_nuevo]
    lineas = ["#!/usr/bin/env bash",
              f"# {destino.name}/UNDO.sh — deshace la fase M3 (vault Obsidian): borra los nombres nuevos y",
              "# restaura desde el tarball los originales (editados, renombrados y eliminados).",
              "set -euo pipefail",
              f'ROOT="{DOCS_ROOT}"',
              'cd "$ROOT"'] + [f"rm -f -- {json.dumps(n)}" for n in sorted(nuevos)] + \
             [f'tar -xzf "{tarball}" -C "$ROOT"', 'echo "M3 deshecha: originales restaurados."']
    (destino / "UNDO.sh").write_text("\n".join(lineas) + "\n")
    os.chmod(destino / "UNDO.sh", 0o755)


def aplicar(planes):
    hechos = {"escritos": 0, "renombrados": 0, "eliminados": 0}
    for rel, plan in sorted(planes.items(), key=lambda x: -len(x[0])):
        if plan.eliminar:
            if plan.p.is_dir():
                shutil.rmtree(plan.p)
            else:
                plan.p.unlink()
            hechos["eliminados"] += 1
            continue
        if plan.texto_nuevo is not None:
            plan.p.write_text(plan.texto_nuevo, encoding="utf-8")
            hechos["escritos"] += 1
        if plan.nombre_nuevo:
            destino = plan.p.with_name(plan.nombre_nuevo)
            if destino.exists():
                raise SystemExit(f"colisión: {destino} ya existe (no se aplica {rel})")
            plan.p.rename(destino)
            hechos["renombrados"] += 1
    return hechos


def informe(planes, registro, aplicado):
    n_notas = len(registro["notas"])
    print(f"{'APLICADO' if aplicado else 'SIMULACIÓN'} — {n_notas} notas .md revisadas · "
          f"{sum(1 for p in planes.values() if p.texto_nuevo is not None)} archivos con contenido nuevo · "
          f"{len(registro['renombres'])} renombres · {len(registro['eliminados'])} eliminaciones · "
          f"{len(registro['cursos'])} archivos de cursos con identidad")
    print(f"wikilinks rotos: antes {len(registro['enlaces_rotos_antes'])} · después {len(registro['enlaces_rotos_despues'])}")
    for rel, nuevo in sorted(registro["renombres"].items()):
        print(f"  mv  {rel}\n   →  {nuevo}")
    for rel in registro["eliminados"]:
        print(f"  rm  {rel}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--aplicar", action="store_true", help="escribe (por defecto solo simula)")
    ap.add_argument("--carpeta", action="append", help="limitar a una carpeta del vault (repetible)")
    ap.add_argument("--respaldo", help="carpeta de reparación donde dejar tarball, UNDO.sh y registro")
    ap.add_argument("--json", action="store_true", help="imprime el registro completo en JSON")
    a = ap.parse_args()
    carpetas = a.carpeta or CARPETAS
    for c in carpetas:
        if c not in CARPETAS:
            ap.error(f"carpeta fuera del vault: {c}")
    planes, registro = planificar(carpetas)
    sello = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if a.aplicar:
        destino = Path(a.respaldo) if a.respaldo else DOCS_ROOT / "meta" / "reparaciones" / f"M3_vault_obsidian_{sello}"
        if not destino.is_absolute():
            destino = DOCS_ROOT / destino
        tarball = respaldar(planes, destino, sello)
        escribir_undo(planes, destino, tarball)
        registro["hechos"] = aplicar(planes)
        registro["respaldo"] = str(tarball)
        (destino / "registro.json").write_text(json.dumps(registro, ensure_ascii=False, indent=1))
    informe(planes, registro, a.aplicar)
    if a.json:
        print(json.dumps(registro, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
