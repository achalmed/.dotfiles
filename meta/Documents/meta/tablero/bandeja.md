---
tipo: tablero
estado: activo
tags: [tablero]
aliases: [Bandeja, Inbox]
---

# 📥 Bandeja universal

> Aquí cae TODO lo capturado. Procesar = decidir, no organizar bonito.
>
> **El diario de capturas del día** (`AAAA-MM-DD Capturas`) se procesa
> sección por sección (`## hora`). Por cada entrada, UNA salida:
>
> 1. **< 2 min** → hazlo ya y borra la sección.
> 2. **Es una acción** → `Alt+T` (va al diario de tareas) y borra la sección.
> 3. **Merece nota propia** (idea, proyecto, paper…) → `Alt+N`, copia el texto y borra la sección. La nota se archiva sola en su carpeta.
> 4. **Algún día / quizá** → `Alt+N` → plantilla `algun-dia`. Reaparece en la revisión mensual.
> 5. **Nada de lo anterior** → **borra la sección**. Es la opción más subestimada.
>
> Cuando el diario quede vacío (o solo con lo ya decidido), cambia su
> `estado: bandeja` → `hecho` y desaparece de aquí.
>
> **Notas sueltas** (creadas fuera del sistema): mismas salidas — o dales
> `tipo`/`estado` en Properties, o bórralas.

## Pendiente de procesar

```dataviewjs
await dv.view("meta/dataview/vistas/bandeja", {});
```

← [[inicio]]
