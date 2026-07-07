# Genera las plantillas de tipos de meta/templater/tipos/ desde una sola
# especificación, garantizando estructura y metadata idénticas en todas.
import os

ETIQUETAS = {'idea': 'Idea', 'nota': 'Nota', 'investigacion': 'Investigación', 'proyecto': 'Proyecto', 'persona': 'Persona', 'libro': 'Libro', 'articulo': 'Artículo', 'paper': 'Paper', 'video': 'Video', 'clase': 'Clase', 'reunion': 'Reunión', 'sueno': 'Sueño', 'reflexion': 'Reflexión', 'decision': 'Decisión', 'problema': 'Problema', 'hipotesis': 'Hipótesis', 'experimento': 'Experimento', 'aprendizaje': 'Aprendizaje', 'error': 'Error', 'checklist': 'Checklist', 'objetivo': 'Objetivo', 'rutina': 'Rutina', 'habito': 'Hábito', 'bitacora': 'Bitácora', 'tarea': 'Tarea', 'algun-dia': 'Algún día', 'referencia': 'Referencia'}

DESTINO = "/home/achalmaedison/Documents/meta/templater/tipos"

# nombre → (emoji, estado, tags, extra_dict, cuerpo)
TIPOS = {
    "idea": ("💡", "bandeja", ["idea"], {},
"""## La idea

-

## ¿Por qué importa?

-

## Siguiente acción (si no hay ninguna, en la revisión pasa a `algun-dia`)

- [ ] """),

    "nota": ("📝", "bandeja", ["nota"], {},
"""- """),

    "investigacion": ("🔬", "activo", ["investigacion"], {"pregunta": '""', "proyecto": '""'},
"""## Pregunta de investigación

-

## Hallazgos

-

## Fuentes

-

## Siguiente acción

- [ ] """),

    "proyecto": ("🗂️", "activo", ["project"], {"objetivo": '""', "fecha_limite": '""', "esperando": '""'},
"""## Objetivo (¿cómo se ve TERMINADO?)

-

## ⏭️ Siguiente acción (siempre debe haber UNA sin marcar)

- [ ]

## Tareas

- [ ]

## Registro

- <% tp.date.now("YYYY-MM-DD") %> — creado."""),

    "persona": ("👤", "activo", ["person"], {"relacion": '""', "contacto": '""'},
"""## Quién es

-

## Temas en común / pendientes con esta persona

- [ ] """),

    "libro": ("📖", "bandeja", ["source", "libro"], {"autor": '""', "año": '""', "estado_lectura": "por-leer"},
"""## ¿Por qué leerlo?

-

## Notas

-

## Citas

> """),

    "articulo": ("📰", "bandeja", ["source", "articulo"], {"autor": '""', "url": '""'},
"""## Idea central

-

## Notas

- """),

    "paper": ("📄", "bandeja", ["source", "paper"], {"autor": '""', "año": '""', "doi": '""', "citekey": '""'},
"""## Tesis / aporte

-

## Método

-

## Notas

-

## ¿Citarlo en…?

- """),

    "video": ("🎬", "bandeja", ["source", "video"], {"canal": '""', "url": '""'},
"""## Idea central

-

## Notas (con minuto)

- """),

    "clase": ("🎓", "activo", ["clase"], {"curso": '""', "fecha_clase": '""'},
"""## Objetivo de la sesión

-

## Contenido / guion

-

## Materiales

-

## Tareas derivadas

- [ ] """),

    "reunion": ("🤝", "activo", ["reunion"], {"con": '""', "fecha_reunion": '""'},
"""## Agenda

-

## Notas

-

## Acuerdos → tareas (procesar al terminar)

- [ ] """),

    "sueno": ("🌙", "hecho", ["diary", "sueño"], {},
"""## El sueño

-

## Emociones / posibles disparadores

- """),

    "reflexion": ("🪞", "hecho", ["diary", "reflexion"], {},
"""## ¿Qué pasó / qué estoy pensando?

-

## ¿Qué hago con esto? (nada también es respuesta válida)

- """),

    "decision": ("⚖️", "activo", ["decision"], {"fecha_limite": '""'},
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

    "problema": ("🧩", "activo", ["problema"], {"proyecto": '""'},
"""## Síntoma (qué se observa)

-

## Causa probable

-

## Posibles soluciones

-

## Siguiente acción

- [ ] """),

    "hipotesis": ("🧪", "activo", ["hipotesis"], {},
"""## Enunciado (si X, entonces Y, porque Z)

-

## ¿Cómo probarla / refutarla?

-

## Evidencia a favor / en contra

- """),

    "experimento": ("⚗️", "activo", ["experimento"], {"hipotesis": '""', "inicio": '""', "fin": '""'},
"""## Diseño (qué se cambia, qué se mide)

-

## Resultado

-

## Aprendizaje

- """),

    "aprendizaje": ("🌱", "hecho", ["aprendizaje"], {"fuente": '""'},
"""## ¿Qué aprendí?

-

## ¿Dónde lo aplico?

- """),

    "error": ("🐞", "hecho", ["error"], {"proyecto": '""'},
"""## ¿Qué salió mal?

-

## Causa raíz

-

## ¿Cómo evitarlo la próxima vez?

- """),

    "checklist": ("☑️", "activo", ["checklist"], {},
"""## Pasos

- [ ] """),

    "objetivo": ("🎯", "activo", ["objetivo"], {"plazo": '""', "metrica": '""'},
"""## Resultado esperado (medible)

-

## ¿Por qué importa?

-

## Hitos

- [ ] """),

    "rutina": ("🔁", "activo", ["rutina"], {"horario": '""'},
"""## Pasos (en orden, sin decisiones)

1. """),

    "habito": ("🌿", "activo", ["habito"], {"disparador": '""', "recompensa": '""'},
"""## Hábito (versión mínima viable: tan fácil que no puedas fallar)

-

## Registro

- <% tp.date.now("YYYY-MM-DD") %> — inicio."""),

    "bitacora": ("📓", "activo", ["bitacora"], {"proyecto": '""'},
"""## <% tp.date.now("YYYY-MM-DD") %>

- """),

    "tarea": ("✅", "siguiente", ["task"], {"proyecto": '""', "fecha_limite": '""', "sp_est": "30m"},
"""## Descripción

- [ ]

> Para ejecutarla en Super Productivity: aparece en el exportador del
> plan diario y de [[semana]] mientras `estado` sea `siguiente` o `activo`."""),

    "algun-dia": ("🌤️", "algun-dia", ["algun-dia"], {},
"""## ¿Qué es?

-

## ¿Qué tendría que pasar para activarlo?

-

> Se revisa solo: aparece en la revisión mensual. No pienses más en esto hoy."""),

    "referencia": ("🔗", "activo", ["referencia"], {"url": '""', "fuente": '""'},
"""## ¿Para qué sirve?

-

## Contenido / extracto

- """),
}

PLANTILLA = """<%*
const titulo = await tp.user.titular(tp, "{etiqueta}");
tR += tp.user.frontmatter(tp, {{ tipo: "{nombre}", estado: "{estado}", tags: [{tags}], extra: {{{extra}}} }});
-%>
# {emoji} <% titulo %>

{cuerpo}
"""

os.makedirs(DESTINO, exist_ok=True)
for nombre, (emoji, estado, tags, extra, cuerpo) in TIPOS.items():
    contenido = PLANTILLA.format(
        nombre=nombre,
        etiqueta=ETIQUETAS[nombre],
        emoji=emoji,
        estado=estado,
        tags=", ".join(f'"{t}"' for t in tags),
        extra=", ".join(f'{k}: {v}' for k, v in extra.items()),
        cuerpo=cuerpo,
    )
    with open(os.path.join(DESTINO, f"{nombre}.md"), "w") as f:
        f.write(contenido)
    print(f"✓ {nombre}.md")
print(f"\n{len(TIPOS)} plantillas generadas en {DESTINO}")
