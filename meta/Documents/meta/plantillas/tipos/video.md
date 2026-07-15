<%*
const titulo = await tp.user.titular(tp, "Video");
tR += tp.user.frontmatter(tp, { tipo: "video", estado: "bandeja", tags: ["source", "video"], extra: {canal: "", url: ""} });
await tp.user.archivar(tp, "video");
-%>
# 🎬 <% titulo %>

## Idea central

-

## Notas (con minuto)

- 
