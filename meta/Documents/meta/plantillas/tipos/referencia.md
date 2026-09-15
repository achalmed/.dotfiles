<%*
const titulo = await tp.user.titular(tp, "Referencia");
tR += tp.user.frontmatter(tp, { tipo: "referencia", titulo: titulo, estado: "activo", tags: [], extra: {url: "", fuente: ""} });
await tp.user.archivar(tp, "referencia");
-%>
# 🔗 <% titulo %>

## ¿Para qué sirve?

-

## Contenido / extracto

- 
