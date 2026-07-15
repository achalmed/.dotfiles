<%*
const titulo = await tp.user.titular(tp, "Nota");
tR += tp.user.frontmatter(tp, { tipo: "nota", estado: "bandeja", tags: ["nota"], extra: {} });
await tp.user.archivar(tp, "nota");
-%>
# 📝 <% titulo %>

- 
