# Dotfiles para Kubuntu

Este repositorio contiene mis configuraciones personales (dotfiles) para Kubuntu con KDE Plasma, Zsh y varias aplicaciones. Uso [GNU Stow](https://www.gnu.org/software/stow/) para gestionar los enlaces simbólicos y Git para sincronizarlos con GitHub.

## Contenido

- **Shell**: Configuración de Zsh (`.zshrc`) y Starship (`starship.toml`) para un prompt personalizado.
- **KDE Plasma**: Configuraciones del entorno de escritorio, incluyendo:
  - `kdeglobals`: Configuraciones globales de KDE.
  - `dolphinrc`: Configuración del explorador de archivos Dolphin.
  - `kwinrc`: Configuración del gestor de ventanas KWin.
  - `plasma-org.kde.plasma.desktop-appletsrc`: Configuración de paneles y widgets.
  - `plasmarc`: Configuración general del escritorio Plasma.
  - `mimeapps.list`: Asociaciones de aplicaciones predeterminadas.
- **Terminal**: Configuración de Konsole (`konsolerc`).
- **Git**: Configuración global de Git (`.gitconfig`).
- **DigiKam**: Configuración de DigiKam (`digikamrc`).
- **Visual Studio Code**: Configuración de VSCode (`settings.json`, `keybindings.json`, `snippets/`).
- **Zotero**: Preferencias de Zotero (`prefs.js`).
- **Obsidian**: Configuración del vault `~/Documents/thoughts` (`.obsidian/`).
- **Calibre**: Configuración de Calibre (`gui.json`, `viewer.json`, etc.).
- **LibreOffice**: Configuración de LibreOffice (`registrymodifications.xcu`, `config/`).
- **Xournal++**: Configuración de Xournal++ (`settings.xml`).
- **Kate**: Configuración del editor Kate (`katerc`, `externaltools/`, `formatting/`, `lspclient/`).
- **TeXstudio**: Configuración de TeXstudio (`texstudio.ini`).
- **LyX**: Configuración de LyX (`preferences`).
- **Okular**: Configuración del visor de PDF Okular (`okularrc`, `okularpartrc`).
- **RStudio**: Configuración de RStudio (`rstudio-prefs.json`).
- **VLC**: Configuración del reproductor VLC (`vlcrc`).
- **Krusader**: Configuración del administrador de archivos Krusader (`krusaderrc`).

## Estructura

```plaintext
~/dotfiles/
├── git/
│   └── .gitconfig
├── kde/
│   └── .config/
│       ├── kdeglobals
│       ├── dolphinrc
│       ├── kwinrc
│       ├── plasma-org.kde.plasma.desktop-appletsrc
│       ├── plasmarc
│       └── mimeapps.list
├── shell/
│   ├── .zshrc
│   └── starship.toml
├── terminal/
│   └── .config/
│       └── konsolerc
├── digikam/
│   └── .config/
│       └── digikamrc
├── vscode/
│   └── .config/
│       ├── settings.json
│       ├── keybindings.json
│       └── snippets/
├── zotero/
│   └── .zotero/zotero/25vfdnq5.default/
│       └── prefs.js
├── obsidian/
│   └── Documents/thoughts/.obsidian/
│       ├── app.json
│       ├── appearance.json
│       ├── community-plugins.json
│       └── ...
├── calibre/
│   └── .config/
│       ├── gui.json
│       ├── viewer.json
│       └── ...
├── libreoffice/
│   └── .config/libreoffice/4/user/
│       ├── registrymodifications.xcu
│       ├── config/
│       └── ...
├── xournalpp/
│   └── .config/
│       └── settings.xml
├── kate/
│   └── .config/
│       ├── katerc
│       ├── externaltools/
│       ├── formatting/
│       └── lspclient/
├── texstudio/
│   └── .config/
│       └── texstudio.ini
├── lyx/
│   └── .config/
│       └── preferences
├── okular/
│   └── .config/
│       ├── okularrc
│       └── okularpartrc
├── rstudio/
│   └── .config/
│       └── rstudio-prefs.json
├── vlc/
│   └── .config/
│       └── vlcrc
├── krusader/
│   └── .config/
│       └── krusaderrc
├── .gitignore
└── install.sh
```

## Requisitos

- **Sistema operativo**: Kubuntu (o cualquier distribución Linux con KDE Plasma).
- **Herramientas**:
  - `stow`: Para gestionar enlaces simbólicos.
  - `git`: Para clonar el repositorio.
  - `zsh`: Shell predeterminado.
  - `starship`: Para el prompt personalizado (opcional).
- **Aplicaciones**: `digikam`, `code`, `zotero`, `obsidian`, `calibre`, `libreoffice`, `xournalpp`, `kate`, `texstudio`, `lyx`, `okular`, `rstudio`, `vlc`, `krusader`.

Instala las dependencias en Kubuntu:
```bash
sudo apt update
sudo apt install stow git zsh digikam code calibre libreoffice xournalpp kate texstudio lyx okular vlc krusader
```
Para Zotero, Obsidian, y RStudio, descárgalos desde sus sitios oficiales:
- Zotero: [www.zotero.org](https://www.zotero.org)
- Obsidian: [obsidian.md](https://obsidian.md)
- RStudio: [rstudio.com](https://rstudio.com)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/achalmed/.dotfiles.git ~/dotfiles
   ```

2. Ejecuta el script de instalación:
   ```bash
   cd ~/dotfiles
   ./install.sh
   ```

3. Cambia el shell a Zsh (si no está configurado):
   ```bash
   chsh -s /bin/zsh
   ```

4. (Opcional) Instala Starship si usas el prompt personalizado:
   ```bash
   curl -sS https://starship.rs/install.sh | sh
   ```

5. (Opcional) Instala extensiones de VSCode:
   ```bash
   code --list-extensions > ~/dotfiles/vscode/extensions.txt
   while read -r line; do code --install-extension "$line"; done < ~/dotfiles/vscode/extensions.txt
   ```

6. (Opcional) Configura el vault de Obsidian:
   Asegúrate de que el vault esté en `~/Documents/thoughts` antes de ejecutar `stow`.

## Actualizar dotfiles

1. Modifica los archivos en `~/dotfiles` o en tu directorio home (los enlaces simbólicos se actualizarán automáticamente).
2. Confirma y sube los cambios a GitHub:
   ```bash
   cd ~/dotfiles
   git add .
   git commit -m "Actualizar dotfiles"
   git push
   ```

## Notas

- **Respaldo**: Antes de instalar en una nueva máquina, haz un respaldo de los archivos existentes en `~/.config/`, `~/.zotero/`, `~/.lyx/`, y `~/Documents/thoughts/.obsidian/` para evitar sobrescribir configuraciones importantes.
- **KDE Plasma**: Algunas configuraciones (como `plasma-org.kde.plasma.desktop-appletsrc`) pueden ser específicas del hardware o la versión de Plasma. Verifica la compatibilidad.
- **Zotero**: Evita incluir `zotero.sqlite` o archivos de caché. Revisa `prefs.js` para datos sensibles.
- **Obsidian**: Asegúrate de que el vault esté en `~/Documents/thoughts` en todas las máquinas.
- **Datos sensibles**: Revisa `.gitconfig`, `prefs.js` (Zotero), y `registrymodifications.xcu` (LibreOffice) para evitar subir información sensible.

## Contribuir

Este es un repositorio personal, pero si tienes sugerencias, ¡siéntete libre de abrir un issue o un pull request!


1. **Guarda el `README.md`**:
   ```bash
   nano ~/dotfiles/README.md
   ```
   Copia el contenido, guarda, y confirma:
   ```bash
   git add README.md
   git commit -m "Actualizar README.md con configuraciones confirmadas"
   git push
   ```
