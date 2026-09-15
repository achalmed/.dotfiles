<%*
const titulo = await tp.user.titular(tp, "Persona");
tR += tp.user.frontmatter(tp, { tipo: "persona", titulo: titulo, estado: "activo", tags: [], extra: {relacion: "", contacto: ""} });
await tp.user.archivar(tp, "persona");
-%>
# 👤 <% titulo %>

## Quién es

-

## Temas en común / pendientes con esta persona

- [ ] 
