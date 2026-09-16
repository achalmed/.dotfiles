# Diagramas de arquitectura

Diagramas Archify (HTML autónomo con SVG en línea) de los sistemas de
`~/Documents`, organizados en **cinco niveles de abstracción**. Nada se
sustituye ni se borra: cada diagrama es una **lectura** de su sistema y se
conserva por lo que aporta.

> **Auditoría integral del 2026-09-08 (FD7).** Se contrastaron los siete
> diagramas existentes contra el código real (no contra la documentación) con
> cuatro barridos de verificación independientes. Se corrigieron 19 hechos, se
> resolvieron las cuatro divergencias que el README anterior dejaba abiertas y
> se añadieron los tres niveles que faltaban. Detalle en §H.
> Reversión: `meta/reparaciones/FD7_diagramas_2026-09-07/UNDO.sh`.

---

## A. Los cinco niveles

| Nivel | Pregunta que responde | Diagrama |
|---|---|---|
| **N1 Ecosistema** | ¿Qué sistemas existen y cómo se agrupan? | [`ecosistema/mapa-del-ecosistema/`](ecosistema/mapa-del-ecosistema/) |
| **N2 Arquitectura del sistema** | ¿Qué subsistemas, módulos e integraciones tiene? | las cuatro lecturas de [`ecosistema/`](ecosistema/) |
| **N3 Arquitectura interna** | ¿Cómo es por dentro cada sistema? | [`01-notes/`](01-notes/), [`02-analysis/`](02-analysis/), [`03-writing/`](03-writing/), [`05-sgdp/`](05-sgdp/), [`10-class/`](10-class/) |
| **N4 Flujos operativos** | ¿Qué pasa, paso a paso, con un documento? | [`ecosistema/metodo-documental/`](ecosistema/metodo-documental/) |
| **N5 Datos e información** | ¿De dónde viene el dato, dónde queda y qué sale? | [`ecosistema/datos-y-procedencia/`](ecosistema/datos-y-procedencia/) |

Se leen de arriba abajo: N1 dice qué hay, N2 cómo se conecta, N3 cómo funciona
por dentro, N4 qué hace una persona con ello y N5 qué queda escrito.

## Convención de carpetas

Dos niveles: **sujeto** (qué sistema se dibuja) y **énfasis** (qué lectura de
ese sistema). El nombre de archivo repite el del énfasis, para que la ruta sea
predecible sin abrir la carpeta.

```
diagramas/<sujeto>/<enfasis>/
├── <enfasis>.archify.json          fuente editable (la verdad del diagrama)
├── <enfasis>.html                  entregable autónomo
└── <enfasis>.visual-check.*        evidencia de navegador (receipt + 4 PNG + hoja de contactos)
```

El `.archify.json` es lo que se edita; el `.html` **se regenera**, nunca se
edita a mano. `meta.output` dentro del spec debe decir `<enfasis>.html`.

---

## B. Inventario

### `ecosistema/` — el workspace `~/Documents` completo

Fuente conceptual: `meta/ARQUITECTURA.md`, `meta/DIAGNOSTICO_INTEGRAL_2026-09.md`
y la verificación contra código de FD7.

| Nivel | Énfasis | Tipo | Nodos | Aristas | Qué aporta y solo él |
|---|---|---|---:|---:|---|
| N1 | [`mapa-del-ecosistema/`](ecosistema/mapa-del-ecosistema/) | architecture | 14 | 13 | Los ocho dominios A–H en una pantalla, con la cadena de conocimiento como columna vertebral y la infraestructura común separada |
| N2 | [`arquitectura-general/`](ecosistema/arquitectura-general/) | architecture | 12 | 11 | La escritura de vuelta `sync → calibre` (`ko_*` · `zot_*`) y el índice `quarto → vault`. Separa herramienta (`scripts_quarto_studio`) de artefacto (`website-achalma`) |
| N2 | [`cadena-de-lectura/`](ecosistema/cadena-de-lectura/) | architecture | 12 | 12 | Única que dibuja `scripts_for_fuentes → datafw` (`importa _lib`), la única dependencia admitida entre los dos sistemas de adquisición. Separa AWF de Academic_Class / CampusTeX |
| N2 | [`adquisicion-y-procedencia/`](ecosistema/adquisicion-y-procedencia/) | architecture | 12 | 13 | Modela la **procedencia como almacén** (`catalogo.sqlite + data/raw`), no como atributo. Fija la hora del espejo diario |
| N2 | [`pipeline-quarto/`](ecosistema/pipeline-quarto/) | architecture | 11 | 11 | Centrado en publicación: separa `qstudio` (herramienta), `hub` (04 index) y `netlify` (despliegue). Único con tarjeta **«Fuera del diagrama»**, que declara el alcance |
| N4 | [`metodo-documental/`](ecosistema/metodo-documental/) | workflow | 11 | 10 | Los diez pasos 00–09 como proceso, con la rama de excepción cuando el documento no se localiza |
| N5 | [`datos-y-procedencia/`](ecosistema/datos-y-procedencia/) | dataflow | 13 | 12 | Fuentes → adquisición → almacenes → derivados → salidas, con las claves puente y las clasificaciones de cada flujo |

