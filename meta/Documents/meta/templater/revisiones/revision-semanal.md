<%*
/* Revisión semanal — incluye el PLAN de la próxima semana (un solo ritual,
   no dos documentos). Calcula sola el rango lunes–domingo de la semana
   que termina: nada de fechas a mano. */
await tp.file.rename(`${tp.date.now("YYYY")}-W${tp.date.now("ww")} Revisión semanal`);
const inicio = window.moment().startOf("isoWeek").format("YYYY-MM-DD");
const fin = window.moment().endOf("isoWeek").format("YYYY-MM-DD");
tR += tp.user.frontmatter(tp, {
  tipo: "revision-semanal",
  estado: "en-curso",
  tags: ["revision"],
  extra: {
    semana: `"${tp.date.now("YYYY")}-W${tp.date.now("ww")}"`,
    fecha_inicio: inicio,
    fecha_fin: fin,
  },
});
-%>
# 🗓️ Revisión semanal — <% inicio %> → <% fin %>

> Domingo 18:00. **Máximo 40 min.** No es para rediseñar el sistema:
> es para vaciar, decidir y elegir UN foco.

## 1 · Vaciar (10 min)

### 📥 Bandeja a cero

```dataviewjs
await dv.view("meta/dataview/vistas/bandeja", {});
```

> Por cada elemento, UNA decisión: hacer ya (<2 min) · `tarea` · `proyecto` ·
> `algun-dia` · referencia · **borrar**. Borrar es la opción por defecto.

## 2 · Mirar la semana que termina (10 min)

### 🏆 3 victorias

1.
2.
3.

### 📈 Energía y sueño (automático)

```dataview
TABLE WITHOUT ID file.link AS "Día", energia_manana AS "Mañana", energia_tarde AS "Tarde", energia_noche AS "Noche", sueño_horas AS "Sueño"
FROM "07 diary"
WHERE tipo = "plan-diario" AND fecha >= date(this.fecha_inicio) AND fecha <= date(this.fecha_fin)
SORT fecha ASC
```

### ✅ Prioridades cumplidas vs pendientes (automático)

```dataview
TASK
FROM "07 diary"
WHERE tipo = "plan-diario" AND fecha >= date(this.fecha_inicio) AND fecha <= date(this.fecha_fin)
GROUP BY file.link
```

### 🚧 ¿Dónde se rompió el sistema?

- Bloque que más se incumplió:
- Gatillo dominante: ☐ overwhelm ☐ perfeccionismo ☐ falta de claridad ☐ aburrimiento ☐ miedo ☐ distracción ☐ baja energía ☐ resistencia
- Ajuste mínimo (no rediseño):

## 3 · Proyectos (10 min)

```dataviewjs
await dv.view("meta/dataview/vistas/proyectos", { wip: 3 });
```

> Proyecto 😴 detenido: decide — reactivar (define siguiente acción),
> `espera` o `algun-dia`. Proyecto 🚫 sin siguiente acción: defínela AHORA.

## 4 · Elegir (10 min)

**LA prioridad de la próxima semana (una sola):**
-

**2–3 tareas de apoyo:**
1.
2.
3.

**A qué digo NO esta semana:**
-

**⚙️ System tweak (UNA mejora pequeña, o ninguna):**
-

> Al terminar: `estado: hecho` en Properties.
