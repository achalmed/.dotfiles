/**
 * etiqueta_proyecto.js — Script de usuario de Templater (tp.user.etiqueta_proyecto).
 *
 * Devuelve las etiquetas #project de la nota actual (una por línea), para
 * que las notas de tarea creadas desde una selección hereden el proyecto.
 *
 * Usado por: meta/plantillas/extract bibliography task from selection.md
 * (Sustituye a projecttag.js, conservado en meta/archivo/javascript/.)
 */
function etiqueta_proyecto(tp) {
    return tp.file.tags
        .filter((etiqueta) => etiqueta.includes("#project"))
        .join("\n");
}
module.exports = etiqueta_proyecto;
