<%*
const titulo = await tp.user.titular(tp, "Objetivo");
tR += tp.user.frontmatter(tp, { tipo: "objetivo", titulo: titulo, estado: "activo", tags: [], extra: {plazo: "", metrica: ""} });
await tp.user.archivar(tp, "objetivo");
-%>
# 🎯 <% titulo %>

## Resultado esperado (medible)

-

## ¿Por qué importa?

-

## Hitos

- [ ] 
