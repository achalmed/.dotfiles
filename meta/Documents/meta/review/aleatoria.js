/**
 * aleatoria.js — Vista DataviewJS: resucita notas antiguas al azar.
 *
 * Muestra N notas aleatorias de un tipo dado, priorizando material olvidado
 * (más de 30 días sin modificar). Sirve para revisar ideas viejas sin tener
 * que "ponerse a revisar": cada vez que abres el tablero aparecen otras.
 *
 * Uso: await dv.view("meta/review/aleatoria", { tipo: "idea", n: 3 });
 *   - tipo (opcional): filtra por `tipo:` del frontmatter. Sin tipo = todas.
 *   - n    (opcional): cuántas mostrar. Por defecto 3.
 *
 * Usado por: meta/tablero/ideas.md.
 */
const tipo = input?.tipo ?? null;
const n = input?.n ?? 3;

const hoy = dv.date("today");
let paginas = dv.pages('"01 notes" OR "02 analysis"')
    .where((p) => (tipo ? p.tipo === tipo : true))
    .where((p) => hoy.diff(p.file.mday, "days").days > 30);

// Si no hay nada tan antiguo, usa cualquiera del tipo.
if (paginas.length === 0 && tipo) {
    paginas = dv.pages('"01 notes" OR "02 analysis"').where((p) => p.tipo === tipo);
}

const barajadas = paginas.array().sort(() => Math.random() - 0.5).slice(0, n);

if (barajadas.length === 0) {
    dv.paragraph("Nada que resucitar todavía.");
} else {
    dv.paragraph("¿Sigue viva? Enlázala a un proyecto. ¿Muerta? Archívala o bórrala.");
    dv.list(barajadas.map((p) => p.file.link));
}
