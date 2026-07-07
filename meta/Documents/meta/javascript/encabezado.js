/**
 * encabezado.js — Script de usuario de Templater (tp.user.encabezado).
 *
 * Al extraer una anotación de Zotero hacia una nota nueva, copia el
 * encabezado (frontmatter + sección "### Note") de la nota de investigación
 * actual y actualiza el campo `page-no::` con la página de la anotación
 * seleccionada (tomada del parámetro `?page=` del enlace de Zotero).
 *
 * Usado por: meta/templater/extract research note from selection.md
 * (Sustituye a header.js, conservado en meta/archivo/javascript/.)
 */
function encabezado(tp) {
    const contenido = tp.file.content;
    const seleccion = tp.file.selection();

    // Encabezado = todo hasta el final de la línea "### Note".
    const cabecera = contenido.substring(0, contenido.indexOf("### Note") + 10);

    // Página anotada, extraída del enlace de Zotero (…?page=N&annotation=…).
    const pagina = seleccion.substring(
        seleccion.indexOf("?page=") + 6,
        seleccion.indexOf("&annotation"));

    // Reemplaza el valor anterior de page-no:: por el de la selección.
    const inicio = cabecera.indexOf("page-no:: ") + 10;
    const paginaAnterior = cabecera.substring(
        inicio, cabecera.indexOf("\n", inicio));

    return cabecera.replace(
        "page-no:: " + paginaAnterior + "\n",
        "page-no:: " + pagina + "\n");
}
module.exports = encabezado;
