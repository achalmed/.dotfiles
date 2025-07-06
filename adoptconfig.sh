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
stow -v --adopt git
stow -v --adopt kde
stow -v --adopt shell
stow -v --adopt terminal

echo "Dotfiles instalados correctamente!"
