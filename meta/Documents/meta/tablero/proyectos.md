---
tipo: tablero
estado: activo
tags: [tablero]
aliases: [Proyectos]
---

# 🗂️ Proyectos

> Máximo 3 activos. Un proyecto activo SIEMPRE tiene una siguiente acción
> sin marcar; si no la tiene, está bloqueado aunque no lo parezca.

```dataviewjs
await dv.view("meta/tasks/proyectos", { wip: 3 });
```

## ✅ Tareas sueltas por estado

```dataview
TABLE WITHOUT ID file.link AS "Tarea", proyecto AS "Proyecto", fecha_limite AS "Límite", estado AS "Estado"
WHERE tipo = "tarea" AND !contains(list("hecho", "archivado"), estado)
SORT fecha_limite ASC
```

← [[inicio]]
