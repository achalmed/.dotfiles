<%*
const titulo = await tp.user.titular(tp, "Libro");
tR += tp.user.frontmatter(tp, { tipo: "libro", titulo: titulo, estado: "bandeja", tags: [], extra: {autor: "", anio: "", estado_lectura: por_leer} });
await tp.user.archivar(tp, "libro");
-%>
# 📖 <% titulo %>

## ¿Por qué leerlo?

-

## Notas

-

## Citas

> 
