# koreader-data — Respaldo versionado de las lecturas de KOReader

**No es un paquete stow** (no se symlinkea): es el respaldo en texto de los
*datos* de lectura, que el principio de mínima captura excluye de los paquetes
pero que sí queremos versionar para no perder semanas de estadísticas al
cambiar de máquina. Lo actualiza automáticamente
`~/Documents/scripts_for_calibre/script_koreader_estudio` (timer cada 30 min)
con un commit local; se publica con `dotfiles sync-push`.

## Contenido

| Archivo | Qué es | Fuente viva |
|---|---|---|
| `statistics.sql` | dump SQL de las estadísticas de lectura (tiempo, sesiones, páginas) | `~/.config/koreader/settings/statistics.sqlite3` |
| `hashdocsettings/` | todos los sidecars `.sdr` (progreso, estado, marcadores) indexados por hash del contenido del libro | `~/.config/koreader/hashdocsettings/` |
| `history.lua` | historial de documentos abiertos | `~/.config/koreader/history.lua` |

`settings.reader.lua` **no** se respalda aquí: contiene el bloque `kosync`
(credenciales). Las preferencias puras van en el paquete `koreader/`.

## Restaurar en una máquina nueva

```bash
# 1. Instalar KOReader y abrirlo una vez (crea ~/.config/koreader)
# 2. Restaurar estadísticas:
sqlite3 ~/.config/koreader/settings/statistics.sqlite3 < statistics.sql
# 3. Restaurar sidecars y historial:
cp -a hashdocsettings ~/.config/koreader/
cp history.lua ~/.config/koreader/
# 4. En KOReader: Configuración → Documento → Ubicación de metadatos → hash
```

Como sidecars y estadísticas se emparejan por **hash del contenido** de cada
libro (MD5 parcial de KOReader), funcionan aunque la biblioteca cambie de ruta
o de disco.
