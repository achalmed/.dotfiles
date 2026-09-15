<%*
const titulo = await tp.user.titular(tp, "Experimento");
tR += tp.user.frontmatter(tp, { tipo: "experimento", titulo: titulo, estado: "activo", tags: [], extra: {hipotesis: "", inicio: "", fin: ""} });
await tp.user.archivar(tp, "experimento");
-%>
# ⚗️ <% titulo %>

## Diseño (qué se cambia, qué se mide)

-

## Resultado

-

## Aprendizaje

- 
