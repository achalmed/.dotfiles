/**
 * bandeja.js — Vista DataviewJS: contenido de la bandeja universal.
 *
 * Lista todo lo pendiente de procesar: notas en "01 notes/00-bandeja" y
 * cualquier nota del vault con `estado: bandeja`. Muestra la edad de cada
 * elemento y marca en rojo lo que lleva más de 7 días sin procesar.
 *
 * Uso: await dv.view("meta/capture/bandeja", { limite: 50 });
 *   - limite (opcional): máximo de filas a mostrar. Por defecto 100.
 *
 * Usado por: meta/tablero/bandeja.md, meta/tablero/inicio.md.
 */
const limite = input?.limite ?? 100;

const paginas = dv
    .pages('"01 notes" OR "05 tasks" OR "07 diary" OR "02 analysis"')
    // Pertenece a la bandeja si su estado lo dice; la carpeta solo cuenta
    // para notas sin metadata (creadas fuera del sistema). Una nota ya
    // procesada (estado cambiado) deja de aparecer aunque siga en la carpeta.
    .where((p) => p.estado === "bandeja" ||
                  (!p.estado && p.file.folder === "01 notes/00-bandeja"))
    .distinct((p) => p.file.path)
    .sort((p) => p.file.ctime, "asc");

const hoy = dv.date("today");
const edad = (p) => Math.floor(hoy.diff(p.file.cday, "days").days);

if (paginas.length === 0) {
    dv.paragraph("✅ **Bandeja vacía.** Nada que procesar. Ve a ejecutar.");
} else {
    dv.paragraph(
        `**${paginas.length} elemento(s) sin procesar.** ` +
        (paginas.length > 20 ? "⚠️ Procesa en lote: decide rápido, no organices bonito." : ""));
    dv.table(
        ["Nota", "Tipo", "Edad (días)"],
        paginas.limit(limite).map((p) => [
            p.file.link,
            p.tipo ?? "—",
            edad(p) > 7 ? `🔴 ${edad(p)}` : edad(p),
        ]));
}
