/**
 * load-current-note.js — Macro de QuickAdd.
 *
 * Reabre la nota activa después de cargar un workspace: lee del portapapeles
 * la URI de Obsidian copiada por "Advanced URI: copy URI for current file"
 * (paso anterior de la macro) y la abre.
 *
 * Corrección: la versión original llamaba window.open(window.open(text)),
 * lo que abría la nota dos veces.
 *
 * Nombre de archivo fijo: está referenciado por su ruta en la configuración
 * de QuickAdd (.obsidian/plugins/quickadd/data.json) — no renombrar.
 */
module.exports = async () => {
    const uri = await navigator.clipboard.readText();
    window.open(uri);
};
