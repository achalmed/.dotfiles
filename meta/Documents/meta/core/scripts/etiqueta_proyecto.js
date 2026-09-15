/**
 * etiqueta_proyecto.js — Script de usuario de Templater (tp.user.etiqueta_proyecto).
 *
 * Devuelve las etiquetas de proyecto de la nota actual (`proyecto/<id>`, o el
 * histórico `project/...` del starter de Zotero), sin `#`, como lista, para que
 * las notas de tarea creadas desde una selección hereden el proyecto en su
 * `tags:` (NORMATIVA_ARCHIVOS §10.4: las etiquetas van en el frontmatter).
 *
 * Usado por: meta/plantillas/extract bibliography task from selection.md
 * (Sustituye a projecttag.js, conservado en meta/archivo/javascript/.)
 */
function etiqueta_proyecto(tp) {
    return (tp.file.tags ?? [])
        .filter((etiqueta) => /^#(proyecto|project)(\/|$)/.test(etiqueta))
        .map((etiqueta) => etiqueta.replace(/^#/, "").replace(/^project(\/|$)/, "proyecto$1"));
}
module.exports = etiqueta_proyecto;
