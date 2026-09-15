<%*
const titulo = await tp.user.titular(tp, "Problema");
tR += tp.user.frontmatter(tp, { tipo: "problema", titulo: titulo, estado: "activo", tags: [], extra: {proyecto: ""} });
await tp.user.archivar(tp, "problema");
-%>
# 🧩 <% titulo %>

## Síntoma (qué se observa)

-

## Causa probable

-

## Posibles soluciones

-

## Siguiente acción

- [ ] 
