# ====================================================
#  Información
# ====================================================
# ~/.zshrc — configuración interactiva de Zsh
# Gestionado por el repo de dotfiles (~/.dotfiles/shell/.zshrc, symlink).
# Objetivos: arranque rápido, carga condicional (solo se activa lo que está
# instalado) y compatibilidad Arch Linux / Kubuntu.
#
# Decisiones clave:
#   - Oh My Zsh sigue siendo el framework base (tema robbyrussell salvo que
#     Starship esté instalado, en cuyo caso Starship toma el prompt).
#   - Conda se carga en diferido (lazy): su hook costaba ~1.8 s por shell.
#     Pon DOTFILES_CONDA_LAZY=0 antes de este bloque para volver al modo clásico.
#   - Las integraciones de herramientas modernas (fzf, zoxide, eza, bat, fd,
#     direnv, atuin, mise, fnm, cargo, go, sdkman…) se activan solas si la
#     herramienta aparece en el sistema; no requieren editar este archivo.
#   - Extensiones locales de la máquina: ~/.zshrc.local (no versionado).

# ====================================================
#  Variables de entorno
# ====================================================
# --- Sistema ---
# Solo se fija LANG si el sistema no lo definió ya (respeta la configuración
# de locale de KDE / /etc/default/locale).
: "${LANG:=es_ES.UTF-8}"
export LANG

export EDITOR="nvim"
export VISUAL="$EDITOR"
export PAGER="less"
# -R: respeta colores ANSI; -F: sale si cabe en pantalla; -X: no limpia al salir
export LESS="-RFX"

# ====================================================
#  PATH
# ====================================================
# Helper reutilizable: antepone un directorio al PATH solo si existe.
# (typeset -U al final del archivo garantiza que no haya duplicados.)
_path_prepend() { [[ -d "$1" ]] && path=("$1" $path) }
_path_append()  { [[ -d "$1" ]] && path=($path "$1") }

_path_prepend "$HOME/bin"
_path_prepend "$HOME/.local/bin"

# Anaconda al frente del PATH: preserva que python3/pip/pygmentize sean los de
# conda aunque la inicialización completa sea diferida (ver sección Conda).
_path_prepend "$HOME/anaconda3/bin"

# Toolchains opcionales (solo si existen)
_path_append "$HOME/.cargo/bin"          # Rust
_path_append "$HOME/go/bin"              # Go
_path_append "$HOME/.local/share/pnpm"   # pnpm
_path_append "$HOME/.bun/bin"            # bun

# ====================================================
#  Configuración de Zsh (Oh My Zsh)
# ====================================================
export ZSH="$HOME/.oh-my-zsh"

# Si Starship está instalado él dibuja el prompt; se desactiva el tema de OMZ
# para no cargar dos prompts.
if command -v starship >/dev/null 2>&1; then
  ZSH_THEME=""
else
  ZSH_THEME="robbyrussell"
fi

# Recordatorio de actualización en lugar de preguntar en cada arranque
zstyle ':omz:update' mode reminder
zstyle ':omz:update' frequency 13

# Puntos de espera mientras se calcula un completado largo
COMPLETION_WAITING_DOTS="true"

# --- Plugins (construcción condicional) ---
# Solo se cargan plugins cuya herramienta existe: cada plugin innecesario
# añade tiempo de arranque y aliases muertos.
plugins=(git history command-not-found)

command -v gh        >/dev/null 2>&1 && plugins+=(gh)
command -v python3   >/dev/null 2>&1 && plugins+=(python pip)
command -v node      >/dev/null 2>&1 && plugins+=(node npm)
command -v code      >/dev/null 2>&1 && plugins+=(vscode)
command -v pygmentize >/dev/null 2>&1 && plugins+=(colorize)

# Aliases específicos de la distro (repo compartido Arch/Kubuntu)
if [[ -f /etc/arch-release ]]; then
  plugins+=(archlinux)
elif command -v apt >/dev/null 2>&1; then
  plugins+=(ubuntu)
fi

# z de OMZ solo si no está zoxide (que lo reemplaza, ver su sección)
command -v zoxide >/dev/null 2>&1 || plugins+=(z)

