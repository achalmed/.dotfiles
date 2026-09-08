# Diagramas de arquitectura

Diagramas Archify (HTML autónomo con SVG en línea) de los sistemas de
`~/Documents`. Nada se sustituye ni se borra: cada diagrama es una **lectura**
de su sistema y se conserva por lo que aporta.

## Convención

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

Un sujeto nuevo abre carpeta propia (`02-analysis/`, `10-class/`,
`quarto-studio/`…). Un énfasis nuevo del mismo sujeto entra como hermano de los
que ya están.

## Inventario

### `ecosistema/` — el workspace `~/Documents` completo

Fuente conceptual: `meta/ARQUITECTURA.md` y `meta/DIAGNOSTICO_INTEGRAL_2026-09.md`.

| Énfasis | Título | Nodos | Aristas | `validate` showcase | `visual-check` |
|---|---|---:|---:|---|---|
| `cadena-de-lectura/` | Ecosistema ~/Documents — arquitectura | 12 | 11 | 9/9, 0 err / 0 warn | pass |
| `adquisicion-y-procedencia/` | Ecosistema ~/Documents — Edison Achalma | 12 | 13 | 9/9, 0 err / 0 warn | pass |
| `pipeline-quarto/` | Ecosistema ~/Documents | 11 | 11 | 9/9, 0 err / 0 warn | pass |
| `arquitectura-general/` | Ecosistema ~/Documents — arquitectura | 12 | 13 | 9/9, 0 err / 0 warn | pass |

### `03-writing/` — Academic Writing Framework

Fuente conceptual: `03 writing/CLAUDE.md` (reglas de arquitectura) y el propio código.

| Énfasis | Título | Nodos | Aristas | `validate` showcase | `visual-check` |
|---|---|---:|---:|---|---|
| `arquitectura-en-capas/` | Academic Writing Framework — arquitectura en capas | 12 | 12 | 9/9, 0 err / 0 warn | pass |

### `05-sgdp/` — Sistema de Gestión Documental Parlamentario

Fuente conceptual: `09 trabajo/congreso de la republica - despacho-diputado/05_sgdp/CLAUDE.md`
y el propio código (`backend/app/`, `frontend/src/`, `marco_documental/`).

| Énfasis | Título | Nodos | Aristas | `validate` showcase | `visual-check` |
|---|---|---:|---:|---|---|
| `produccion-del-documento/` | SGDP — Sistema de Gestión Documental Parlamentario | 10 | 9 | 9/9, 0 err / 0 warn | pass |

### `02-analysis/` — datafw

Fuente conceptual: el propio código (`connectors/_lib/marco.py`, `registro.py`,
`pipeline/lib_proc/fuentes.py`) y `02 analysis/CLAUDE.md`.

| Énfasis | Título | Nodos | Aristas | `validate` showcase | `visual-check` |
|---|---|---:|---:|---|---|
| `zonas-de-dependencia/` | datafw — arquitectura del framework de datos | 12 | 11 | 9/9, 0 err / 0 warn | pass |

`visual-check` = contención, legibilidad, chrome del visor y capturas en
1440×900, 1600×1000, 1920×1080 y 2048×1320, en tema claro y oscuro.

## Cuánto se solapan las cuatro lecturas del ecosistema

Nodos en común sobre 12 (11 en `pipeline-quarto`), por identificador:

|  | cadena-de-lectura | pipeline-quarto | arquitectura-general |
|---|---:|---:|---:|
| **adquisicion-y-procedencia** | 7 | 2 | 9 |
| **cadena-de-lectura** | — | 4 | 10 |
| **pipeline-quarto** | — | — | 3 |

Lectura: `arquitectura-general`, `cadena-de-lectura` y `adquisicion-y-procedencia`
son **variantes del mismo diagrama** (75–83 % de nodos compartidos entre las dos
más próximas). `pipeline-quarto` es un diagrama distinto: comparte 2–4 nodos con
las demás porque cambia de plano, del almacenamiento a la publicación.

Las cuatro se titulan «Ecosistema ~/Documents», así que el título no distingue:
distingue la carpeta. Por eso el énfasis va en el slug y no en el título.

