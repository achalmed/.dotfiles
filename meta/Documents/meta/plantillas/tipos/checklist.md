<%*
const titulo = await tp.user.titular(tp, "Checklist");
tR += tp.user.frontmatter(tp, { tipo: "checklist", titulo: titulo, estado: "activo", tags: [], extra: {} });
await tp.user.archivar(tp, "checklist");
-%>
# ☑️ <% titulo %>

## Pasos

- [ ] 
