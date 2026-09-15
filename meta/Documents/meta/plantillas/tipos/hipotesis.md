<%*
const titulo = await tp.user.titular(tp, "Hipótesis");
tR += tp.user.frontmatter(tp, { tipo: "hipotesis", titulo: titulo, estado: "activo", tags: [], extra: {} });
await tp.user.archivar(tp, "hipotesis");
-%>
# 🧪 <% titulo %>

## Enunciado (si X, entonces Y, porque Z)

-

## ¿Cómo probarla / refutarla?

-

## Evidencia a favor / en contra

- 
