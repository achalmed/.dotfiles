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
 * cambiando los ajustes en QuickAdd: con "Checklist" cada línea se vuelve
 * `- [ ]`, y además:
 *
 *  - "Asistente": tras escribir, selectores rápidos de Estado / Prioridad /
 *    Urgencia / Tipo (Esc = por defecto, sin fricción) y la pregunta
 *    "¿pertenece a una tarea existente?" (nueva / subtarea / añadir detalle /
 *    relacionar) con la lista de tareas abiertas — sin escribir IDs jamás.
 *    Se guardan como campos inline de Dataview: [prioridad:: alta] …
 *    Opciones y valores: meta/sistema/config.json → tareas.
 *
 *  - "Arrastre": al crear el diario de un día nuevo, las `- [ ]` pendientes
 *    del diario anterior se copian bajo "## ⏭️ Arrastradas de <fecha>"
 *    (conservando estado, campos y sangría) y en el archivo viejo quedan
 *    marcadas `- [>]` para que no haya duplicados en los tableros.
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
        const asistente = Boolean(settings?.["Asistente"]);
        const arrastre = Boolean(settings?.["Arrastre"]);
        const Notice = params.obsidian?.Notice ?? window.Notice;
        const avisar = (msg) => { if (Notice) new Notice(msg); };

        // Configuración central (opcional: sin ella todo sigue funcionando).
        let config = {};
        try {
            config = JSON.parse(await app.vault.adapter.read("meta/sistema/config.json"));
        } catch (e) { /* sin config → valores por defecto */ }

        const aviso = checklist
            ? "✅ Tarea(s) — una por línea. Ctrl+Enter guarda, Esc cancela."
            : "📥 Escribe. Ctrl+Enter guarda, Esc cancela.";
        const texto = (await quickAddApi.wideInputPrompt(aviso)) ?? "";
        if (!texto.trim()) return; // cancelado o vacío: no tocar nada

        const ahora = window.moment();
        const fecha = ahora.format("YYYY-MM-DD");
        const ruta = `${carpeta}/${fecha} ${nombre}.md`;
        const reDiario = new RegExp(`^(\\d{4}-\\d{2}-\\d{2}) ${nombre}\\.md$`);

        // Un suggester que NUNCA rompe la captura: Esc = valor por defecto.
        const elegir = async (opciones) => {
            if (!Array.isArray(opciones) || opciones.length === 0) return "";
            try {
                const r = await quickAddApi.suggester(
                    opciones.map((o) => o.etiqueta),
                    opciones.map((o) => o.valor)
                );
                return r ?? "";
            } catch (e) {
                return "";
            }
        };

        // ——— Cuerpo de la entrada ———
        let lineas = texto
            .trim()
            .split("\n")
            .map((l) => l.trim())
            .filter((l) => l.length > 0);

        let marcado = "- [ ] ";
        let campos = "";

        if (checklist && asistente) {
            const t = config.tareas ?? {};
            const estadoT = await elegir(t.estados);
            const prioridad = await elegir(t.prioridades);
            const urgencia = await elegir(t.urgencias);
            const tipoT = await elegir(t.tipos);
            if (estadoT === "completada") marcado = "- [x] ";
            else if (estadoT) campos += ` [estado:: ${estadoT}]`;
            if (prioridad) campos += ` [prioridad:: ${prioridad}]`;
            if (urgencia) campos += ` [urgencia:: ${urgencia}]`;
            if (tipoT) campos += ` [tipo:: ${tipoT}]`;
        }

        const aChecklist = (l, sangria = "") =>
            /^- \[.\]/.test(l)
                ? sangria + l + campos
                : sangria + marcado + l.replace(/^[-*+]\s*/, "") + campos;

        // ——— ¿Pertenece a una tarea existente? (solo modo asistente) ———
        if (checklist && asistente) {
            const abiertas = [];
            try {
                const dias = config.tareas?.diasBusquedaRelacion ?? 14;
                const limite = window.moment().subtract(dias, "days").format("YYYY-MM-DD");
                const diarios = app.vault
                    .getMarkdownFiles()
                    .filter((f) => f.parent?.path === carpeta && reDiario.test(f.name))
                    .filter((f) => f.name.slice(0, 10) >= limite)
                    .sort((a, b) => b.name.localeCompare(a.name));
                for (const f of diarios) {
                    const contenido = await app.vault.cachedRead(f);
                    for (const linea of contenido.split("\n")) {
                        const m = linea.match(/^(\s*)- \[ \] (.*)$/);
                        if (m) abiertas.push({ archivo: f, linea, sangria: m[1], texto: m[2] });
                    }
                }
            } catch (e) { /* sin tareas abiertas: seguir como nueva */ }

            if (abiertas.length > 0) {
                const modo = (await elegir([
                    { etiqueta: "🆕 Tarea nueva (Enter)", valor: "nueva" },
                    { etiqueta: "📎 Subtarea de una existente…", valor: "subtarea" },
                    { etiqueta: "➕ Añadir detalle a una existente…", valor: "anadir" },
                    { etiqueta: "🔗 Relacionar con una existente…", valor: "relacionar" },
                ])) || "nueva";

                let padre = null;
                if (modo !== "nueva") {
                    const limpiar = (s) => s.replace(/\[[^\]]*::[^\]]*\]/g, "").replace(/\s+/g, " ").trim();
                    try {
                        const i = await quickAddApi.suggester(
                            abiertas.map((a) => `${limpiar(a.texto)}   · ${a.archivo.basename}`),
                            abiertas.map((_, i) => i)
                        );
                        if (i != null) padre = abiertas[i];
                    } catch (e) { /* Esc: sigue como nueva */ }
                }

                if (padre && (modo === "subtarea" || modo === "anadir")) {
                    // Insertar bajo la tarea elegida, en SU archivo, con sangría.
                    const sangria = padre.sangria + "    ";
                    const bloque = lineas
                        .map((l) => modo === "subtarea" ? aChecklist(l, sangria) : `${sangria}- ${l.replace(/^[-*+]\s*/, "")}`)
                        .join("\n");
                    await app.vault.process(padre.archivo, (data) => {
                        const arr = data.split("\n");
                        const idx = arr.indexOf(padre.linea);
                        if (idx === -1) return data; // la línea cambió: no tocar
                        arr.splice(idx + 1, 0, ...bloque.split("\n"));
                        return arr.join("\n");
                    });
                    avisar(`📎 → bajo "${padre.texto.slice(0, 40)}" (${padre.archivo.basename})`);
                    return;
                }
                if (padre && modo === "relacionar") {
                    const ref = padre.texto.replace(/\[[^\]]*::[^\]]*\]/g, "").replace(/\s+/g, " ").trim().slice(0, 60);
                    campos += ` [rel:: ${ref}]`;
                }
            }
        }

        const cuerpo = checklist ? lineas.map((l) => aChecklist(l)).join("\n") : texto.trim();
        const entrada = `\n## ${ahora.format("HH:mm")}\n\n${cuerpo}\n` +
            (checklist ? "" : "\n---\n");

        let archivo = app.vault.getAbstractFileByPath(ruta);
        if (!archivo) {
            // ——— Arrastre de pendientes del diario anterior (día nuevo) ———
            let seccionArrastre = "";
            if (checklist && arrastre && (config.arrastre?.activado ?? true)) {
                try {
                    const previos = app.vault
                        .getMarkdownFiles()
                        .filter((f) => f.parent?.path === carpeta && reDiario.test(f.name))
                        .filter((f) => f.name.slice(0, 10) < fecha)
                        .sort((a, b) => b.name.localeCompare(a.name));
                    if (previos.length > 0) {
                        const prev = previos[0];
                        const contenido = await app.vault.read(prev);
                        const norm = (s) => s.replace(/\[[^\]]*::[^\]]*\]/g, "").replace(/\s+/g, " ").trim().toLowerCase();
                        const vistas = new Set();
                        const pendientes = [];
                        for (const l of contenido.split("\n")) {
                            if (/^\s*- \[ \]/.test(l)) {
                                const clave = norm(l.replace(/^\s*- \[ \]\s*/, ""));
                                if (clave && !vistas.has(clave)) {
                                    vistas.add(clave);
                                    pendientes.push(l);
                                }
                            }
                        }
                        if (pendientes.length > 0) {
                            const enc = (config.arrastre?.encabezado ?? "## ⏭️ Arrastradas de {fecha}")
                                .replace("{fecha}", prev.name.slice(0, 10));
                            seccionArrastre = `\n${enc}\n\n${pendientes.join("\n")}\n`;
                            // En el archivo viejo quedan marcadas como arrastradas:
                            // '- [>]' no cuenta como pendiente → sin duplicados.
                            await app.vault.process(prev, (data) =>
                                data
                                    .split("\n")
                                    .map((l) => (/^\s*- \[ \]/.test(l) ? l.replace("- [ ]", "- [>]") : l))
                                    .join("\n")
                            );
                            avisar(`⏭️ ${pendientes.length} pendiente(s) arrastrada(s) de ${prev.name.slice(0, 10)}`);
                        }
                    }
                } catch (e) { /* el arrastre nunca debe impedir la captura */ }
            }

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
                "AutoNoteMover: disable",
                "---",
                "",
                `# ${nombre} del ${fecha}`,
                "",
            ].join("\n");
            archivo = await app.vault.create(ruta, encabezado + seccionArrastre + entrada);
        } else {
            // Días siguientes / misma jornada: SIEMPRE añadir al final.
            await app.vault.append(archivo, entrada);
        }

        avisar(`${checklist ? "✅" : "📥"} → ${fecha} ${nombre}`);
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
            "Asistente": {
                type: "checkbox",
                defaultValue: false,
                description: "Tras escribir: Estado/Prioridad/Urgencia/Tipo y relación con tareas existentes (Esc = defecto). Requiere Checklist.",
            },
            "Arrastre": {
                type: "checkbox",
                defaultValue: false,
                description: "Al crear el diario de un día nuevo, arrastrar las pendientes del anterior (las viejas quedan '- [>]'). Requiere Checklist.",
            },
        },
    },
};
