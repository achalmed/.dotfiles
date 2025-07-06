# Dotfiles para Kubuntu

Este repositorio contiene mis configuraciones personales (dotfiles) para Kubuntu con KDE Plasma, Zsh y otras herramientas. Uso [GNU Stow](https://www.gnu.org/software/stow/) para gestionar los enlaces simbólicos y Git para sincronizarlos con GitHub.

## Contenido

- **Shell**: Configuración de Zsh (`.zshrc`) y Starship (`starship.toml`) para un prompt personalizado.
- **KDE Plasma**: Configuraciones para el entorno de escritorio, incluyendo:
  - `kdeglobals`: Configuraciones globales de KDE.
  - `dolphinrc`: Configuración del explorador de archivos Dolphin.
  - `kwinrc`: Configuración del gestor de ventanas KWin.
  - `plasma-org.kde.plasma.desktop-appletsrc`: Configuración de paneles y widgets.
  - `plasmarc`: Configuración general del escritorio Plasma.
  - `mimeapps.list`: Asociaciones de aplicaciones predeterminadas.
- **Terminal**: Configuración de Konsole (`konsolerc`).
- **Git**: Configuración global de Git (`.gitconfig`).

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

Instala las dependencias en Kubuntu:
```bash
sudo apt update
sudo apt install stow git zsh
curl -sS https://starship.rs/install.sh | sh
```

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

   El script usa `stow` para crear enlaces simbólicos en tu directorio home.

3. Cambia el shell a Zsh (si no está configurado):
   ```bash
   chsh -s /bin/zsh
   ```

4. (Opcional) Instala Starship si usas el prompt personalizado:
   ```bash
   curl -sS https://starship.rs/install.sh | sh
   ```

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

- **Respaldo**: Antes de instalar en una nueva máquina, haz un respaldo de los archivos existentes en `~/.config/` y `~` para evitar sobrescribir configuraciones importantes.
- **KDE Plasma**: Algunas configuraciones (como `plasma-org.kde.plasma.desktop-appletsrc`) pueden ser específicas del hardware o la versión de Plasma. Verifica la compatibilidad.
- **Datos sensibles**: Revisa `.gitconfig` y otros archivos para evitar subir información sensible (como correos o claves API).

## Contribuir

Este es un repositorio personal, pero si tienes sugerencias, ¡siéntete libre de abrir un issue o un pull request!



