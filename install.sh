#!/bin/bash

# Directorio de los dotfiles
DOTFILES_DIR="$HOME/dotfiles"

# Verifica si Stow está instalado
if ! command -v stow &> /dev/null; then
    echo "Error: GNU Stow no está instalado. Instálalo con: sudo apt install stow"
    exit 1
fi

# Crear enlaces simbólicos con Stow
cd "$DOTFILES_DIR" || exit
stow -v git
stow -v kde
stow -v shell
stow -v terminal

echo "Dotfiles instalados correctamente!"
