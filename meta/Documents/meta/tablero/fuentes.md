---
tipo: tablero
estado: activo
tags: [tablero]
aliases: [Fuentes, Lecturas]
---

# 📚 Fuentes y lecturas

## 📖 Pendientes de leer / ver

```dataview
TABLE WITHOUT ID file.link AS "Fuente", tipo AS "Tipo", autor AS "Autor", creado AS "Añadida"
WHERE contains(list("libro", "articulo", "paper", "video"), tipo) AND estado = "bandeja"
SORT creado ASC
```

## 🔬 Investigaciones activas

```dataview
TABLE WITHOUT ID file.link AS "Investigación", pregunta AS "Pregunta", proyecto AS "Proyecto"
WHERE tipo = "investigacion" AND estado = "activo"
```

## 🔗 Referencias recientes

```dataview
LIST
WHERE tipo = "referencia"
SORT creado DESC
LIMIT 10
```

> Las notas de lectura de Zotero se crean con `Ctrl+R` (Zotero Integration)
> y viven en `01 notes` — búscalas con los workspaces de siempre (`Ctrl+S`).

← [[inicio]]
