<%*
/* Revisión mensual — incluye el plan del mes siguiente. */
const mes = tp.date.now("YYYY-MM");
await tp.file.rename(`${mes} Revisión mensual`);
tR += tp.user.frontmatter(tp, {
  tipo: "revision-mensual",
  estado: "en-curso",
  tags: ["revision"],
  extra: { mes: `"${mes}"` },
});
-%>
# 📆 Revisión mensual — <% mes %>

> Último domingo del mes, después de la semanal. **Máximo 45 min.**

## 1 · Objetivos: ¿avanzaron?

```dataview
TABLE WITHOUT ID file.link AS "Objetivo", plazo AS "Plazo", metrica AS "Métrica", estado AS "Estado"
WHERE tipo = "objetivo" AND estado != "archivado"
```

> Por cada uno: sigue · ajustar · **matar** (archivar sin culpa).

## 2 · Algún día: ¿algo despertó?

```dataview
LIST
WHERE estado = "algun-dia"
```

> Activa como máximo UNO. El resto sigue durmiendo (o se borra).

## 3 · Revisiones semanales del mes (automático)

```dataview
TABLE WITHOUT ID file.link AS "Semana", estado AS "Estado"
WHERE tipo = "revision-semanal" AND dateformat(date(creado), "yyyy-MM") = this.mes
```

## 4 · Números del mes

| Área | Resultado | Nota |
| --- | --- | --- |
| 📖 Libros |  |  |
| 📄 Papers |  |  |
| ✍️ Publicaciones (blogs) |  |  |
| 🎓 Clases |  |  |
| 💰 GnuCash al día | ☐ Sí ☐ No |  |

## 5 · Plan del próximo mes

**Tema del mes (una frase):**
-

**3 resultados concretos:**
1.
2.
3.

**Qué NO haré este mes:**
-

> Al terminar: `estado: hecho`.
