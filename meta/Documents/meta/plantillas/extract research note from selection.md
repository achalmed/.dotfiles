<%*
/* Extrae la selección (una anotación de Zotero) a una nota de investigación
   nueva: copia el encabezado de la nota actual con el número de página
   actualizado, pide un título y deja un enlace [[...]] en el lugar de origen.
   Nombre de archivo fijo: asignado a un atajo de teclado en la
   configuración de Templater — no renombrar. */

const fileName = await tp.system.prompt("New Note Title", "Type your title here", true);

tp.file.create_new(tp.user.encabezado(tp)+tp.file.selection(), fileName, false);

await tp.file.cursor_append("[["+fileName+"]]");

%>