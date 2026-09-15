<%*
const titulo = await tp.user.titular(tp, "Decisión");
tR += tp.user.frontmatter(tp, { tipo: "decision", titulo: titulo, estado: "activo", tags: [], extra: {fecha_limite: ""} });
await tp.user.archivar(tp, "decision");
-%>
# ⚖️ <% titulo %>

## ¿Qué hay que decidir?

-

## Opciones y costo de cada una

1.

## Criterio de decisión

-

## ✅ Decisión tomada y por qué

-

## Revisión (¿fue buena? — completar después)

- 
