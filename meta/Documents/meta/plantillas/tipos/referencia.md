<%*
const titulo = await tp.user.titular(tp, "Referencia");
tR += tp.user.frontmatter(tp, { tipo: "referencia", estado: "activo", tags: ["referencia"], extra: {url: "", fuente: ""} });
await tp.user.archivar(tp, "referencia");
-%>
# 🔗 <% titulo %>

## ¿Para qué sirve?

-

## Contenido / extracto

- 
