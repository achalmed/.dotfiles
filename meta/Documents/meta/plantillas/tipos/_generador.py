"""meta/plantillas/tipos/_generador.py — genera las 27 plantillas de tipo de nota desde una sola especificación.

Objetivo: que las plantillas de meta/plantillas/tipos/ tengan estructura y metadata
  idénticas: se escriben aquí una vez y se regeneran (`python3 _generador.py`).
Método: un diccionario tipo → (emoji, estado, extra, cuerpo) y una plantilla Templater
  común que llama a titular.js, frontmatter.js y archivar.js.
Fundamento: meta/NORMATIVA_ARCHIVOS.md §1 (claves snake_case), §2.1 (estados), §10.4 (la
  primera etiqueta es el tipo y la pone el generador); fase M3 2026-09-15.
Límite: no toca planes/ ni revisiones/, que tienen lógica de fecha propia.
"""
from pathlib import Path

ETIQUETAS = {'idea': 'Idea', 'nota': 'Nota', 'investigacion': 'Investigación', 'proyecto': 'Proyecto', 'persona': 'Persona', 'libro': 'Libro', 'articulo': 'Artículo', 'paper': 'Paper', 'video': 'Video', 'clase': 'Clase', 'reunion': 'Reunión', 'sueno': 'Sueño', 'reflexion': 'Reflexión', 'decision': 'Decisión', 'problema': 'Problema', 'hipotesis': 'Hipótesis', 'experimento': 'Experimento', 'aprendizaje': 'Aprendizaje', 'error': 'Error', 'checklist': 'Checklist', 'objetivo': 'Objetivo', 'rutina': 'Rutina', 'habito': 'Hábito', 'bitacora': 'Bitácora', 'tarea': 'Tarea', 'algun-dia': 'Algún día', 'referencia': 'Referencia'}

# Ruta relativa al propio archivo, no absoluta: este script YA vive en
# plantillas/tipos/, así que Path(__file__).parent es esa misma carpeta (destino
# de las plantillas). Funciona igual desde el repo (~/.dotfiles/meta/…) o desde
# el vault (~/Documents/meta/…) sin editar nada.
DESTINO = Path(__file__).resolve().parent

