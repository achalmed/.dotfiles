<%*
const titulo = await tp.user.titular(tp, "Aprendizaje");
tR += tp.user.frontmatter(tp, { tipo: "aprendizaje", estado: "hecho", tags: ["aprendizaje"], extra: {fuente: ""} });
await tp.user.archivar(tp, "aprendizaje");
-%>
# 🌱 <% titulo %>

## ¿Qué aprendí?

-

## ¿Dónde lo aplico?

- 