### `01-notes/` — el vault de notas (N3)

Fuente: `.obsidian/app.json`, `.obsidian/plugins/auto-note-mover/` (`data.json`
y el `main.js` que lo interpreta), el connector de Zotero, `meta/consultar/config.sh`,
los manifiestos de `06 archives/` y el disco de `01 notes/`.

| Énfasis | Nodos | Aristas | Qué aporta |
|---|---:|---:|---|
| [`bandeja-y-archivo/`](01-notes/bandeja-y-archivo/) | 12 | 11 | Las **dos mitades con reglas distintas** bajo un mismo nombre: la enrutada, que un solo enrutador gobierna desde `00-bandeja/`, y la de material (`40 · 50 · 70`), 475 MB que ninguna de las 26 reglas toca. Único que dibuja el alcance real del Auto Note Mover y las dos vías por las que una nota acaba en la raíz |

### `02-analysis/` — datafw (N3)

Fuente: código de `connectors/_lib/`, `pipeline/`, `sources/` y `02 analysis/CLAUDE.md`.

| Énfasis | Nodos | Aristas | Qué aporta |
|---|---:|---:|---|
| [`zonas-de-dependencia/`](02-analysis/zonas-de-dependencia/) | 12 | 11 | La **frontera de dependencias verificada en el código**: `connectors/_lib` importa solo stdlib mientras `pipeline/` exige pandas · numpy · scipy · statsmodels · pyreadstat. Son dos sistemas con contratos de despliegue distintos |

### `03-writing/` — Academic Writing Framework (N3)

Fuente: código del framework y `03 writing/CLAUDE.md`.

| Énfasis | Nodos | Aristas | Qué aporta |
|---|---:|---:|---|
| [`arquitectura-en-capas/`](03-writing/arquitectura-en-capas/) | 12 | 12 | La regla «cada capa solo mira hacia abajo y sobrescribe sin editar» como camino en serpentina, más la cadena real de `scripts/build.sh` |

### `05-sgdp/` — Sistema de Gestión Documental Parlamentario (N3)

Fuente: `05_sgdp/CLAUDE.md` y el código (`backend/app/`, `frontend/src/`, `marco_documental/`).

| Énfasis | Nodos | Aristas | Qué aporta |
|---|---:|---:|---|
| [`produccion-del-documento/`](05-sgdp/produccion-del-documento/) | 10 | 9 | La capa web (FastAPI + React) **sobre** el framework LaTeX, y el **reparto del estado** entre Postgres (metadatos y correlativo) y el disco (`.tex`, PDF, adjuntos) |

### `10-class/` — Academic_Class_Framework (N3)

Fuente: el código del framework (`scripts/temario.py`, `publicar-web.py`,
`build.sh`, `validate.sh`), los `temario.yml` de las áreas y `10 Class/CLAUDE.md`.

| Énfasis | Nodos | Aristas | Qué aporta |
|---|---:|---:|---|
| [`curriculo-y-publicacion/`](10-class/curriculo-y-publicacion/) | 12 | 12 | El **currículo como fuente única**: `temario.yml` gobierna cinco vistas, dos de ellas fuera del repo (ficha web y temario del learning-skill). Y el único que dibuja las **dos mitades** del framework: un núcleo sin cursos dentro frente a `areas/`, 23 submódulos git |

