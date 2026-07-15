---
tipo: tablero
estado: activo
tags: [tablero]
aliases: [Mantenimiento]
---

# 🧹 Mantenimiento del sistema

> Se mira UNA vez por semana (dentro de la revisión semanal), no cada día.
> Si todo sale ✅, cierra y no toques nada: un sistema sano se nota porque
> no pide atención.

```dataviewjs
await dv.view("meta/organization/salud", { desde: "2026-07-06" });
```

## 📊 Notas recientes (últimos 7 días)

```dataview
TABLE WITHOUT ID file.link AS "Nota", tipo AS "Tipo", estado AS "Estado", creado AS "Creada"
WHERE creado AND date(creado) >= date(today) - dur(7 days)
SORT creado DESC
LIMIT 30
```

← [[inicio]]
