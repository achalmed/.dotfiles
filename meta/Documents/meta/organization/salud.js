/**
 * salud.js — Vista DataviewJS: salud del sistema (mantenimiento).
 *
 * Detecta automáticamente las notas que rompen el estándar, para que el
 * usuario nunca tenga que "salir a buscar" desorden:
 *   - Sin título real (Untitled / "captura" / "entrada" automáticos)
 *   - Sin metadata (sin `tipo` o sin `estado`) — solo notas creadas desde
 *     la fecha `desde` (las históricas del vault no se auditan)
 *   - Bandeja envejecida (estado bandeja con más de 7 días)
 *   - Huérfanas recientes (sin enlaces entrantes ni salientes)
 *
 * Uso: await dv.view("meta/organization/salud", { desde: "2026-07-06" });
 *
 * Usado por: meta/tablero/mantenimiento.md.
 */
const desde = dv.date(input?.desde ?? "2026-07-06");
const CONTENIDO = ["01 notes", "02 analysis", "05 tasks", "07 diary", "06 archives"];

const recientes = dv
    .pages(CONTENIDO.map((c) => `"${c}"`).join(" OR "))
    .where((p) => p.file.cday >= desde);

const sinTitulo = recientes.where((p) =>
    /^(untitled|sin título|captura$|entrada \d)/i.test(p.file.name));
const sinMetadata = recientes.where((p) => !p.tipo || !p.estado);
const hoy = dv.date("today");
const envejecidas = recientes.where((p) =>
    p.estado === "bandeja" && hoy.diff(p.file.cday, "days").days > 7);
const huerfanas = recientes.where((p) =>
    p.file.inlinks.length === 0 && p.file.outlinks.length === 0 &&
    p.tipo !== "plan-diario");

const seccion = (titulo, paginas, consejo) => {
    dv.header(3, `${titulo} (${paginas.length})`);
    if (paginas.length === 0) dv.paragraph("✅ Nada.");
    else {
        dv.paragraph(consejo);
        dv.list(paginas.limit(30).map((p) => p.file.link));
    }
};

seccion("🏷️ Notas sin título real", sinTitulo,
    "Renómbralas con un título descriptivo (o bórralas si ya no aportan).");
seccion("📇 Notas sin tipo o estado", sinMetadata,
    "Añade `tipo:` y `estado:` en Properties, o recréalas desde una plantilla.");
seccion("🧟 Bandeja envejecida (> 7 días)", envejecidas,
    "Decisión rápida por cada una: hacer, agendar, algún-día o borrar.");
seccion("🔗 Huérfanas recientes", huerfanas,
    "Enlázalas desde el proyecto/tema al que pertenecen, o archívalas.");
