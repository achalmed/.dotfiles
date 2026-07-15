/**
 * agrupar.js — Vista DataviewJS: SUGERENCIAS de agrupación de tareas.
 *
 * Replica el método "hoja de papel bond": capturar suelto durante el día y
 * al final detectar qué ideas pertenecen al mismo tema. Analiza las tareas
 * pendientes recientes de los diarios de tareas, detecta palabras
 * significativas compartidas y propone grupos:
 *
 *     Estas 4 tareas parecen del mismo tema («latex») — ¿agruparlas?
 *     [✅ Agrupar]  [🚫 No]  [⏰ Más tarde]
 *
 * SOLO sugiere; nunca actúa sola:
 *   - Agrupar   → añade `[tema:: palabra]` a esas líneas (nada se mueve).
 *   - No        → no volver a sugerir esa palabra (localStorage).
 *   - Más tarde → oculta la sugerencia durante esta sesión (sessionStorage).
 *
 * Configuración: meta/sistema/config.json → agrupacion
 * (días analizados, stopwords, tamaño mínimo de grupo, máx. sugerencias).
 *
 * Uso: await dv.view("meta/dataview/vistas/agrupar", {});
 * Usado por: meta/tablero/bandeja.md.
 */
let config = {};
try {
    config = JSON.parse(await dv.io.load("meta/sistema/config.json")) ?? {};
} catch (e) { /* sin config → valores por defecto */ }
const cfg = config.agrupacion ?? {};
const DIAS = cfg.diasAnalisis ?? 7;
const MIN_LETRAS = cfg.minLetrasPalabra ?? 4;
const MIN_TAREAS = cfg.minTareasPorGrupo ?? 2;
const MAX_SUGERENCIAS = cfg.maxSugerencias ?? 5;
const STOPWORDS = new Set((cfg.stopwords ?? []).map((w) => w.toLowerCase()));

const limite = dv.date("today").minus(dv.duration(`${DIAS} days`));

// Tareas pendientes de los diarios "AAAA-MM-DD Tareas" recientes.
const paginas = dv
    .pages('"05 tasks"')
    .where((p) => /^\d{4}-\d{2}-\d{2} Tareas$/.test(p.file.name) &&
                  dv.date(p.file.name.slice(0, 10)) >= limite);

const tareas = [];
for (const p of paginas) {
    for (const t of p.file.tasks) {
        if (t.status === " ") tareas.push({ path: t.path, line: t.line, texto: t.text });
    }
}

// Tokenizar: sin campos inline, sin acentos, solo palabras significativas.
const normalizar = (s) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const palabrasDe = (texto) => {
    const limpio = normalizar(texto.replace(/\[[^\]]*::[^\]]*\]/g, " "));
    return [...new Set(
        limpio.split(/[^a-zñ0-9]+/)
            .filter((w) => w.length >= MIN_LETRAS && !STOPWORDS.has(w))
    )];
};

const porPalabra = new Map();
for (const t of tareas) {
    for (const w of palabrasDe(t.texto)) {
        if (!porPalabra.has(w)) porPalabra.set(w, []);
        porPalabra.get(w).push(t);
    }
}

// Proponer: palabras con suficientes tareas, no descartadas, sin tema ya puesto.
const descartada = (w) =>
    window.localStorage.getItem(`metaos.agrupar.no.${w}`) === "1" ||
    window.sessionStorage.getItem(`metaos.agrupar.luego.${w}`) === "1";
const yaAgrupado = (grupo) => grupo.every((t) => /\[tema::/.test(t.texto));

const vistos = new Set(); // conjuntos de tareas ya propuestos (evitar duplicados)
const propuestas = [];
for (const [palabra, grupo] of [...porPalabra.entries()].sort((a, b) => b[1].length - a[1].length)) {
    if (grupo.length < MIN_TAREAS || descartada(palabra) || yaAgrupado(grupo)) continue;
    const clave = grupo.map((t) => `${t.path}:${t.line}`).sort().join("|");
    if (vistos.has(clave)) continue;
    vistos.add(clave);
    propuestas.push({ palabra, grupo });
    if (propuestas.length >= MAX_SUGERENCIAS) break;
}

if (propuestas.length === 0) {
    dv.paragraph("💤 Sin sugerencias: ninguna palabra significativa se repite entre las tareas pendientes recientes.");
} else {
    dv.paragraph(`🧩 **${propuestas.length} posible(s) tema(s) detectado(s)** en tus tareas de los últimos ${DIAS} días. Tú decides — el sistema nunca agrupa solo.`);
    for (const { palabra, grupo } of propuestas) {
        const caja = dv.container.createEl("div", {
            attr: { style: "border:1px solid var(--background-modifier-border); border-radius:8px; padding:0.6em 0.9em; margin:0.5em 0;" },
        });
        caja.createEl("strong", { text: `Estas ${grupo.length} tareas parecen del mismo tema: «${palabra}»` });
        const ul = caja.createEl("ul");
        for (const t of grupo) {
            ul.createEl("li", { text: t.texto.replace(/\[[^\]]*::[^\]]*\]/g, "").trim() + `  · ${t.path.split("/").pop().replace(".md", "")}` });
        }
        const botones = caja.createEl("div");
        const boton = (texto, accion) => {
            const b = botones.createEl("button", { text: texto, attr: { style: "margin-right:0.5em;" } });
            b.addEventListener("click", accion);
            return b;
        };
        boton(`✅ Agrupar como [tema:: ${palabra}]`, async () => {
            let n = 0;
            for (const t of grupo) {
                const archivo = app.vault.getAbstractFileByPath(t.path);
                if (!archivo) continue;
                await app.vault.process(archivo, (data) => {
                    const arr = data.split("\n");
                    if (arr[t.line] !== undefined && arr[t.line].includes(t.texto.slice(0, 20)) && !arr[t.line].includes("[tema::")) {
                        arr[t.line] += ` [tema:: ${palabra}]`;
                        n++;
                    }
                    return arr.join("\n");
                });
            }
            new Notice(`🧩 [tema:: ${palabra}] añadido a ${n} tarea(s).`);
            caja.remove();
        });
        boton("🚫 No", () => {
            window.localStorage.setItem(`metaos.agrupar.no.${palabra}`, "1");
            caja.remove();
        });
        boton("⏰ Más tarde", () => {
            window.sessionStorage.setItem(`metaos.agrupar.luego.${palabra}`, "1");
            caja.remove();
        });
    }
}