# autosuggestions antes que syntax-highlighting; syntax-highlighting SIEMPRE
# el último (requisito del propio plugin)
[[ -d "$ZSH/custom/plugins/zsh-autosuggestions" ]]     && plugins+=(zsh-autosuggestions)
[[ -d "$ZSH/custom/plugins/zsh-syntax-highlighting" ]] && plugins+=(zsh-syntax-highlighting)

source "$ZSH/oh-my-zsh.sh"

# ====================================================
#  Historial
# ====================================================
# Va después de OMZ para sobrescribir sus valores por defecto.
HISTFILE="$HOME/.zsh_history"
HISTSIZE=100000                   # líneas en memoria
SAVEHIST=100000                   # líneas en disco

setopt EXTENDED_HISTORY           # guarda timestamp y duración de cada comando
setopt SHARE_HISTORY              # historial compartido entre sesiones, escritura inmediata
setopt HIST_IGNORE_ALL_DUPS       # elimina duplicados antiguos al repetir un comando
setopt HIST_IGNORE_SPACE          # comandos con espacio inicial no se guardan (privacidad)
setopt HIST_REDUCE_BLANKS         # normaliza espacios en blanco
setopt HIST_VERIFY                # expandir !! muestra el comando antes de ejecutarlo

# ====================================================
#  Opciones del shell
# ====================================================
setopt AUTO_CD                    # escribir un directorio equivale a cd
setopt AUTO_PUSHD                 # cd apila directorios (navegar atrás con popd / cd -N)
setopt PUSHD_IGNORE_DUPS          # sin duplicados en la pila
setopt CORRECT                    # sugiere corrección de comandos mal escritos
setopt INTERACTIVE_COMMENTS       # permite comentarios # en la línea de comandos
setopt NO_BEEP                    # sin pitidos

# ====================================================
#  Autocompletado
# ====================================================
# compinit ya lo ejecutó OMZ; aquí solo se afina el comportamiento.
zstyle ':completion:*' use-cache yes
zstyle ':completion:*' cache-path "$HOME/.cache/zsh/zcompcache"
zstyle ':completion:*' menu select                          # menú interactivo con flechas
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"     # colores como ls
# Coincidencia insensible a mayúsculas y por subcadena
zstyle ':completion:*' matcher-list 'm:{a-zñ}={A-ZÑ}' 'r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*:descriptions' format '%F{yellow}-- %d --%f'

# ====================================================
#  Aliases
# ====================================================
# --- Archivos y navegación ---
alias ..='cd ..'
alias ...='cd ../..'
alias lt='ls -ltrh'               # por fecha, reciente al final
# (ls/ll/la los define OMZ; eza los redefine en su sección si está instalado)

# --- Sistema (según distro) ---
if [[ -f /etc/arch-release ]]; then
  alias update='sudo pacman -Syu'
  alias limpiar='sudo pacman -Sc && sudo pacman -Rns $(pacman -Qtdq 2>/dev/null)'
elif command -v apt >/dev/null 2>&1; then
  alias update='sudo apt update && sudo apt upgrade'
  alias limpiar='sudo apt autoremove && sudo apt autoclean'
fi

# --- Red ---
alias miip='curl -s ifconfig.me && echo'
alias puertos='ss -tulnp'

# --- Quarto ---
if command -v quarto >/dev/null 2>&1; then
  alias qp='quarto preview'
  alias qr='quarto render'
fi

# (git: el plugin git de OMZ ya provee gst, gco, gaa, glog, etc.)

# ====================================================
#  Funciones
# ====================================================
# mkcd <dir> — crea un directorio (con padres) y entra en él
mkcd() { mkdir -p "$1" && cd "$1" }

