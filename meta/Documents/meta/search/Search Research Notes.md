keyword:: cuba

author:: 
recipient:: 
title:: 
publication:: 
date:: 
archive:: 
archive-location:: 

note-created::
note-modified::
note-title:: 

start-date:: 
end-date:: 
comment:: 
tags:: 

sortby:: start-date
sortorder:: desc

```dataviewjs
await dv.view("meta/search/buscar", {
    fuentes: '"01 notes"',
    detalle: true,
    mensaje: "   Escribe criterios en uno o más campos para buscar notas de investigación.",
});
```

La búsqueda por `keyword` encuentra una palabra o frase en todo el texto de la nota y en su título.
En los campos de texto la búsqueda es por frase, sin distinguir mayúsculas.
Fechas: `YYYY-MM-DD`, `<YYYY-MM-DD` o `>YYYY-MM-DD`.
Etiquetas: `#tag1 #tag2`.
Orden: escribe el nombre exacto del campo en `sortby` y `asc`/`desc` en `sortorder`.
Si se dejan vacíos, se ordena por fecha de modificación descendente.

%%Escribe `cuba` en el campo keyword para encontrar las dos notas de investigación de ejemplo
(ahora en "01 notes/90-ejemplos-vault-original"). Para ver el grafo y los backlinks de una nota
encontrada, haz clic en su título y usa el atajo `Ctrl-N`.%%
