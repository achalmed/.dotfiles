<%*
const titulo = await tp.user.titular(tp, "Nota");
tR += tp.user.frontmatter(tp, { tipo: "nota", titulo: titulo, estado: "bandeja", tags: [], extra: {} });
await tp.user.archivar(tp, "nota");
-%>
# 📝 <% titulo %>

- 
