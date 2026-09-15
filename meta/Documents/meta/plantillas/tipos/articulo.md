<%*
const titulo = await tp.user.titular(tp, "Artículo");
tR += tp.user.frontmatter(tp, { tipo: "articulo", titulo: titulo, estado: "bandeja", tags: [], extra: {autor: "", url: ""} });
await tp.user.archivar(tp, "articulo");
-%>
# 📰 <% titulo %>

## Idea central

-

## Notas

- 
