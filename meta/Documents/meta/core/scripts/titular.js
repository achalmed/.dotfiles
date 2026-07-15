/**
 * titular.js — Script de usuario de Templater (tp.user.titular).
 *
 * Pide un título y renombra la nota siguiendo el ESTÁNDAR ÚNICO de nombres
 * del vault (ver meta/docs/02-metadata.md):
 *
 *     AAAA-MM-DD <Tipo> - <Título>.md      (con título)
 *     AAAA-MM-DD <Tipo> HHmm.md            (sin título / Esc)
 *
 * Ejemplos: "2026-07-06 Idea - Sistema de tareas.md",
 *           "2026-07-06 Paper - Acemoglu instituciones.md".
 *
 * Garantiza que nunca quede un archivo "Untitled" y que dos notas nunca
 * choquen de nombre (añade la hora exacta si hace falta). Devuelve el
 * título "humano" (sin fecha ni tipo) para usarlo como H1.
 *
 * Uso desde una plantilla:
 *   <%* const titulo = await tp.user.titular(tp, "Idea"); %>
 *   # 💡 <% titulo %>
 *
 * Usado por: todas las plantillas de meta/plantillas/tipos.
 */
async function titular(tp, etiqueta = "Nota") {
    const fecha = tp.date.now("YYYY-MM-DD");
    let titulo = "";
    try {
        titulo = (await tp.system.prompt(`Título (${etiqueta}) — Enter = automático`)) ?? "";
    } catch (e) {
        titulo = ""; // Esc = título automático, nunca un error.
    }
    titulo = titulo
        .replace(/[\\/:*?"<>|#^\[\]{}]/g, " ")
        .replace(/\s+/g, " ")
        .trim();

    const nombre = titulo
        ? `${fecha} ${etiqueta} - ${titulo}`
        : `${fecha} ${etiqueta} ${tp.date.now("HHmm")}`;
    try {
        await tp.file.rename(nombre);
    } catch (e) {
        // Ya existe una nota con ese nombre: añadir hora exacta.
        await tp.file.rename(`${nombre} ${tp.date.now("HHmmss")}`);
    }
    return titulo || `${etiqueta} ${tp.date.now("HHmm")}`;
}
module.exports = titular;
