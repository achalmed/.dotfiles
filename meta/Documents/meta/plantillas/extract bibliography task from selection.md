<%*
/* Crea una nota de tarea (tipo: tarea) a partir del texto seleccionado,
   heredando las etiquetas proyecto/<id> de la nota actual en su frontmatter
   (NORMATIVA_ARCHIVOS §6.2 y §10.4; antes eran etiquetas en línea `#task`).
   Nombre de archivo fijo: asignado a un atajo de teclado en la
   configuración de Templater — no renombrar. */
const proyectos = tp.user.etiqueta_proyecto(tp);
const fm = tp.user.frontmatter(tp, { tipo: "tarea", titulo: "new task", estado: "activo", tags: proyectos });
tp.file.create_new(fm + "\n" + tp.file.selection(), "new task");
-%>
