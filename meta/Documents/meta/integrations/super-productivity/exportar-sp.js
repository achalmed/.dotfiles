/**
 * exportar-sp.js — Vista DataviewJS: exportador a Super Productivity.
 *
 * Convierte tareas de Obsidian en líneas de texto con la sintaxis corta de
 * Super Productivity, listas para COPIAR Y PEGAR en su barra "Add task"
 * (una línea = una tarea). Sintaxis generada, apta para regex:
 *
 *     <texto de la tarea> +<proyecto> #<tag> <estimado> @<fecha>
 *
 * Modos (parámetro `origen`):
 *   - "actual"  → tareas sin completar (- [ ]) de la nota actual
 *                 (p. ej. las 3 prioridades del plan diario).
 *   - "tareas"  → todo lo accionable del vault: casillas sin completar de
 *                 los diarios de tareas (tipo "tareas", creados con Alt+T)
 *                 + notas tipo "tarea" con estado "siguiente" o "activo"
 *                 (usa sus campos: proyecto, sp_est, fecha_limite).
 *
 * Uso: await dv.view("meta/integrations/super-productivity/exportar-sp", { origen: "actual" });
 *
 * Usado por: meta/plantillas/planes/plan-diario.md, meta/tablero/semana.md.
 */
const origen = input?.origen ?? "actual";
let lineas = [];

const limpiar = (texto) =>
    texto.replace(/\[\[([^\]|]+\|)?([^\]]+)\]\]/g, "$2") // [[enlaces]] → texto
         .replace(/\s+/g, " ")
         .trim();

if (origen === "actual") {
    lineas = dv.current().file.tasks
        .filter((t) => !t.completed)
        .map((t) => limpiar(t.text))
        .filter((t) => t.length > 0) // checkboxes aún vacíos no se exportan
        .array();
} else {
    // 1) Casillas pendientes de los diarios de tareas (Alt+T).
    const deDiarios = dv.pages('"05 tasks"')
        .where((p) => p.tipo === "tareas")
        .sort((p) => p.file.name, "asc")
        .flatMap((p) => p.file.tasks.filter((t) => !t.completed))
        .map((t) => limpiar(t.text))
        .filter((t) => t.length > 0)
        .array();

    // 2) Notas de tarea individuales (con proyecto/estimado/fecha).
    const deNotas = dv.pages()
        .where((p) => p.tipo === "tarea" && ["siguiente", "activo"].includes(p.estado))
        .sort((p) => p.fecha_limite ?? p.file.ctime, "asc")
        .map((p) => {
            let linea = limpiar(p.file.name.replace(/^\d{4}-\d{2}-\d{2} Tarea - /, ""));
            if (p.proyecto) linea += ` +${String(p.proyecto).replace(/\s+/g, "-")}`;
            if (p.sp_est) linea += ` ${p.sp_est}`;
            if (p.fecha_limite) linea += ` @${p.fecha_limite}`;
            return linea;
        })
        .array();

    lineas = [...deDiarios, ...deNotas];
}

if (lineas.length === 0) {
    dv.paragraph("✅ Nada que exportar.");
} else {
    dv.paragraph("Copia el bloque (botón 📋 del bloque de código) y pega **línea por línea** en la barra *Add task* de Super Productivity:");
    dv.paragraph("```\n" + lineas.join("\n") + "\n```");
}
