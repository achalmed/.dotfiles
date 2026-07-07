<%*
const titulo = await tp.user.titular(tp, "Proyecto");
tR += tp.user.frontmatter(tp, { tipo: "proyecto", estado: "activo", tags: ["project"], extra: {objetivo: "", fecha_limite: "", esperando: ""} });
-%>
# 🗂️ <% titulo %>

## Objetivo (¿cómo se ve TERMINADO?)

-

## ⏭️ Siguiente acción (siempre debe haber UNA sin marcar)

- [ ]

## Tareas

- [ ]

## Registro

- <% tp.date.now("YYYY-MM-DD") %> — creado.