## Qué aporta cada uno (y solo él)

- **`ecosistema/cadena-de-lectura/`** — Única que dibuja
  `scripts_for_fuentes → datafw` (`importa _lib`), que `ARQUITECTURA.md` declara
  *la única dependencia admitida* entre los dos sistemas de adquisición. Única
  que separa AWF (`03 writing`) de Academic_Class / CampusTeX (`10 Class`,
  `11 Book`) en nodos distintos.
- **`ecosistema/adquisicion-y-procedencia/`** — Única con nodo
  `Fuentes oficiales` (BCRP · INEI · MEF) y nodo `catalogo.sqlite + data/raw`:
  modela la **procedencia como almacén**, no como atributo. Única que fija la
  hora del timer (espejo diario 04:30).
- **`ecosistema/pipeline-quarto/`** — Única centrada en la publicación: separa
  `qstudio` (herramienta), `hub` (04 index) y `netlify` (despliegue) en tres
  nodos. Única con tarjeta **«Fuera del diagrama»**, que declara explícitamente
  el alcance (09 trabajo, 08 personal, prompts, bookmarks, job-hunter-pro,
  scripts_for_*).
- **`ecosistema/arquitectura-general/`** — Única que dibuja la **escritura de
  vuelta** `sync → calibre` (`ko_*` · `zot_*`) y el índice `quarto → vault`
  (`_indice/`, symlinks). Separa herramienta (`scripts_quarto_studio`) de
  artefacto (`website-achalma`).
- **`03-writing/arquitectura-en-capas/`** — Otro sujeto. Dibuja la regla 1 de
  `03 writing/CLAUDE.md` («cada capa solo mira hacia abajo y sobrescribe sin
  editar») como camino principal en serpentina: `article.cls → core/academic.cls
  → core/styles/apa + core/apa → core/config` y de vuelta `classes/*.cls →
  universities/ → covers+structures+themes → documento maestro`. Dos
  contenedores separan lo que no se edita (`core/`) de lo que se selecciona
  (`\usar…`). Abajo, la cadena real de `scripts/build.sh`: LuaLaTeX ×3 con Biber
  entre la primera y la segunda pasada.
- **`05-sgdp/produccion-del-documento/`** — Otro sujeto. Dibuja la capa web
  (FastAPI + React) **sobre** el framework LaTeX: el camino `web → API →
  generador (TipTap → .tex) → marco_documental (build.sh · LuaLaTeX) →
  documentos/SERIE-NNNN-fecha-slug`. Único que modela el **reparto del estado**
  entre Postgres (metadatos y correlativo oficial) y el disco (`.tex`, PDF,
  adjuntos), unidos por `ruta_original` — el origen de la trampa de la mudanza
  de carpeta. Dibuja también lo que entra y sale del sistema: el enlace fijo de
  Tailscale Funnel, `bookmarks/` sembrando el directorio institucional y la
  copia local en los equipos del despacho.
- **`02-analysis/zonas-de-dependencia/`** — Otro sujeto. Única que dibuja la
  **frontera de dependencias verificada en el código**: `connectors/_lib/marco.py`
  importa solo `pathlib` (contenedor «Fase 01 · adquisición (stdlib pura)»)
  mientras `pipeline/` exige pandas · numpy · scipy · statsmodels (contenedor
  «Fases 02-12»). Son dos sistemas con contratos de despliegue distintos. Dibuja
  los 26 conectores como **un** nodo sobre `connectors/_lib`, porque el mecanismo
  vive en el motor y cada institución es un `config.py`. Única que traza la regla
  0b como arista: `biblioteca Calibre → lib_proc/` (`ruta_real()` por manifiesto),
  la sola flecha que entra desde un almacén externo.

## Divergencias por resolver

Las cuatro lecturas del ecosistema no dicen lo mismo. Antes de tomar una como
canónica, resolver esto:

1. **Quién escribe en Calibre.** `cadena-de-lectura` dibuja `calibre → sync` y
   relega la escritura de vuelta a una tarjeta; `arquitectura-general` y
   `adquisicion-y-procedencia` dibujan `sync → calibre`. La segunda lectura es la
   fiel a `ARQUITECTURA.md`, que atribuye al sincronizador las «columnas
   ko_*/zot_*» como producto.
