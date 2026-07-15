/**
 * buscar.js — Buscador unificado de notas del vault (DataviewJS).
 *
 * Sustituye a los cuatro scripts casi idénticos del vault original
 * (search-notes.js, research-notes.js, search-research-notes.js,
 * writing-notes.js), conservados en `meta/archivo/dataview/`.
 *
 * Uso desde una nota de búsqueda:
 *
 *   ```dataviewjs
 *   await dv.view("meta/search/buscar", {
 *     fuentes: '"01 notes"',   // carpetas a consultar (sintaxis de dv.pages)
 *     detalle: true,           // true = tabla completa; false = solo títulos
 *     mensaje: "Escribe criterios para buscar…", // aviso si no hay criterios
 *   });
 *   ```
 *
 * Los criterios se escriben como campos inline en la nota que lo invoca:
 *   keyword::, author::, recipient::, title::, publication::, date::,
 *   archive::, archive-location::, note-title::, start-date::, end-date::,
 *   note-created::, note-modified::, comment::, tags::, sortby::, sortorder::
 *
 * Fechas: `YYYY-MM-DD`, `<YYYY-MM-DD` (antes de) o `>YYYY-MM-DD` (después de).
 * Etiquetas: `#tag1 #tag2` (deben estar todas en la nota).
 */

const fuentes = input?.fuentes ?? '"01 notes"';
const detalle = input?.detalle ?? false;
const mensaje = input?.mensaje ??
    "   Escribe criterios en uno o más campos para buscar notas.";

const actual = dv.current();

// ---- utilidades ------------------------------------------------------------

/** Interpreta un filtro de fecha: `YYYY-MM-DD`, `<fecha` o `>fecha`. */
function filtroFecha(valor) {
    if (!valor) return null;
    const texto = String(valor);
    const op = texto.includes("<") ? "<" : texto.includes(">") ? ">" : "=";
    const tiempo = new Date(texto.replace(/[<>]/g, "").trim()).getTime();
    return Number.isNaN(tiempo) ? null : { op, tiempo };
}

/** Compara la fecha de una página contra un filtro de filtroFecha(). */
function pasaFecha(valorPagina, filtro) {
    if (!filtro) return true;
    if (!valorPagina) return false;
    const t = new Date(String(valorPagina)).getTime();
    if (Number.isNaN(t)) return false;
    return filtro.op === "<" ? t < filtro.tiempo
         : filtro.op === ">" ? t > filtro.tiempo
         : t === filtro.tiempo;
}

/** Búsqueda de subcadena sin distinguir mayúsculas (campos de texto). */
function contiene(valorPagina, criterio) {
    if (!criterio) return true;
    return valorPagina != null &&
        valorPagina.toString().toLowerCase().includes(criterio.toLowerCase());
}

/** Verdadero si todas las etiquetas buscadas están en la página. */
function coincidenEtiquetas(buscadas, delaPagina) {
    for (const t of new Set(buscadas)) {
        if (!delaPagina.some(e => e === t) ||
            buscadas.filter(e => e === t).length >
            delaPagina.filter(e => e === t).length) return false;
    }
    return true;
}

// ---- criterios de la nota invocante ---------------------------------------

const fDate     = filtroFecha(actual.date);
const fInicio   = filtroFecha(actual["start-date"]);
const fFin      = filtroFecha(actual["end-date"]);
const fCreada   = filtroFecha(actual["note-created"]);
const fEditada  = filtroFecha(actual["note-modified"]);

const hayCriterios = Boolean(
    actual.keyword || actual.author || actual.recipient || actual.title ||
    actual.publication || actual.date || actual.archive ||
    actual["archive-location"] || actual["note-title"] ||
    actual["start-date"] || actual["end-date"] ||
    actual["note-created"] || actual["note-modified"] ||
    actual.comment || actual.tags);

if (!hayCriterios) {
    dv.paragraph(mensaje);
} else {
    const pasa = (p) =>
        contiene(p.author, actual.author) &&
        contiene(p.recipient, actual.recipient) &&
        contiene(p.title, actual.title) &&
        contiene(p.publication, actual.publication) &&
        contiene(p.archive, actual.archive) &&
        contiene(p["archive-location"], actual["archive-location"]) &&
        contiene(p.comment, actual.comment) &&
        contiene(p.file.name, actual["note-title"]) &&
        (!actual.date || pasaFecha(p.date, fDate)) &&
        (!actual["start-date"] || pasaFecha(p["start-date"], fInicio)) &&
        (!actual["end-date"] || pasaFecha(p["end-date"], fFin)) &&
        (!actual["note-created"] || pasaFecha(p.file.cday, fCreada)) &&
        (!actual["note-modified"] || pasaFecha(p.file.mday, fEditada)) &&
        (!actual.tags || coincidenEtiquetas(actual.file.tags, p.file.tags));

    // Orden: sortby:: de la nota, o fecha de modificación descendente.
    const clave = (p) => (
        { "note-created": p.file.ctime,
          "note-modified": p.file.mtime,
          "note-title": p.file.name }[actual.sortby] ?? p[actual.sortby] ?? p.file.mtime);
    const orden = actual.sortorder ?? "desc";

    let paginas = dv.pages(fuentes).where(pasa).sort(clave, orden).array();

    // El filtro por palabra clave necesita leer el contenido: solo se carga
    // el texto de las notas cuando keyword:: tiene valor.
    if (actual.keyword) {
        const clavebusq = actual.keyword.toLowerCase();
        const conContenido = await Promise.all(paginas.map(async (p) => {
            const contenido = await dv.io.load(p.file.path);
            return { p, contenido };
        }));
        paginas = conContenido
            .filter(({ p, contenido }) =>
                contenido.toLowerCase().includes(clavebusq) ||
                p.file.name.toLowerCase().includes(clavebusq))
            .map(({ p }) => p);
    }

    if (detalle) {
        dv.table(
            ["Nota", "Fecha inicio", "Fecha fin", "Autor", "Destinatario",
             "Título", "Publicación", "Fecha", "Páginas", "Archivo",
             "Ubicación", "Comentario"],
            paginas.map(p => [
                p.file.link, p["start-date"], p["end-date"], p.author,
                p.recipient, p.title, p.publication, p.date, p["page-no"],
                p.archive, p["archive-location"], p.comment]));
    } else {
        dv.table(["Nota"], paginas.map(p => [p.file.link]));
    }
}
