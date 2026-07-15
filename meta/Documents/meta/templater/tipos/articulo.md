<%*
const titulo = await tp.user.titular(tp, "Artículo");
tR += tp.user.frontmatter(tp, { tipo: "articulo", estado: "bandeja", tags: ["source", "articulo"], extra: {autor: "", url: ""} });
await tp.user.archivar(tp, "articulo");
-%>
# 📰 <% titulo %>

## Idea central

-

## Notas

- 