**Estado de los doce:** `validate` 9/9 checks, composición showcase 0 errores /
0 avisos, `visual-check` `pass` en contención, legibilidad, chrome del visor y
capturas a 1440×900, 1600×1000, 1920×1080 y 2048×1320, en claro y oscuro.

---

## C. Trazabilidad entre niveles

Un elemento se sigue de un nivel al siguiente por su **nombre canónico** (§F).
Estas son las cadenas completas:

**Sistema → subsistema → módulo → componente → proceso → dato**

| N1 (dominio) | N2 (lectura del ecosistema) | N3 (interior) | N4 (proceso) | N5 (dato) |
|---|---|---|---|---|
| D · 02 analysis | `datafw · 02 analysis` | `zonas-de-dependencia` completo | — | `data/raw + catálogo` → `capas derivadas` |
| C · 03 writing | `AWF · Class · Book` | `arquitectura-en-capas` completo | paso 09 → producto | `Informes y tesis` |
| B · 10 Class | `AWF · Class · Book` | `curriculo-y-publicacion` completo | — | `temario.yml` → `04 index/cursos/` |
| E · Biblioteca | `Calibre` · `Zotero` · `KOReader` | — | pasos 00–04 | `metadata.db` · `zotero.sqlite` |
| F · Vault | `Vault Obsidian` | `bandeja-y-archivo` (01 notes) | pasos 05–07 | `Vault Obsidian` |
| A · Publicación | `website-achalma` · `scripts_quarto_studio` | — | — | `Familia Quarto` |
| G · 09 trabajo | fuera de las lecturas | `produccion-del-documento` | — | — |
| H · scripts_* | `scripts_for_calibre` · `scripts_for_fuentes` | — | comandos de cada paso | `sincronizadores` |

**Entrada → procesamiento → transformación → almacenamiento → salida**
lo dibuja N5 de izquierda a derecha en cinco etapas, y N4 lo recorre como
proceso humano.

**Usuario → interfaz → aplicación → servicio → base de datos → resultado**
solo existe completa en el SGDP (N3): `Despacho → Web SGDP → API SGDP →
PostgreSQL → documentos/`. El resto del ecosistema no tiene capa de servicio:
son herramientas de línea de comandos sobre almacenes locales.

### Dónde vive cada hecho (para no repetirlo)

Un mecanismo se dibuja **una sola vez, en el nivel que le corresponde**, y en
los demás aparece como consecuencia:

- El `.ris` de alta a Zotero y su importación manual: **N4** (paso 03). En N2 y
  N5 solo consta que Calibre y Zotero se espejan a las 04:30.
- `data/raw` como bandeja de entrada de la ingesta: **N3 datafw**. En N2 es una
  nota de tarjeta, no una arista.
- El cotejo de fichas contra el PDF por `calibre_id`: **N4**. En N5 es tarjeta.
- El orden de carga de las capas LaTeX: **N3 AWF**. En N1 y N2, un solo nodo.


### Relaciones genuinamente bidireccionales

La revisión transversal confirmó dos pares que van en ambos sentidos y que, por
eso, aparecen con direcciones opuestas en diagramas distintos **sin ser una
contradicción**:

| Par | Ida | Vuelta | Dónde se ve cada una |
|---|---|---|---|
| `scripts_for_calibre` ⇄ `Calibre` | lee `metadata.db` | escribe `ko_*` · `zot_*` | `cadena-de-lectura` dibuja las dos; las demás solo la escritura |
| `scripts_for_calibre` ⇄ `Zotero` | lee anotaciones | espeja a las 04:30 | `arquitectura-general` dibuja la lectura; `adquisicion-y-procedencia` y `cadena-de-lectura`, el espejo |
| `scripts_quarto_studio` ⇄ `Vault` | toma posts `.qmd` | escribe `_indice/` (symlinks) | `arquitectura-general` dibuja la escritura; las otras dos, la lectura |

Ninguna lectura las dibuja completas porque cargar los dos sentidos en un solo
diagrama satura el corredor. Quien necesite el par completo lo tiene aquí.

---

## D. Nomenclatura canónica

