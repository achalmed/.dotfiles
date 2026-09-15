<%*
const titulo = await tp.user.titular(tp, "Reflexión");
tR += tp.user.frontmatter(tp, { tipo: "reflexion", titulo: titulo, estado: "hecho", tags: [], extra: {} });
await tp.user.archivar(tp, "reflexion");
-%>
# 🪞 <% titulo %>

## ¿Qué pasó / qué estoy pensando?

-

## ¿Qué hago con esto? (nada también es respuesta válida)

- 