2. **Calibre → Zotero.** `arquitectura-general` lo dibuja como una sola arista
   (`.ris + espejo diario`). Son **dos mecanismos distintos**: el `.ris` de alta
   lo genera `scripts_for_fuentes/ingesta` y el espejo lo mantiene
   `script_sincronizar_zotero` (timer diario). Fundirlos pierde información.
3. **`class → hub` «publish-web.sh · hardlinks»** (solo en `pipeline-quarto`).
   `CLAUDE.md` dice que los cursos de `website-achalma/cursos/` son *una copia
   separada escrita a mano* y que unificarlos es la fase **F5** del roadmap.
   Verificar si el hardlink ya existe antes de darlo por cierto.
4. **Tipo del vault.** `database` en `pipeline-quarto` y
   `adquisicion-y-procedencia`, `frontend` en `cadena-de-lectura`. Cosmético,
   pero conviene unificarlo cuando haya un diagrama canónico.

## Regenerar o añadir uno nuevo

Desde la carpeta de la skill Archify:

```bash
node bin/archify.mjs validate architecture <ruta>/<enfasis>.archify.json --quality showcase --json
node bin/archify.mjs deliver  architecture <ruta>/<enfasis>.archify.json <ruta>/<enfasis>.html --quality showcase --json
node bin/archify.mjs visual-check <ruta>/<enfasis>.html --json
```

`deliver` congela los bytes de la especificación y devuelve SHA-256 de fuente y
artefacto. No editar el `.html` a mano: `deliver` lo sobrescribe.

Archify solo acepta `en` y `zh-CN` en `meta.locale`. Como todo esto se escribe
en español, el campo va omitido: el contenido está en español y los controles
del visor («Light», «Present», «Export», «GUIDED VIEWS») quedan en inglés. No
hay forma de traducirlos desde el spec.

> **Ojo con las ejecuciones concurrentes.** `visual-check` abre el `.html` con
> Chrome por ruta: mover o renombrar el archivo mientras corre lo rompe con
> `net::ERR_FILE_NOT_FOUND` y deja los sidecars a medias. Terminar una corrida
> antes de reorganizar.

## Versionado

`meta/docs/` es un symlink a `~/.dotfiles/meta/Documents/meta/docs`, y el repo
`ecosistema` ignora `/docs` a propósito (pertenece al vault/dotfiles). Es decir:
**estos diagramas los versiona `~/.dotfiles`, no `ecosistema`.**

`ecosistema/adquisicion-y-procedencia/` venía del commit `f9e4cfe` de la rama
`diagrama-arquitectura` del repo `ecosistema`; al moverlo aquí figura como
borrado en esa rama. El contenido sigue en su historial y en disco.

## Historial de la carpeta

- **2026-09-07.** Se añadió el sujeto `02-analysis/` con el énfasis
  `zonas-de-dependencia/`, generado desde cero contra el código de datafw.
- **2026-09-07, FD6.** Se pasó de un solo nivel (`diagramas/<enfasis>/`) a
  sujeto + énfasis, se normalizaron los nombres de archivo al de su carpeta
  (venían como `ARQUITECTURA_DIAGRAMA`, `ecosistema-arquitectura`,
  `arquitectura-ecosistema-2026-09` y `arquitectura-ecosistema`), se corrigió
  `meta.output` en los dos specs que apuntaban a archivos inexistentes y se
  regeneró `deliver` + `visual-check` en los cinco para que cada receipt apunte
  a su archivo real. Nada se borró.
  Respaldo y reversión: `meta/reparaciones/FD6_diagramas_2026-09-07/UNDO.sh`.
- **2026-09-07.** Entra el sujeto `05-sgdp/` con `produccion-del-documento/`,
  traído de `05_sgdp/docs/arquitectura-sgdp.*` (commit `b9fb271` de ese repo,
  retirado allí en `dd26bd6`). Se renombró al énfasis, se corrigió `meta.output`
  y se regeneraron `deliver` + `visual-check` en la ruta nueva.
