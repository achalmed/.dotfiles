<%*
const anio = tp.date.now("YYYY");
await tp.file.rename(`${anio} Revisión anual`);
tR += tp.user.frontmatter(tp, {
  tipo: "revision-anual",
  estado: "en-curso",
  tags: ["revision"],
  extra: { "año": anio },
});
-%>
# 🎇 Revisión anual — <% anio %>

> Última semana de diciembre. Incluye el plan del año siguiente.

## 1 · El año en retrospectiva

**5 logros del año:**
1.
2.
3.
4.
5.

**3 cosas que dejaría de hacer si volviera a empezar el año:**
1.
2.
3.

**¿Qué aprendí sobre cómo trabajo?** (revisa las notas tipo `aprendizaje` y `error`)

```dataview
LIST
WHERE (tipo = "aprendizaje" OR tipo = "error") AND dateformat(date(creado), "yyyy") = string(this.año)
LIMIT 30
```

## 2 · Áreas de vida (1–10 y una frase)

| Área | Nota | ¿Qué cambiaría? |
| --- | --- | --- |
| Investigación / publicaciones |  |  |
| Docencia |  |  |
| Finanzas |  |  |
| Salud / energía |  |  |
| Relaciones |  |  |
| Aprendizaje (inglés, mates, código) |  |  |

## 3 · Plan del próximo año

**Tema del año (una frase que quepa en un post-it):**
-

**3 objetivos anuales** (crear con `Alt+N` → `objetivo`, plazo diciembre):
1.
2.
3.

## 4 · Limpieza anual del sistema

- [ ] Archivar proyectos muertos (estado → `archivado`)
- [ ] Vaciar `algun-dia` de todo lo que ya no resuena
- [ ] Revisar [[mantenimiento]] y dejar la bandeja a cero

> Al terminar: `estado: hecho`.
