<%*
const titulo = await tp.user.titular(tp, "Hábito");
tR += tp.user.frontmatter(tp, { tipo: "habito", estado: "activo", tags: ["habito"], extra: {disparador: "", recompensa: ""} });
-%>
# 🌿 <% titulo %>

## Hábito (versión mínima viable: tan fácil que no puedas fallar)

-

## Registro

- <% tp.date.now("YYYY-MM-DD") %> — inicio.
