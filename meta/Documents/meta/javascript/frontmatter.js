/**
 * frontmatter.js — Script de usuario de Templater (tp.user.frontmatter).
 *
 * ÚNICA FUENTE DE VERDAD del esquema de metadata del vault.
 * Toda plantilla genera su frontmatter llamando a este script; si algún
 * día cambias el esquema, lo cambias SOLO aquí (ver meta/sistema/metadata.md).
 *
 * Uso desde una plantilla:
 *   <%* tR += tp.user.frontmatter(tp, {
 *     tipo: "idea",              // obligatorio: tipo de nota
 *     estado: "bandeja",         // opcional: por defecto "bandeja"
 *     tags: ["idea"],            // opcional: etiquetas iniciales
 *     extra: { autor: "" },      // opcional: campos propios del tipo
 *   }); %>
 *
 * Usado por: todas las plantillas de meta/templater/tipos, planes y revisiones.
 */
function frontmatter(tp, opciones = {}) {
    const lineas = [
        "---",
        `id: ${tp.date.now("YYYYMMDDHHmmss")}`,
        `tipo: ${opciones.tipo ?? "nota"}`,
        `estado: ${opciones.estado ?? "bandeja"}`,
        `creado: ${tp.date.now("YYYY-MM-DD[T]HH:mm")}`,
        `tags: [${(opciones.tags ?? []).join(", ")}]`,
        "aliases: []",
    ];
    for (const [clave, valor] of Object.entries(opciones.extra ?? {})) {
        lineas.push(`${clave}: ${valor ?? ""}`);
    }
    lineas.push("---", "");
    return lineas.join("\n");
}
module.exports = frontmatter;
