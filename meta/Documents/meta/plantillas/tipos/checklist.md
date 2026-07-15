<%*
const titulo = await tp.user.titular(tp, "Checklist");
tR += tp.user.frontmatter(tp, { tipo: "checklist", estado: "activo", tags: ["checklist"], extra: {} });
await tp.user.archivar(tp, "checklist");
-%>
# ☑️ <% titulo %>

## Pasos

- [ ] 
