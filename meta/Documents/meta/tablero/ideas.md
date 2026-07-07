---
tipo: tablero
estado: activo
tags: [tablero]
aliases: [Ideas]
---

# 💡 Ideas

## Sin procesar

```dataview
TABLE WITHOUT ID file.link AS "Idea", creado AS "Capturada", estado AS "Estado"
WHERE tipo = "idea" AND estado = "bandeja"
SORT creado ASC
```

## 🌤️ En incubación (algún día)

```dataview
LIST
WHERE tipo = "idea" AND estado = "algun-dia"
```

## 🎲 Resucitar: 3 notas antiguas al azar

> Cada vez que abres este tablero salen otras. Cero esfuerzo de revisión.

```dataviewjs
await dv.view("meta/dataview/vistas/aleatoria", { tipo: "idea", n: 3 });
```

← [[inicio]]
