<%*
const titulo = await tp.user.titular(tp, "Bitácora");
tR += tp.user.frontmatter(tp, { tipo: "bitacora", titulo: titulo, estado: "activo", tags: [], extra: {proyecto: ""} });
await tp.user.archivar(tp, "bitacora");
-%>
# 📓 <% titulo %>

## <% tp.date.now("YYYY-MM-DD") %>

- 
