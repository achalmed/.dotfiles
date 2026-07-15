/**
 * archivar.js — Script de usuario de Templater (tp.user.archivar).
 *
 * Archivado CONFIRMADO de notas tipadas: muestra el destino sugerido para
 * el tipo (leído de meta/sistema/config.json → destinos) y pregunta antes
 * de mover. El usuario siempre tiene la última palabra:
 *
 *     ✅ Guardar en <sugerido>     (Enter o Esc = esta opción)
 *     📁 Elegir otra carpeta…      (lista de carpetas del vault)
 *     📥 Dejar en la bandeja
 *
 * La nota nunca vuelve a moverse sola: el frontmatter estándar incluye
 * `AutoNoteMover: disable` (ver frontmatter.js) y la autoorganización solo
 * actúa sobre la bandeja (whitelist en auto-note-mover/data.json).
 *
 * Uso desde una plantilla (después de titular y frontmatter):
 *   <%* await tp.user.archivar(tp, "investigacion"); %>
 *
 * Usado por: todas las plantillas de meta/templater/tipos (via _generador.py).
 */
async function archivar(tp, tipo) {
    const app = window.app;
    const RUTA_CONFIG = "meta/sistema/config.json";

    let config = {};
    try {
        config = JSON.parse(await app.vault.adapter.read(RUTA_CONFIG));
    } catch (e) {
        // Sin config no se mueve nada: quedarse en la bandeja es lo seguro.
        return "";
    }
    const sugerido = (config.destinos ?? {})[tipo] ?? null;
    const ocultas = config.carpetasOcultasAlElegir ?? [];

    const OTRA = "__otra__";
    const BANDEJA = "__bandeja__";
    let opciones, valores;
    if (sugerido) {
        opciones = [
            `✅ Guardar en ${sugerido}  (Enter)`,
            "📁 Elegir otra carpeta…",
            "📥 Dejar en la bandeja",
        ];
        valores = [sugerido, OTRA, BANDEJA];
    } else {
        opciones = ["📥 Dejar en la bandeja  (Enter)", "📁 Elegir otra carpeta…"];
        valores = [BANDEJA, OTRA];
    }

    // Esc = null = primera opción (la sugerida): captura sin fricción.
    let eleccion = await tp.system.suggester(opciones, valores, false, `Destino (${tipo})`);
    eleccion = eleccion ?? valores[0];

    if (eleccion === OTRA) {
        const carpetas = app.vault
            .getAllLoadedFiles()
            .filter((f) => f instanceof tp.obsidian.TFolder && f.path !== "/")
            .map((f) => f.path)
            .filter((p) => !ocultas.some((o) => p === o || p.startsWith(o + "/")))
            .sort();
        const destino = await tp.system.suggester(carpetas, carpetas, false, "Carpeta destino");
        eleccion = destino ?? BANDEJA; // Esc aquí = no mover.
    }

    if (eleccion === BANDEJA) return "";

    try {
        if (!app.vault.getAbstractFileByPath(eleccion)) {
            await app.vault.createFolder(eleccion).catch(() => {});
        }
        await tp.file.move(`${eleccion}/${tp.file.title}`);
        new tp.obsidian.Notice(`📁 → ${eleccion}`);
        return eleccion;
    } catch (e) {
        new tp.obsidian.Notice(`⚠️ No se pudo mover a ${eleccion}: queda en la bandeja.`);
        return "";
    }
}
module.exports = archivar;
