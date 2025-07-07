#!/bin/bash
# Verificar datos sensibles en prefs.js
if grep -iE "password|secretKey|apiKey" ~/dotfiles/zotero/.zotero/zotero/25vfdnq5.default/prefs.js; then
    echo "Advertencia: Posibles datos sensibles encontrados en prefs.js. Revisa antes de hacer commit."
    exit 1
else
    echo "No se encontraron datos sensibles en prefs.js."
fi
