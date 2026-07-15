---
tipo: tablero
estado: activo
tags: [tablero]
aliases: [Inicio, Home]
---

# 🏠 Inicio

> `Alt+C` capturar · `Alt+T` capturar tarea · `Alt+N` nota tipada · `Alt+D` plan de hoy · `Alt+B` bandeja

## ⏭️ Siguiente acción por proyecto

> Regla de oro: elige UNA y empieza. No sigas leyendo el tablero.

```dataviewjs
await dv.view("meta/tasks/proyectos", { soloSiguiente: true, wip: 3 });
```

## 🎯 Prioridades de hoy

```dataviewjs
const hoy = window.moment().format("YYYY-MM-DD");
const plan = dv.page(`07 diary/${window.moment().format("YYYY")}/${hoy}`);
if (!plan) {
    dv.paragraph(`⚠️ Aún no existe el plan de hoy. Ábrelo con **Alt+D** (se crea solo).`);
} else {
    const tareas = plan.file.tasks.filter(t => !t.completed);
    if (tareas.length === 0) dv.paragraph("✅ Todo lo de hoy está hecho (o aún sin definir).");
    else dv.taskList(tareas, false);
}
```

## ⚡ Tareas rápidas (para arrancar cuando cuesta empezar)

> Menos de 15 min cada una. Empezar por una pequeña rompe la parálisis.

```dataview
LIST
WHERE tipo = "tarea" AND estado = "siguiente" AND (sp_est = "5m" OR sp_est = "10m" OR sp_est = "15m")
LIMIT 5
```

## 📥 Bandeja

```dataviewjs
const n = dv.pages('"01 notes" OR "05 tasks" OR "07 diary" OR "02 analysis"')
    .where(p => p.estado === "bandeja" ||
                (!p.estado && p.file.folder === "01 notes/00-bandeja"))
    .length;
dv.paragraph(n === 0
    ? "✅ Bandeja vacía."
    : `**${n} elemento(s) esperando.** Se procesan a las 20:20 o en la revisión semanal — no ahora. → [[bandeja]]`);
```

## 🧭 Tableros

[[bandeja]] · [[proyectos]] · [[ideas]] · [[fuentes]] · [[semana]] · [[mantenimiento]]
