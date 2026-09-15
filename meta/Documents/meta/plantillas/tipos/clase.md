<%*
const titulo = await tp.user.titular(tp, "Clase");
tR += tp.user.frontmatter(tp, { tipo: "clase", titulo: titulo, estado: "activo", tags: [], extra: {curso: "", fecha_clase: ""} });
await tp.user.archivar(tp, "clase");
-%>
# 🎓 <% titulo %>

## Objetivo de la sesión

-

## Contenido / guion

-

## Materiales

-

## Tareas derivadas

- [ ] 