# ====================================================
#  Conda (carga diferida)
# ====================================================
# El hook oficial de conda tarda ~1.8 s; era el 95 % del tiempo de arranque.
# Estrategia: anaconda3/bin ya está en el PATH (python/pip funcionan siempre)
# y la inicialización completa se ejecuta solo la primera vez que se invoca
# `conda` (activate, install, etc.). auto_activate_base se respeta en ese
# momento. Para volver al comportamiento clásico: export DOTFILES_CONDA_LAZY=0
if [[ -x "$HOME/anaconda3/bin/conda" ]]; then
  if [[ "${DOTFILES_CONDA_LAZY:-1}" == "1" ]]; then
    conda() {
      unfunction conda
      eval "$("$HOME/anaconda3/bin/conda" shell.zsh hook 2>/dev/null)"
      conda "$@"
    }
  else
    eval "$("$HOME/anaconda3/bin/conda" shell.zsh hook 2>/dev/null)"
  fi
fi

# ====================================================
#  Herramientas modernas (carga condicional)
# ====================================================
# Cada bloque se activa solo si la herramienta está instalada.

# --- fzf: búsqueda difusa (Ctrl-R historial, Ctrl-T archivos, Alt-C cd) ---
if command -v fzf >/dev/null 2>&1; then
  if fzf --zsh >/dev/null 2>&1; then
    eval "$(fzf --zsh)"                                     # fzf >= 0.48
  else
    for _f in /usr/share/fzf/key-bindings.zsh \
              /usr/share/fzf/completion.zsh \
              /usr/share/doc/fzf/examples/key-bindings.zsh \
              /usr/share/doc/fzf/examples/completion.zsh; do
      [[ -f "$_f" ]] && source "$_f"
    done
    unset _f
  fi
fi

# --- zoxide: cd inteligente (reemplaza al plugin z de OMZ) ---
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init zsh)"

# --- eza: ls moderno ---
if command -v eza >/dev/null 2>&1; then
  alias ls='eza --group-directories-first'
  alias ll='eza -l --group-directories-first --git'
  alias la='eza -la --group-directories-first --git'
  alias tree='eza --tree'
fi

# --- bat: cat con sintaxis coloreada ---
if command -v bat >/dev/null 2>&1; then
  alias cat='bat --paging=never'
  export MANPAGER="sh -c 'col -bx | bat -l man -p'"         # man con colores
elif command -v batcat >/dev/null 2>&1; then
  alias bat='batcat'                                        # nombre en Debian/Ubuntu
  alias cat='batcat --paging=never'
fi

# --- fd: find moderno (en Debian/Ubuntu el binario se llama fdfind) ---
command -v fd >/dev/null 2>&1 || { command -v fdfind >/dev/null 2>&1 && alias fd='fdfind'; }

# --- direnv: entornos por directorio ---
command -v direnv >/dev/null 2>&1 && eval "$(direnv hook zsh)"

# --- atuin: historial sincronizado y con búsqueda ---
command -v atuin >/dev/null 2>&1 && eval "$(atuin init zsh)"

# --- mise: gestor de versiones de runtimes ---
command -v mise >/dev/null 2>&1 && eval "$(mise activate zsh)"

# --- fnm: gestor de versiones de Node ---
command -v fnm >/dev/null 2>&1 && eval "$(fnm env --use-on-cd)"

# --- SDKMAN (Java): su init exige ir al final según su documentación ---
if [[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]]; then
  export SDKMAN_DIR="$HOME/.sdkman"
  source "$SDKMAN_DIR/bin/sdkman-init.sh"
fi

# ====================================================
#  Prompt (Starship)
# ====================================================
# Config versionada en ~/.config/starship.toml (paquete shell del repo).
# Solo se activa si el binario existe; si no, OMZ mantiene robbyrussell.
command -v starship >/dev/null 2>&1 && eval "$(starship init zsh)"

# ====================================================
#  Utilidades personales
# ====================================================
# Scripts propios en ~/Documents (rutas actualizadas tras la reorganización
# v4 de scripts_for_linux)
alias compilar="$HOME/Documents/scripts_for_latex/script_compilar_latex/main.sh"
alias ptree="$HOME/Documents/scripts_for_linux/scripts_filesystem_studio/backend/script_proyect_tree/main.sh"

# ====================================================
#  Configuración final
# ====================================================
# Sin duplicados en PATH aunque se re-ejecute este archivo (source ~/.zshrc)
typeset -U path PATH

# Ajustes locales de esta máquina (no versionados en dotfiles)
[[ -f "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"
