<%*
const trimestre = `${tp.date.now("YYYY")}-Q${tp.date.now("Q")}`;
await tp.file.rename(`${trimestre} Revisión trimestral`);
tR += tp.user.frontmatter(tp, {
  tipo: "revision-trimestral",
  estado: "en-curso",
  tags: ["revision"],
  extra: { trimestre: `"${trimestre}"` },
});
-%>
# 🧭 Revisión trimestral — <% trimestre %>

> Una tarde por trimestre. Aquí SÍ se permite pensar en grande — es el
> único lugar del sistema donde está permitido.

## 1 · ¿El rumbo sigue siendo el correcto?

- ¿Qué me acercó de verdad a donde quiero estar (docencia, investigación, publicaciones)?
- ¿Qué consumió tiempo sin mover nada?
- Si solo pudiera conservar 3 proyectos, ¿cuáles?

```dataviewjs
await dv.view("meta/dataview/vistas/proyectos", { wip: 3 });
```

## 2 · Poda dura

- Proyectos a archivar (mínimo 1):
- Objetivos a matar o reformular:
- Hábitos/rutinas que ya no sirven:

## 3 · Objetivos del próximo trimestre

> Máximo 3. Crea cada uno con `Alt+N` → plantilla `objetivo`.

1.
2.
3.

## 4 · Sistema

- ¿Qué fricción apareció repetidamente en las revisiones semanales?
- UNA mejora estructural para el trimestre (solo una):

> Al terminar: `estado: hecho`.
