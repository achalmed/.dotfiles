<%*
const titulo = await tp.user.titular(tp, "Investigación");
tR += tp.user.frontmatter(tp, { tipo: "investigacion", estado: "activo", tags: ["investigacion"], extra: {pregunta: "", proyecto: ""} });
await tp.user.archivar(tp, "investigacion");
-%>
# 🔬 <% titulo %>

## Pregunta de investigación

-

## Hallazgos

-

## Fuentes

-

## Siguiente acción

- [ ] 
