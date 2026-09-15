<%*
const titulo = await tp.user.titular(tp, "Reunión");
tR += tp.user.frontmatter(tp, { tipo: "reunion", titulo: titulo, estado: "activo", tags: [], extra: {con: "", fecha_reunion: ""} });
await tp.user.archivar(tp, "reunion");
-%>
# 🤝 <% titulo %>

## Agenda

-

## Notas

-

## Acuerdos → tareas (procesar al terminar)

- [ ] 
