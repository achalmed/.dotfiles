%%Las veinte notas modificadas más recientemente (excluye la infraestructura de "meta"). Se incluye en el workspace "Work-with-notes"; puedes reemplazarla por Backlinks o un Outline si lo prefieres.%%
```dataview
TABLE without ID
	file.link as ""
FROM -"meta"
WHERE file.name != this.file.name 
SORT file.mtime DESC
LIMIT 20
```
