/**
 * frontmatter.js — Script de usuario de Templater (tp.user.frontmatter).
 *
 * ÚNICA FUENTE DE VERDAD del esquema de metadata del vault (instancia de
 * meta/NORMATIVA_ARCHIVOS.md §6.2 «nota del vault» y §10, desde 2026-09-13;
 * fase M3 2026-09-15). Toda plantilla genera su frontmatter llamando a este
 * script; si algún día cambias el esquema, lo cambias SOLO aquí (ver
 * meta/docs/02-metadata.md).
 *
 * Contrato: emite `id tipo titulo estado creado tags aliases AutoNoteMover`
 * y después las claves `extra` del tipo. `creado` es fecha (la hora vive en
 * `id`); la primera etiqueta es SIEMPRE el tipo (§10.4) y las demás son
 * `tema/<slug>` o `proyecto/<id>`.
 *
 * Uso desde una plantilla:
 *   <%* tR += tp.user.frontmatter(tp, {
 *     tipo: "idea",              // obligatorio: tipo de nota
 *     titulo: titulo,            // opcional: el que devolvió tp.user.titular
 *     estado: "bandeja",         // opcional: por defecto "bandeja" (ciclo §2.1)
 *     tags: ["tema/economia"],   // opcional: etiquetas además del tipo
 *     extra: { autor: "" },      // opcional: campos propios del tipo (snake_case)
 *   }); %>
 *
 * Usado por: todas las plantillas de meta/plantillas/tipos, planes y revisiones.
 */
function frontmatter(tp, opciones = {}) {
    const tipo = opciones.tipo ?? "nota";
    // YAML necesita comillas cuando el título lleva `:`, `#`, corchetes, comillas…
    const escalar = (v) => {
        v = String(v ?? "");
        return /[:#\[\]{}"'|>&*!%@`,]|^\s|\s$|^-/.test(v) || v === "" ? JSON.stringify(v) : v;
    };
    const tags = [tipo, ...(opciones.tags ?? []).filter((t) => t && t !== tipo)];
    const lineas = [
        "---",
        `id: ${tp.date.now("YYYYMMDDHHmmss")}`,
        `tipo: ${tipo}`,
        `titulo: ${escalar(opciones.titulo)}`,
        `estado: ${opciones.estado ?? "bandeja"}`,
        `creado: ${tp.date.now("YYYY-MM-DD")}`,   // fecha; la hora vive en `id` (NORMATIVA_ARCHIVOS §3)
        `tags: [${tags.join(", ")}]`,
        "aliases: []",
        // La organización manual manda: ninguna nota nacida de una plantilla
        // puede ser movida por Auto Note Mover. El archivado de notas tipadas
        // lo decide el usuario vía archivar.js al crearlas.
        "AutoNoteMover: disable",
    ];
    for (const [clave, valor] of Object.entries(opciones.extra ?? {})) {
        lineas.push(`${clave}: ${valor ?? ""}`);
    }
    lineas.push("---", "");
    return lineas.join("\n");
}
module.exports = frontmatter;