Un componente conserva **el mismo nombre, función, relación, jerarquía y
responsabilidad** en todos los diagramas. Denominación canónica y variantes que
se unificaron:

| Canónico | Variantes que aparecían | Tipo Archify |
|---|---|---|
| `02 analysis (datafw)` | `datafw · 02 analysis`, `datafw · connectors`, `datafw/connectors`, `02 analysis` | `backend` |
| `03 writing (AWF)` | `AWF · 03 writing`, `Academic_Writing_Framework`, `Frameworks LuaLaTeX` | `backend` |
| `Calibre` / `biblioteca/` | `Calibre · biblioteca/`, `biblioteca/ (Calibre)`, `biblioteca Calibre`, `Biblioteca de lectura` | `database` |
| `Zotero` | consistente | `database` |
| `KOReader` | consistente | `external` |
| `Vault Obsidian` | consistente en nombre, **no en tipo** | `database` |
| `scripts_for_calibre` | `sincronizadores` (solo en N5, por etapa) | `backend` |
| `scripts_for_fuentes` | `ingesta` (solo en N5, por etapa) | `backend` |
| `scripts_quarto_studio` | `qstudio` | `backend` |
| `04 index (website-achalma)` | `04 index · website`, `hub`, `Familia Quarto` | `frontend` |
| `core/` | consistente | `backend` |
| `meta/ (ecosistema)` | `meta/ · ecosistema`, `meta/ · doctor`, `meta/ · repo ecosistema` | `security` |

**Regla de tipos.** `database` = almacén con estado propio; `backend` =
herramienta que transforma; `frontend` = superficie que una persona abre;
`external` = fuera del workspace o que no recibe escrituras; `security` =
gobierno y auditoría; `cloud` = servicio remoto; `messagebus` = disparo
asíncrono (los timers).

**Colisión de nombres que hay que respetar.** Existen dos `core/` distintos:
`~/Documents/core/` (núcleo de las suites) y `~/Documents/meta/core/`
(configuración del vault OS). Y tres `biblioteca.py` con propósitos distintos.
Los diagramas nombran siempre el primero; el segundo no aparece.

---

## E. Diagnóstico

Lo que la auditoría encontró, por categoría. Cada punto se verificó contra el
código, no contra la documentación.

### E.1 Errores conceptuales (hechos falsos)

| # | Diagrama | Estaba mal | Es |
|---|---|---|---|
| 1 | `arquitectura-general` | Arista `datafw → Calibre` «ingesta · enlaza data/raw» | datafw **no cataloga**. Quien lee `data/raw` y escribe en Calibre es `scripts_for_fuentes/ingesta` |
| 2 | `arquitectura-general` | Arista única `Calibre → Zotero` «.ris + espejo diario» | Son **dos mecanismos**: el `.ris` lo genera la ingesta y se importa a mano; el espejo lo mantiene `script_sincronizar_zotero` a las 04:30 |
| 3 | `zonas-de-dependencia` | «cuatro capas inmutables» | Son **nueve** capas derivadas bajo `data/` |
| 4 | `zonas-de-dependencia` | «12 fases: audit → modelo» | Hay 12 fases de diseño pero **10 módulos ejecutables**; la 11 es un subcomando de `modelo/` y la 12 no tiene código |
| 5 | `zonas-de-dependencia` | `biblioteca Calibre → lib_proc` «`ruta_real()` por manifiesto» | `ruta_real()` **no lee `metadata.db`**: pasa por `scripts_for_fuentes/manifiesto` y el resolutor `core/py-common/biblioteca.py` |
| 6 | `arquitectura-en-capas` | Nodo `bib/references.bib` | `03 writing/bib/references.bib` **no existe**; cada proyecto lleva el suyo |
| 7 | `arquitectura-en-capas` | `TEXINPUTS = core/` | `build.sh` exporta la **raíz del framework** con búsqueda recursiva (`//`) |
| 8 | `arquitectura-en-capas` | Salida `build/<job>.pdf` | El PDF queda **junto al `.tex` maestro**; `03 writing/build/` está vacío |
| 9 | `arquitectura-en-capas` | `universities/unsch` | `universities/` tiene **unsch, pnp y _template** |
| 10 | `arquitectura-en-capas` | «LuaLaTeX ×3» con Biber entre pasadas | Es **pasada 1 → Biber → pasadas 2 y 3** |
| 11 | `produccion-del-documento` | Funnel «publica el sitio» | Publica el **puerto 5173** (la web); la API queda tras el proxy de Vite |
| 12 | `produccion-del-documento` | `marco_documental` como `external` sin origen | Vive **dentro del repo** `05_sgdp` y **hereda la arquitectura del AWF** |

