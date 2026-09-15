/**
 * proyectos.js — Vista DataviewJS: estado de todos los proyectos.
 *
 * Muestra tres bloques y aplica las reglas anti-procrastinación:
 *   1. Activos — con su SIGUIENTE ACCIÓN (primera tarea sin completar).
 *      Un proyecto activo sin siguiente acción se marca 🚫 (está bloqueado
 *      de facto). Un proyecto sin tocar en 14 días se marca 😴 (detenido).
 *      Si hay más de `wip` proyectos activos, avisa (límite de trabajo
 *      en curso).
 *   2. En espera — estado "en_espera" (delegado / esperando algo externo).
 *   3. Algún día — estado "algun_dia" (incubación).
 *
 * Uso: await dv.view("meta/tasks/proyectos", { wip: 3 });
 *
 * Usado por: meta/tablero/proyectos.md, meta/tablero/inicio.md
 * (con { soloSiguiente: true } muestra solo las siguientes acciones).
 */
const wip = input?.wip ?? 3;
const soloSiguiente = input?.soloSiguiente ?? false;

// Acotado a las carpetas de contenido del vault: sin argumento, dv.pages()
// indexaría TODO ~/Documents (biblioteca, pub_*, repos) — lentísimo e
// irrelevante. Los proyectos (tipo: proyecto) viven en estas carpetas: se
// crean en la bandeja (01 notes) y se archivan a 05 tasks (ver
// core/config/config.json → destinos.proyecto); 02 analysis y 07 diary se
// incluyen por si una nota tipada acaba allí.
const CARPETAS = '"01 notes" or "02 analysis" or "05 tasks" or "07 diary"';
const todos = dv.pages(CARPETAS).where((p) => p.tipo === "proyecto");
const activos = todos.where((p) => p.estado === "activo").sort((p) => p.file.mtime, "desc");
const espera = todos.where((p) => p.estado === "en_espera");
const algunDia = todos.where((p) => p.estado === "algun_dia");

const hoy = dv.date("today");
const diasSinTocar = (p) => Math.floor(hoy.diff(p.file.mday, "days").days);
const siguienteAccion = (p) => {
    const t = p.file.tasks.filter((t) => !t.completed).first();
    return t ? t.text : "🚫 SIN siguiente acción — defínela o pasa el proyecto a en_espera";
};

if (activos.length > wip) {
    dv.paragraph(
        `⚠️ **${activos.length} proyectos activos (límite: ${wip}).** ` +
        "Demasiados frentes = ninguno avanza. Pasa alguno a `estado: en_espera` o `algun_dia`.");
}

dv.header(3, `🟢 Activos (${activos.length})`);
dv.table(
    ["Proyecto", "Siguiente acción", "Días sin tocar"],
    activos.map((p) => [
        p.file.link,
        siguienteAccion(p),
        diasSinTocar(p) > 14 ? `😴 ${diasSinTocar(p)}` : diasSinTocar(p),
    ]));

if (!soloSiguiente) {
    dv.header(3, `⏸️ En espera (${espera.length})`);
    dv.table(["Proyecto", "Esperando"], espera.map((p) => [p.file.link, p.esperando ?? "—"]));

    dv.header(3, `🌤️ Algún día (${algunDia.length})`);
    dv.list(algunDia.map((p) => p.file.link));
}
