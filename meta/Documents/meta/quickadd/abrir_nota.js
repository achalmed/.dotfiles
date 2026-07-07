/**
 * abrir_nota.js — Macro de QuickAdd: abre una nota del vault por su ruta.
 *
 * Sirve para asignar un atajo de teclado a cualquier nota (tableros,
 * bandeja, etc.) sin plugins extra: cada choice de QuickAdd que use este
 * script define su propia "Ruta" en los ajustes de la macro.
 *
 * Nombre de archivo fijo: referenciado por su ruta en
 * .obsidian/plugins/quickadd/data.json — no renombrar.
 */
module.exports = {
    entry: async (params, settings) => {
        const ruta = (settings?.["Ruta"] || "").trim();
        if (!ruta) return;
        const archivo = params.app.vault.getAbstractFileByPath(ruta);
        if (!archivo) {
            const Notice = params.obsidian?.Notice ?? window.Notice;
            if (Notice) new Notice(`No existe: ${ruta}`);
            return;
        }
        await params.app.workspace.getLeaf(false).openFile(archivo);
    },
    settings: {
        name: "abrir_nota",
        author: "Edison Achalma",
        options: {
            "Ruta": {
                type: "text",
                defaultValue: "meta/tablero/inicio.md",
                description: "Ruta de la nota a abrir (relativa al vault).",
            },
        },
    },
};
