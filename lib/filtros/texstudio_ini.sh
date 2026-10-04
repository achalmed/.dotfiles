#!/usr/bin/env bash
# lib/filtros/texstudio_ini.sh — filtro «clean» de git para texstudio/.config/texstudio/texstudio.ini
#
# TeXstudio guarda en el mismo .ini las preferencias (que se versionan) y el estado de uso:
# últimos archivos abiertos, último documento, carpeta de colaboración y último directorio.
# Esas claves llevan rutas privadas de la máquina y no deben salir del disco. Git pasa el
# archivo por aquí al prepararlo (`git add`): lo que se confirma ya no las tiene; la copia en
# disco queda intacta. Se activa con `.gitattributes` más
#   git config filter.texstudio-ini.clean 'bash lib/filtros/texstudio_ini.sh'
# (lo hace `./main.sh instalar`; en un clon nuevo, repetirlo una vez).
set -euo pipefail
grep -v -E '^(Files\\(Last%20Document|Recent%20Files|Recent%20Files%20Highlighting|Recent%20Project%20Files|Recent%20Session%20Files)|CollaborativeEditing\\ClientFolder|qttwp\\lastdir)=' || true
