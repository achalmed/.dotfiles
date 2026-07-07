/**
 * captura_diaria.js — Macro de QuickAdd: captura universal en un DIARIO DE
 * CAPTURAS (un solo archivo por día, nunca cientos de notas sueltas).
 *
 * Flujo: atajo → cuadro de texto → Ctrl+Enter → la entrada se AÑADE al
 * final del archivo del día con su hora:
 *
 *     01 notes/00-bandeja/2026-07-06 Capturas.md
 *         ## 09:13
 *         Idea…
 *         ---
 *
 * Al día siguiente crea solo el archivo nuevo. Nunca sobrescribe: siempre
 * añade al final (orden cronológico garantizado por construcción).
 *
 * La misma macro sirve para el diario de TAREAS (05 tasks/… Tareas.md)
 * cambiando los ajustes en QuickAdd: con "Checklist" activado cada línea
 * escrita se convierte en `- [ ]`.
 *
 * Nombre de archivo fijo: referenciado por su ruta en
 * .obsidian/plugins/quickadd/data.json — no renombrar.
 * IMPORTANTE: vive en meta/quickadd/ (NO moverlo a meta/javascript/:
 * Templater carga esa carpeta y exige que todo exporte funciones; este
 * script exporta un objeto {entry, settings} para QuickAdd).
 */
module.exports = {
    entry: async (params, settings) => {
        const { app, quickAddApi } = params;
        const carpeta = (settings?.["Carpeta"] || "01 notes/00-bandeja").trim();
        const nombre = (settings?.["Nombre"] || "Capturas").trim();
        const tipo = (settings?.["Tipo"] || "capturas").trim();
        const estado = (settings?.["Estado"] || "bandeja").trim();
        const checklist = Boolean(settings?.["Checklist"]);

        const aviso = checklist
            ? "✅ Tarea(s) — una por línea. Ctrl+Enter guarda, Esc cancela."
            : "📥 Escribe. Ctrl+Enter guarda, Esc cancela.";
        const texto = (await quickAddApi.wideInputPrompt(aviso)) ?? "";
        if (!texto.trim()) return; // cancelado o vacío: no tocar nada

        const ahora = window.moment();
        const fecha = ahora.format("YYYY-MM-DD");
        const ruta = `${carpeta}/${fecha} ${nombre}.md`;

        // Cuerpo de la entrada: texto tal cual, o checklist línea a línea.
        let cuerpo = texto.trim();
        if (checklist) {
            cuerpo = cuerpo
                .split("\n")
                .map((l) => l.trim())
                .filter((l) => l.length > 0)
                .map((l) => (/^- \[.\]/.test(l) ? l : `- [ ] ${l.replace(/^[-*+]\s*/, "")}`))
                .join("\n");
        }
        const entrada = `\n## ${ahora.format("HH:mm")}\n\n${cuerpo}\n` +
            (checklist ? "" : "\n---\n");

        let archivo = app.vault.getAbstractFileByPath(ruta);
        if (!archivo) {
            // Primer uso del día: crear el diario con el frontmatter estándar
            // (mismo esquema que meta/javascript/frontmatter.js).
            if (!app.vault.getAbstractFileByPath(carpeta)) {
                await app.vault.createFolder(carpeta).catch(() => {});
            }
            const encabezado = [
                "---",
                `id: ${ahora.format("YYYYMMDDHHmmss")}`,
                `tipo: ${tipo}`,
                `estado: ${estado}`,
                `creado: ${ahora.format("YYYY-MM-DD[T]HH:mm")}`,
                "tags: []",
                "aliases: []",
                "---",
                "",
                `# ${nombre} del ${fecha}`,
                "",
            ].join("\n");
            archivo = await app.vault.create(ruta, encabezado + entrada);
        } else {
            // Días siguientes / misma jornada: SIEMPRE añadir al final.
            await app.vault.append(archivo, entrada);
        }

        const Notice = params.obsidian?.Notice ?? window.Notice;
        if (Notice) new Notice(`${checklist ? "✅" : "📥"} → ${fecha} ${nombre}`);
    },

    settings: {
        name: "captura_diaria",
        author: "Edison Achalma",
        options: {
            "Carpeta": {
                type: "text",
                defaultValue: "01 notes/00-bandeja",
                description: "Carpeta del diario de capturas.",
            },
            "Nombre": {
                type: "text",
                defaultValue: "Capturas",
                description: "Sufijo del archivo diario: 'AAAA-MM-DD <Nombre>.md'.",
            },
            "Tipo": {
                type: "text",
                defaultValue: "capturas",
                description: "Valor del campo `tipo` en el frontmatter.",
            },
            "Estado": {
                type: "text",
                defaultValue: "bandeja",
                description: "Valor del campo `estado` (bandeja = aparece en el tablero para procesar).",
            },
            "Checklist": {
                type: "checkbox",
                defaultValue: false,
                description: "Convertir cada línea en una casilla '- [ ]' (modo tareas).",
            },
        },
    },
};