# nombre → (emoji, estado, tags, extra_dict, cuerpo)
# `tags` va vacío a propósito: frontmatter.js antepone el tipo (§10.4) y las demás
# etiquetas (`tema/<slug>`, `proyecto/<id>`) las pone el autor. Se retiraron los
# sinónimos en inglés (task, project, person, source, diary), que solo servían a
# Auto Note Mover, y ninguna nota de plantilla se mueve sola (AutoNoteMover: disable).
TIPOS = {
    "idea": ("💡", "bandeja", [], {},
"""## La idea

-

## ¿Por qué importa?

-

## Siguiente acción (si no hay ninguna, en la revisión pasa a `estado: algun_dia`)

- [ ] """),

    "nota": ("📝", "bandeja", [], {},
"""- """),

    "investigacion": ("🔬", "activo", [], {"pregunta": '""', "proyecto": '""'},
"""## Pregunta de investigación

-

## Hallazgos

-

## Fuentes

-

## Siguiente acción

- [ ] """),

    "proyecto": ("🗂️", "activo", [], {"objetivo": '""', "fecha_limite": '""', "esperando": '""'},
"""## Objetivo (¿cómo se ve TERMINADO?)

-

## ⏭️ Siguiente acción (siempre debe haber UNA sin marcar)

- [ ]

## Tareas

- [ ]

## Registro

- <% tp.date.now("YYYY-MM-DD") %> — creado."""),

    "persona": ("👤", "activo", [], {"relacion": '""', "contacto": '""'},
"""## Quién es

-

## Temas en común / pendientes con esta persona

- [ ] """),

    "libro": ("📖", "bandeja", [], {"autor": '""', "anio": '""', "estado_lectura": "por_leer"},
"""## ¿Por qué leerlo?

-

## Notas

-

## Citas

> """),

    "articulo": ("📰", "bandeja", [], {"autor": '""', "url": '""'},
"""## Idea central

-

## Notas

- """),

    "paper": ("📄", "bandeja", [], {"autor": '""', "anio": '""', "doi": '""', "clave_bibtex": '""'},
"""## Tesis / aporte

-

## Método

-

## Notas

-

## ¿Citarlo en…?

- """),

    "video": ("🎬", "bandeja", [], {"canal": '""', "url": '""'},
"""## Idea central

-

## Notas (con minuto)

- """),

    "clase": ("🎓", "activo", [], {"curso": '""', "fecha_clase": '""'},
"""## Objetivo de la sesión

-

## Contenido / guion

-

## Materiales

-

## Tareas derivadas

- [ ] """),

    "reunion": ("🤝", "activo", [], {"con": '""', "fecha_reunion": '""'},
"""## Agenda

-

## Notas

-

## Acuerdos → tareas (procesar al terminar)

- [ ] """),

    "sueno": ("🌙", "hecho", [], {},
"""## El sueño

-

## Emociones / posibles disparadores

- """),

    "reflexion": ("🪞", "hecho", [], {},
"""## ¿Qué pasó / qué estoy pensando?

-

## ¿Qué hago con esto? (nada también es respuesta válida)

- """),

    "decision": ("⚖️", "activo", [], {"fecha_limite": '""'},
"""## ¿Qué hay que decidir?

-

## Opciones y costo de cada una

1.

## Criterio de decisión

-

## ✅ Decisión tomada y por qué

-

## Revisión (¿fue buena? — completar después)

- """),

    "problema": ("🧩", "activo", [], {"proyecto": '""'},
"""## Síntoma (qué se observa)

-

## Causa probable

-

## Posibles soluciones

-

## Siguiente acción

- [ ] """),

    "hipotesis": ("🧪", "activo", [], {},
"""## Enunciado (si X, entonces Y, porque Z)

-

## ¿Cómo probarla / refutarla?

-

## Evidencia a favor / en contra

- """),

    "experimento": ("⚗️", "activo", [], {"hipotesis": '""', "inicio": '""', "fin": '""'},
"""## Diseño (qué se cambia, qué se mide)

-

## Resultado

-

## Aprendizaje

- """),

    "aprendizaje": ("🌱", "hecho", [], {"fuente": '""'},
"""## ¿Qué aprendí?

-

## ¿Dónde lo aplico?

- """),

    "error": ("🐞", "hecho", [], {"proyecto": '""'},
"""## ¿Qué salió mal?

-

## Causa raíz

-

## ¿Cómo evitarlo la próxima vez?

- """),

    "checklist": ("☑️", "activo", [], {},
"""## Pasos

- [ ] """),

    "objetivo": ("🎯", "activo", [], {"plazo": '""', "metrica": '""'},
"""## Resultado esperado (medible)

-

## ¿Por qué importa?

-

## Hitos

- [ ] """),

    "rutina": ("🔁", "activo", [], {"horario": '""'},
"""## Pasos (en orden, sin decisiones)

1. """),

    "habito": ("🌿", "activo", [], {"disparador": '""', "recompensa": '""'},
"""## Hábito (versión mínima viable: tan fácil que no puedas fallar)

-

## Registro

- <% tp.date.now("YYYY-MM-DD") %> — inicio."""),

    "bitacora": ("📓", "activo", [], {"proyecto": '""'},
"""## <% tp.date.now("YYYY-MM-DD") %>

- """),

    "tarea": ("✅", "siguiente", [], {"proyecto": '""', "fecha_limite": '""', "sp_est": "30m"},
"""## Descripción

- [ ]

> Para ejecutarla en Super Productivity: aparece en el exportador del
> plan diario y de [[semana]] mientras `estado` sea `siguiente` o `activo`."""),

    "algun-dia": ("🌤️", "algun_dia", [], {},
"""## ¿Qué es?

-

## ¿Qué tendría que pasar para activarlo?

-

> Se revisa solo: aparece en la revisión mensual. No pienses más en esto hoy."""),

    "referencia": ("🔗", "activo", [], {"url": '""', "fuente": '""'},
"""## ¿Para qué sirve?

-

## Contenido / extracto

- """),
}

# tipo que declara la nota (la plantilla algun-dia crea una `idea` en estado `algun_dia`,
# porque §2.1 solo admite ese estado en idea|tarea; el destino de archivar sigue siendo el suyo)
TIPO_DECLARADO = {"algun-dia": "idea"}

PLANTILLA = """<%*
const titulo = await tp.user.titular(tp, "{etiqueta}");
tR += tp.user.frontmatter(tp, {{ tipo: "{tipo}", titulo: titulo, estado: "{estado}", tags: [{tags}], extra: {{{extra}}} }});
await tp.user.archivar(tp, "{nombre}");
-%>
# {emoji} <% titulo %>

{cuerpo}
"""

DESTINO.mkdir(parents=True, exist_ok=True)
for nombre, (emoji, estado, tags, extra, cuerpo) in TIPOS.items():
    contenido = PLANTILLA.format(
        nombre=nombre,
        tipo=TIPO_DECLARADO.get(nombre, nombre),
        etiqueta=ETIQUETAS[nombre],
        emoji=emoji,
        estado=estado,
        tags=", ".join(f'"{t}"' for t in tags),
        extra=", ".join(f'{k}: {v}' for k, v in extra.items()),
        cuerpo=cuerpo,
    )
    (DESTINO / f"{nombre}.md").write_text(contenido)
    print(f"✓ {nombre}.md")
print(f"\n{len(TIPOS)} plantillas generadas en {DESTINO}")
