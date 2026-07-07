<%*
const titulo = await tp.user.titular(tp, "Bitácora");
tR += tp.user.frontmatter(tp, { tipo: "bitacora", estado: "activo", tags: ["bitacora"], extra: {proyecto: ""} });
-%>
# 📓 <% titulo %>

## <% tp.date.now("YYYY-MM-DD") %>

- 
