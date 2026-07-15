<%*
const titulo = await tp.user.titular(tp, "Tarea");
tR += tp.user.frontmatter(tp, { tipo: "tarea", estado: "siguiente", tags: ["task"], extra: {proyecto: "", fecha_limite: "", sp_est: 30m} });
await tp.user.archivar(tp, "tarea");
-%>
# ✅ <% titulo %>

## Descripción

- [ ]

> Para ejecutarla en Super Productivity: aparece en el exportador del
> plan diario y de [[semana]] mientras `estado` sea `siguiente` o `activo`.
