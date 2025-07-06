#!/bin/bash

# Directorio de los dotfiles
DOTFILES_DIR="$HOME/dotfiles"

# Verifica si Stow está instalado
if ! command -v stow &> /dev/null; then
    echo "Error: GNU Stow no está instalado. Instálalo con: sudo apt install stow"
    exit 1
fi

# Crear enlaces simbólicos con Stow y adoptar archivos existentes
cd "$DOTFILES_DIR" || exit
stow -v --adopt git kde shell terminal digikam vscode zotero obsidian calibre libreoffice xournalpp kate texstudio lyx okular rstudio vlc krusader

echo "Dotfiles instalados correctamente!"
