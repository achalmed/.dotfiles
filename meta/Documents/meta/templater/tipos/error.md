<%*
const titulo = await tp.user.titular(tp, "Error");
tR += tp.user.frontmatter(tp, { tipo: "error", estado: "hecho", tags: ["error"], extra: {proyecto: ""} });
await tp.user.archivar(tp, "error");
-%>
# 🐞 <% titulo %>

## ¿Qué salió mal?

-

## Causa raíz

-

## ¿Cómo evitarlo la próxima vez?

- 
