<%*
/* Crea una nota de tarea (#task) a partir del texto seleccionado,
   heredando las etiquetas #project de la nota actual.
   Nombre de archivo fijo: asignado a un atajo de teclado en la
   configuración de Templater — no renombrar. */
tp.file.create_new('#task \n'+tp.user.etiqueta_proyecto(tp)+'\n\n'+ tp.file.selection(), "new task");
-%>