### E.2 Divergencias entre diagramas (resueltas)

Las cuatro que el README anterior dejaba abiertas:

1. **Quién escribe en Calibre.** Ambas direcciones son reales y ninguna lectura
   las tenía completas. `scripts_for_calibre` **lee** `metadata.db` y **escribe**
   las columnas `ko_*` y `zot_*`. `cadena-de-lectura` dibujaba solo la lectura;
   ahora dibuja las dos.
2. **Calibre → Zotero.** Confirmado que son dos mecanismos distintos (E.1 #2).
   Ya no se funden en una arista.
3. **`class → hub` por hardlink.** **Confirmado que existe y ya corrió**:
   `10 Class/scripts/publicar-web.py` crea los enlaces y hay 11 archivos con
   `nlink > 1` en `04 index/cursos/`. El destino es `04 index/cursos/`, no
   `pub_*`. La duda queda cerrada; la etiqueta ahora nombra el script real.
4. **Tipo del vault.** Unificado a `database` en las cuatro lecturas (era
   `frontend` en dos de ellas). El vault es un almacén, no una interfaz.

### E.3 Elementos faltantes (añadidos)

- **No había N1**: ningún diagrama respondía «qué sistemas existen». Cuatro
  lecturas del ecosistema competían por ser el mapa general sin serlo.
- **No había N4**: el Método Documental, que es el proceso operativo central
  del workspace, no estaba dibujado en ninguna parte.
- **No había N5**: no existía una vista de datos con fuentes, transformaciones,
  almacenes y salidas.
- **Dependencia inversa no documentada**: `02 analysis/pipeline/lib_proc/fuentes.py`
  inyecta `scripts_for_fuentes/manifiesto` en `sys.path`. La dependencia entre
  los dos sistemas de adquisición es **bidireccional**, no unidireccional como
  decía `ARQUITECTURA.md`. Recogido en tarjeta de `cadena-de-lectura`.
- **Cobertura real de conectores**: `sources/` declara 40 instituciones y solo
  26 tienen conector. Recogido en tarjeta de `zonas-de-dependencia`.
- **Contracorriente `replicacion`**: `pipeline/replicacion` mueve paquetes
  **desde** Calibre **hacia** `data/raw/biblioteca`, invirtiendo el flujo
  dominante. Recogido en tarjeta de `zonas-de-dependencia`.

### E.4 Duplicidades

`arquitectura-general`, `cadena-de-lectura` y `adquisicion-y-procedencia`
comparten entre 7 y 10 nodos de 12: son **variantes del mismo diagrama N2**.
No se fusionan porque cada una aporta una arista que las demás no tienen (§B), y
porque fundirlas produciría un diagrama de más de 16 nodos que ya no cabe en una
pantalla. `pipeline-quarto` cambia de plano (publicación) y comparte solo 2–4.

La decisión es **mantenerlas como lecturas alternativas del mismo nivel** y que
el N1 nuevo asuma el papel de mapa general que ninguna de ellas cumplía.

### E.5 Problemas de organización (corregidos)

- Cinco de los siete diagramas desbordaban verticalmente la primera pantalla
  tras la corrección de contenidos. Se recortaron las tarjetas sin perder
  ningún hecho verificado.
- Las cuatro lecturas del ecosistema se titulaban casi igual («Ecosistema
  ~/Documents»), de modo que el título no distinguía. Los diagramas nuevos
  llevan el nivel en el título (`(N1)`, `(N4)`, `(N5)`).

### E.6 Riesgos detectados que NO son de diagrama

Hallazgos de la verificación que pertenecen al código, no a los diagramas. Se
dejan registrados aquí porque el doctor debería vigilarlos:

- **Dos escritores de `metadata.db` sin lock**: `script_catalogacion_biblioteca`
  y `script_metadatos_calibre` escriben con `calibredb` y nunca hacen `source`
  de `lock.sh`, contra lo que afirma `ARQUITECTURA.md`.
- **El lock falla en silencio**: `core/shell-lib/lock.sh` usa `flock -n` y ante
  contención hace `exit 0`. Un timer que colisiona no reporta nada; no hay cola.
- **`02 analysis` no usa `core/env.py`** ni tiene `suite.yml`: es el único
  sistema grande fuera del contrato de suites.
- **`cv.pdf` del sitio está huérfano**: no coincide con ningún build actual del
  CV y lleva unas seis semanas de desfase.
- **Deriva documental**: `pipeline/codegen/config.py` se declara «Fase 11»
  contra su propio `main.py`; `INTEGRACION_ECOSISTEMA.md` describe `archivar`
  en modo enlace cuando el código usa modo manifiesto desde FD4.
- **`10 Class/CLAUDE.md` cuenta mal los cursos**: dice «los **61/61** `course_*`
  cumplen el 00–09»; en disco hay **54** (`find areas -maxdepth 2 -type d -name
  'course_*'`), los 54 con `temario.yml`. El diagrama dibuja 54, no 61.
- **`01 notes/readme.md` nombra mal la bandeja**: dice que «la raíz funciona como
  bandeja de entrada»; `app.json` fija `newFileFolderPath: 01 notes/00-bandeja`
  y el enrutador excluye toda carpeta salvo esa.
- **El connector de Zotero escribe fuera del enrutador**: su formato
  «Create research note» apunta a `01 notes/{{citekey}}.md`, en la raíz, que el
  Auto Note Mover no vigila. Toda ficha importada se queda donde cae.
- **El manifiesto de reorganización quedó obsoleto**: 432 de sus 459 destinos
  bajo `01 notes` ya no existen en disco (la capa `<año>/` de `20-universidad`
  nunca se creó y la tesis acabó en `03 writing/theses/`). Sirve como historia,
  no como mapa.

---

## F. Relaciones y dependencias

Las **dependencias explícitas admitidas** entre sistemas, verificadas en código:

| Origen → Destino | Mecanismo | Dibujada en |
|---|---|---|
| `scripts_for_fuentes` → `datafw/connectors/_lib` | `sys.path`, importa `almacen`, `red`, `validacion` | N2 `cadena-de-lectura` |
| `datafw/pipeline/lib_proc` → `scripts_for_fuentes/manifiesto` | `sys.path`, resuelve `ruta_real()` | tarjeta N2 (inversa de la anterior) |
| `datafw/reportes` → `03 writing/scripts/build.sh` | ruta hermana `DATAFW_DIR.parent / "03 writing"` | N1, N2 `pipeline-quarto` |
| `10 Class` → `04 index/cursos/` | `publicar-web.py`, hardlinks | N1, N2 `pipeline-quarto` |
| `05_sgdp` → `bookmarks/` | `POST /api/directorio/importar` | N3 SGDP |
| `05_sgdp/marco_documental` → arquitectura del AWF | herencia declarada, no código compartido | N3 SGDP (tarjeta) |
| toda suite → `core/env.sh` · `core/shell-lib` | `source` | N1, N2 `arquitectura-general` |
| `meta/doctor` → todo | solo lectura | N1, N2 |

**Ciclo real que conviene conocer:** `scripts_for_fuentes` y `datafw` se
importan mutuamente. No es un ciclo de ejecución (cada import ocurre en una fase
distinta), pero sí de despliegue: si falta uno, el otro rompe.

---

## G. Arquitectura propuesta

La estructura recomendada tras la auditoría es la que ya queda aplicada:

```
diagramas/
├── ecosistema/                     el workspace completo
│   ├── mapa-del-ecosistema/        N1 · mapa general          ← entrada
│   ├── arquitectura-general/       N2 · lectura de control
│   ├── cadena-de-lectura/          N2 · lectura de dependencias
│   ├── adquisicion-y-procedencia/  N2 · lectura de procedencia
│   ├── pipeline-quarto/            N2 · lectura de publicación
│   ├── metodo-documental/          N4 · flujo operativo
│   └── datos-y-procedencia/        N5 · datos
├── 01-notes/bandeja-y-archivo/          N3 · vault de notas
├── 02-analysis/zonas-de-dependencia/    N3 · datafw
├── 03-writing/arquitectura-en-capas/    N3 · AWF
├── 05-sgdp/produccion-del-documento/    N3 · SGDP
└── 10-class/curriculo-y-publicacion/    N3 · Academic_Class
```

**Por dónde empezar a leer:** `mapa-del-ecosistema` (N1) → la lectura N2 que
interese → el N3 del sistema concreto. `metodo-documental` (N4) se lee solo,
sin contexto previo.

### Lo que falta dibujar (propuesta, no aplicado)

Sistemas reales del workspace que ningún diagrama cubre por dentro:

| Sujeto propuesto | Por qué hace falta |
|---|---|
| `04-index/` — familia Quarto | 12 sitios, 5 backends, un Excel de metadatos y un índice de symlinks. Hoy solo se ve desde fuera en `pipeline-quarto` |
| `scripts_for_calibre/` — sincronización | Siete suites, tres timers, el lock y la política de espejo. Es la pieza más automatizada y solo aparece como un nodo |
| `core/` — contrato de suites | `suite.yml`, `suites.py`, `shell-lib`, `py-common` y los generadores de índice |
| `09-trabajo/` — CIL y correo | El SGDP está dibujado; sus dos repos hermanos no |

---

## H. Cambios realizados (FD7, 2026-09-08)

| Qué estaba mal | Qué se modificó | Por qué | Relación creada / eliminada |
|---|---|---|---|
| No existía mapa general | Se creó `ecosistema/mapa-del-ecosistema/` (N1) | Cuatro lecturas competían por ese papel sin cumplirlo | 13 aristas nuevas entre dominios |
| No existía flujo operativo | Se creó `ecosistema/metodo-documental/` (N4) | El proceso central del workspace no estaba dibujado | 10 aristas nuevas; rama de excepción |
| No existía vista de datos | Se creó `ecosistema/datos-y-procedencia/` (N5) | Faltaba fuentes → almacenes → salidas con clasificaciones | 12 flujos nuevos |
| `datafw → Calibre` era falsa | Arista **eliminada**; el hecho correcto pasó a tarjeta y al N3 | datafw no cataloga | −1 arista en `arquitectura-general` |
| `.ris` y espejo fundidos | Arista reetiquetada a «espejo 04:30»; el `.ris` se dibuja en N4 | Son dos mecanismos con operadores distintos | arista conservada, semántica corregida |
| Faltaba la escritura de vuelta a Calibre | **Añadida** `sync → calibre` «escribe ko_* · zot_*» | La lectura sola no explicaba el producto del sincronizador | +1 arista en `cadena-de-lectura` |
| Vault con dos tipos distintos | Unificado a `database` | Es un almacén, no una interfaz | sin cambio de aristas |
| «cuatro capas» / «12 fases» | Corregido a nueve capas y 10 módulos | Contradecía el disco y el código | sin cambio de aristas |
| `ruta_real()` mal atribuida | Reetiquetada a «fuentes.yml → calibre_id» | No lee `metadata.db` directamente | arista conservada, origen aclarado |
| Seis hechos falsos del AWF | Nodos y etiquetas corregidos | Ninguno resistía la lectura del código | sin cambio de aristas |
| Funnel y `marco_documental` | Puerto corregido; tipo cambiado a `backend` con herencia del AWF | El Funnel publica :5173; el marco no es externo | sin cambio de aristas |
| Consulta de verificación en N4 | Arista `verificar → calibre` **eliminada** | Cruzaba dos corredores y su significado ya lo lleva el tag `calibre_id` | −1 arista |
| Cotejo `calibre → vault` en N5 | Flujo **eliminado** de N5, conservado en N4 | Compartía corredor con la nota de literatura; pertenece al nivel de proceso | −1 flujo |
| Cinco diagramas desbordaban | Tarjetas recortadas | La primera pantalla es requisito de entrega | sin cambio de aristas |

**Nada se borró del disco.** Las dos aristas y el flujo retirados son
correcciones de contenido, no pérdidas: el hecho que expresaban está en el nivel
que le corresponde o en una tarjeta.

---

## Regenerar o añadir uno nuevo

Desde la carpeta de la skill Archify:

```bash
node bin/archify.mjs validate <tipo> <ruta>/<enfasis>.archify.json --quality showcase --json
node bin/archify.mjs deliver  <tipo> <ruta>/<enfasis>.archify.json <ruta>/<enfasis>.html --quality showcase --json
node bin/archify.mjs visual-check <ruta>/<enfasis>.html --json
```

`<tipo>` es `architecture`, `workflow`, `sequence`, `dataflow` o `lifecycle`.
`deliver` congela los bytes de la especificación y devuelve SHA-256 de fuente y
artefacto. No editar el `.html` a mano: `deliver` lo sobrescribe.

Lecciones de layout de esta ronda, para no repetirlas:

- El alto es el límite real: la página entera debe caber en 900 px. Tres
  tarjetas de dos líneas es lo máximo cómodo junto a un diagrama de cinco filas.
- En `dataflow`, un flujo que cruza de fila choca con la etiqueta del flujo de
  misma fila en ese hueco. Se resuelve con `channelX` **al borde** del corredor
  (no en el centro), o quitando el flujo si su sitio es otro nivel.
- Los sublabels de nodo por encima de unos 24 caracteres rompen
  `desktop-readability` a 1440 px.

Archify solo acepta `en` y `zh-CN` en `meta.locale`. Como todo esto se escribe
en español, el campo va omitido: el contenido está en español y los controles
del visor («Light», «Present», «Export», «GUIDED VIEWS») quedan en inglés.

> **Ojo con las ejecuciones concurrentes.** `visual-check` abre el `.html` con
> Chrome por ruta: mover o renombrar el archivo mientras corre lo rompe con
> `net::ERR_FILE_NOT_FOUND` y deja los sidecars a medias. Terminar una corrida
> antes de reorganizar.

## Versionado

`meta/docs/` es un symlink a `~/.dotfiles/meta/Documents/meta/docs`, y el repo
`ecosistema` ignora `/docs` a propósito. Es decir: **estos diagramas los
versiona `~/.dotfiles`, no `ecosistema`.**

## Historial de la carpeta

- **2026-09-08.** Entra el sujeto `01-notes/` con `bandeja-y-archivo/`,
  generado contra la configuración de Obsidian y el `main.js` del Auto Note
  Mover, no contra la documentación del vault. Cierra otro hueco de §G; quedan
  tres. `validate` 9/9 y `visual-check` `pass`. Deja tres divergencias nuevas
  en §E.6, todas del vault, ninguna del diagrama.
- **2026-09-08.** Entra el sujeto `10-class/` con `curriculo-y-publicacion/`,
  generado desde cero contra el código del framework docente. Cierra el primer
  hueco que §G dejaba abierto; quedan cuatro. `validate` 9/9 y `visual-check`
  `pass`. Corrige de paso un desfase documental: `10 Class/CLAUDE.md` afirma
  «61/61 cursos» y el disco tiene **54** (§E.6).
- **2026-09-08, FD7.** Auditoría integral: verificación de los siete diagramas
  contra el código con cuatro barridos independientes; 19 hechos corregidos, las
  cuatro divergencias resueltas y tres niveles nuevos (N1, N4, N5). Los diez
  diagramas quedan con `validate` 9/9 y `visual-check` `pass`.
  Reversión: `meta/reparaciones/FD7_diagramas_2026-09-07/UNDO.sh`.
- **2026-09-07.** Se añadió el sujeto `02-analysis/` con `zonas-de-dependencia/`,
  generado desde cero contra el código de datafw.
- **2026-09-07, FD6.** Se pasó de un solo nivel a sujeto + énfasis, se
  normalizaron los nombres de archivo al de su carpeta, se corrigió `meta.output`
  en dos specs y se regeneró todo. Nada se borró.
  Reversión: `meta/reparaciones/FD6_diagramas_2026-09-07/UNDO.sh`.
- **2026-09-07.** Entra el sujeto `05-sgdp/` con `produccion-del-documento/`,
  traído de `05_sgdp/docs/arquitectura-sgdp.*`.
