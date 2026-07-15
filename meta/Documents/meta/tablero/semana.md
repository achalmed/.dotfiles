---
tipo: tablero
estado: activo
tags: [tablero]
aliases: [Semana]
---

# 🗓️ Semana

## ⏰ Con fecha límite en los próximos 7 días

```dataview
TABLE WITHOUT ID file.link AS "Qué", tipo AS "Tipo", fecha_limite AS "Límite"
WHERE fecha_limite AND date(fecha_limite) >= date(today) AND date(fecha_limite) <= date(today) + dur(7 days) AND !contains(list("hecho", "archivado"), estado)
SORT fecha_limite ASC
```

## 🔴 Vencidas

```dataview
TABLE WITHOUT ID file.link AS "Qué", tipo AS "Tipo", fecha_limite AS "Límite"
WHERE fecha_limite AND date(fecha_limite) < date(today) AND !contains(list("hecho", "archivado"), estado)
SORT fecha_limite ASC
```

## ⏸️ En espera (delegado / bloqueado por terceros)

```dataview
TABLE WITHOUT ID file.link AS "Qué", tipo AS "Tipo", esperando AS "Esperando a"
WHERE estado = "espera"
```

## 📤 Exportar tareas activas a Super Productivity

```dataviewjs
await dv.view("meta/integrations/super-productivity/exportar-sp", { origen: "tareas" });
```

## 📅 Planes diarios de esta semana

```dataview
LIST
FROM "07 diary"
WHERE tipo = "plan-diario" AND fecha >= date(today) - dur(6 days)
SORT fecha DESC
```

← [[inicio]]
