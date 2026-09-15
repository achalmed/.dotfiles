<%*
const titulo = await tp.user.titular(tp, "Idea");
tR += tp.user.frontmatter(tp, { tipo: "idea", titulo: titulo, estado: "bandeja", tags: [], extra: {} });
await tp.user.archivar(tp, "idea");
-%>
# 💡 <% titulo %>

## La idea

-

## ¿Por qué importa?

-

## Siguiente acción (si no hay ninguna, en la revisión pasa a `estado: algun_dia`)

- [ ] 
