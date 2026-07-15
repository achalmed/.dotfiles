<%*
const titulo = await tp.user.titular(tp, "Experimento");
tR += tp.user.frontmatter(tp, { tipo: "experimento", estado: "activo", tags: ["experimento"], extra: {hipotesis: "", inicio: "", fin: ""} });
await tp.user.archivar(tp, "experimento");
-%>
# ⚗️ <% titulo %>

## Diseño (qué se cambia, qué se mide)

-

## Resultado

-

## Aprendizaje

- 
