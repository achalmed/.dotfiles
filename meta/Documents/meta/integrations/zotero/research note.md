---
id: {{importDate | format("YYYYMMDDHHmmss")}}
tipo: lectura
titulo: "{{title | replace('"', '\\"')}}"
estado: bandeja
creado: {{importDate | format("YYYY-MM-DD")}}
tags: [lectura{% for t in tags %}, {% if t.tag == "secondary" or t.tag == "primary" %}fuente/{{t.tag}}{% elif "-project" in t.tag %}proyecto/{{t.tag | lower | replace(" ", "-") | replace("-project", "")}}{% else %}tema/{{t.tag | lower | replace(" ", "-")}}{% endif %}{% endfor %}]
aliases: []
AutoNoteMover: disable
cssclasses: [research-note]
calibre_id:
zotero_key: {{desktopURI | replace("zotero://select/library/items/", "")}}
clave_bibtex: {{citekey}}
tipo_zotero: {{itemType}}{% for type, creators in creators | groupby("creatorType") %}
{{type | replace("interviewee", "author") | replace("director", "author") | replace("presenter", "author") | replace("podcaster", "author") | replace("programmer", "author") | replace("cartographer", "author") | replace("inventor", "author") | replace("sponsor", "author") | replace("performer", "author") | replace("artist", "author") | replace("author", "autor") | replace("translator", "traductor")}}: "{%- for creator in creators -%}{%- if creator.name %}{{creator.name}}{%- else %}{{creator.lastName}}, {{creator.firstName}}{%- endif %}{% if not loop.last %}; {% endif %}{% endfor %}"{%- endfor %}{% if publicationTitle %}
publicacion: "{{publicationTitle}}"{% endif %}{% if date %}
publicado: {{date | format("YYYY-MM-DD")}}{% endif %}{% if archive %}
archivo: "{{archive}}"{% endif %}{% if archiveLocation %}
archivo_ubicacion: "{{archiveLocation}}"{% endif %}
---
%% meta/integrations/zotero/research note.md — plantilla de Zotero Integration (Ctrl+R): nota de lectura
   con el frontmatter único del vault (NORMATIVA_ARCHIVOS §6.2, §10.5; fase M3 2026-09-15).
   `calibre_id` lo rellena el autor: la obra vive en Calibre y Zotero solo apunta a ella (§1.1).
   Las etiquetas de Zotero entran como `tema/<slug>` o `proyecto/<id>` (§10.4). %%
{{bibliography}}
[online]({{uri}}) [local]({{desktopURI}}) {%- for attachment in attachments | filterby("path", "endswith", ".pdf") %} [pdf](file://{{attachment.path | replace(" ", "%20")}})
{%- endfor %}

### Índice

fecha_inicio:: {% if date %}{{date | format("YYYY-MM-DD")}}{% endif %}
fecha_fin::
pagina:: {% for annotation in annotations %}{% if loop.first %}{{annotation.pageLabel}}{% endif %}{% endfor %}

### Conexiones

comentario::

### Note
{% macro calloutHeader(color) -%}
{%- if color == "#ff6666" -%}
Importante
{%- endif -%}
{%- if color == "#5fb236" -%}
Referencia
{%- endif -%}
{%- if color == "#2ea8e5" -%}
Sin definir - azul
{%- endif -%}
{%- if color == "#a28ae5" -%}
Sin definir - morado
{%- endif -%}
{%- endmacro -%}

{% persist "annotations" %}
{% set annotations = annotations | filterby("date", "dateafter", lastImportDate) -%}
{% if annotations.length > 0 %}
### Importado el {{importDate | format("YYYY-MM-DD HH:mm")}}

{%- for annotation in annotations %}
{% if annotation.color !== "#ffd400" %}
>[!quote{% if annotation.color %}|{{annotation.color}}{% endif %}] {{calloutHeader(annotation.color)}}
>{%- endif -%}{% if annotation.imageRelativePath %}
![[{{annotation.imageRelativePath}}]] {% endif %}{% if annotation.annotatedText %}
{{annotation.annotatedText}} [(p. {{annotation.pageLabel}})](zotero://open-pdf/library/items/{{annotation.attachment.itemKey}}?page={{annotation.pageLabel}}&annotation={{annotation.id}}){%- endif %}{%- if annotation.comment%}
%%{{annotation.comment}}%%{%- endif %}{%- endfor %}{% endif %} {% endpersist %}
