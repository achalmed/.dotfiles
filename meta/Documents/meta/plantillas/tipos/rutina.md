<%*
const titulo = await tp.user.titular(tp, "Rutina");
tR += tp.user.frontmatter(tp, { tipo: "rutina", titulo: titulo, estado: "activo", tags: [], extra: {horario: ""} });
await tp.user.archivar(tp, "rutina");
-%>
# 🔁 <% titulo %>

## Pasos (en orden, sin decisiones)

1. 
