<%*
/* Plan diario — se aplica solo al crear la nota diaria (carpeta 07 diary).
   La fecha se toma del NOMBRE del archivo (YYYY-MM-DD), así funciona
   igual si abres la nota de hoy, de ayer o de mañana. */
const valida = window.moment(tp.file.title, "YYYY-MM-DD", true).isValid();
const fecha = valida ? tp.file.title : tp.date.now("YYYY-MM-DD");
const f = window.moment(fecha, "YYYY-MM-DD");
tR += tp.user.frontmatter(tp, {
  tipo: "plan-diario",
  estado: "en-curso",
  tags: ["plan"],
  extra: {
    fecha: fecha,
    dia: f.format("dddd"),
    energia_manana: '""',
    energia_tarde: '""',
    energia_noche: '""',
    "sueño_horas": '""',
  },
});
-%>
# 📅 Plan del día — <% f.format("dddd D [de] MMMM") %>

> ⏱️ **Planificar toma 10 minutos, no 2 horas.** Rellena las 3 prioridades,
> exporta a Super Productivity y EMPIEZA. El resto del documento se llena solo.

## 🎯 Las 3 prioridades de hoy

> Máximo 3. Si surge algo más durante el día: `Alt+C` (captura) y sigues trabajando.

- [ ]
- [ ]
- [ ]

### 📤 Exportar a Super Productivity (automático)

```dataviewjs
await dv.view("meta/integrations/super-productivity/exportar-sp", { origen: "actual" });
```

---

## 🧠 Contexto (automático — solo leer, no organizar)

### 📌 Tareas no completadas de ayer

```dataview
TASK
FROM "07 diary"
WHERE tipo = "plan-diario" AND fecha = date(this.fecha) - dur(1 day) AND !completed
```

### 📥 Bandeja (si hay algo urgente, súbelo a prioridad; el resto espera a las 20:20)

```dataviewjs
await dv.view("meta/capture/bandeja", { limite: 10 });
```

---

## ⏱️ Bloques del día

> Referencia de la rutina base. La ejecución vive en Super Productivity.

| Hora  | Bloque                                | Etiqueta(s)         | Hecho |
| ----- | ------------------------------------- | ------------------- | ----- |
| 06:00 | Despertar y activación                | #rutina             | [ ]   |
| 06:20 | Ejercicio                             | #ejercicio          | [ ]   |
| 06:50 | Ducha y desayuno                      | #rutina             | [ ]   |
| 07:20 | Plan diario express                   | #seguimiento        | [ ]   |
| 07:30 | Deep Work 1 — Investigación/Economía  | #estudio #economia  | [ ]   |
| 09:20 | Programación / Linux (tope fijo)      | #python #linux      | [ ]   |
| 10:40 | Mecanografía                          | #mecanografia       | [ ]   |
| 10:55 | Correo y admin                        | #admin              | [ ]   |
| 11:15 | Lectura de papers (Zotero)            | #zotero #lectura    | [ ]   |
| 12:10 | Almuerzo                              | #rutina             | [ ]   |
| 13:10 | Docencia                              | #clase #docencia    | [ ]   |
| 14:55 | Inglés                                | #ingles #duolingo   | [ ]   |
| 15:40 | Matemáticas / estadística             | #estadistica        | [ ]   |
| 16:40 | Lectura de libros                     | #lectura            | [ ]   |
| 17:40 | Proyecto personal                     | #proyecto           | [ ]   |
| 18:40 | Cena                                  | #rutina             | [ ]   |
| 19:20 | Tiempo libre                          | #descanso           | [ ]   |
| 20:20 | Procesar bandeja (`Alt+B`)            | #seguimiento        | [ ]   |
| 21:00 | Cierre del día (abajo)                | #seguimiento        | [ ]   |
| 23:00 | Dormir                                | #salud              | [ ]   |

---

## 🚧 ¿Bloqueador previsto hoy?

- Gatillo probable: ☐ overwhelm ☐ perfeccionismo ☐ falta de claridad ☐ aburrimiento ☐ miedo ☐ distracción ☐ baja energía ☐ resistencia
- Estrategia si aparece:

---

## 🌙 Cierre del día (21:00 — esta ES la revisión diaria, 10 min máximo)

**¿Qué hice?**
-

**¿Qué aprendí?** (si es grande → `Alt+N` → plantilla `aprendizaje`)
-

**¿Qué interrumpió mi foco?**
-

**UNA cosa a mejorar mañana:**
-

**Energía del día (1–10):**

> Al terminar: cambia `estado: en-curso` → `estado: hecho` en Properties
> y rellena `energia_*` y `sueño_horas`.
