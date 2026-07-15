<%*
const titulo = await tp.user.titular(tp, "Idea");
tR += tp.user.frontmatter(tp, { tipo: "idea", estado: "bandeja", tags: ["idea"], extra: {} });
await tp.user.archivar(tp, "idea");
-%>
# 💡 <% titulo %>

## La idea

-

## ¿Por qué importa?

-

## Siguiente acción (si no hay ninguna, en la revisión pasa a `algun-dia`)

- [ ] 
