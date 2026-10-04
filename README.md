---
tipo: readme
estado: activo
---
# .dotfiles/ — la configuración de las aplicaciones de la máquina, en paquetes, y el gestor que la enlaza en `$HOME`

Gestor de dotfiles para Arch Linux y Kubuntu (repositorio achalmed/.dotfiles en GitHub). Cada aplicación
es un paquete con layout compatible con GNU Stow; `main.sh` crea los enlaces simbólicos desde el
repo hacia `$HOME`, de modo que lo que se cambia en la aplicación aparece como cambio en el repo.

## Qué es

Este repo **no es un respaldo del sistema**. Solo versiona lo que responde que sí a: «¿es una
personalización que hice a mano y quiero reproducir en otra máquina?». Entran preferencias,
temas, atajos, plantillas y la configuración de editores, del shell y de plugins; quedan fuera
caché, historial, archivos recientes, geometría de ventanas, estado de sesión, identificadores de
máquina y credenciales. La selección es explícita: `config.sh` enumera los archivos de cada
paquete y lo que no está ahí no se toca. El criterio completo y cada paquete, en
[docs/paquetes.md](docs/paquetes.md).

## Uso

Requisitos: `git` y `bash` 4 o superior; opcionales `zsh`, `starship` y `stow`. Distribuciones
reconocidas: Arch, Archcraft, EndeavourOS, Manjaro (pacman); Ubuntu, Kubuntu, Debian, Linux
Mint, Pop!_OS (apt). En otra, se instala `git` a mano y el resto funciona igual.

```bash
# Máquina nueva, el repo ya está en GitHub
git clone https://github.com/achalmed/.dotfiles.git ~/.dotfiles
~/.dotfiles/main.sh instalar-deps        # dependencias de la distro y fuentes de usuario
~/.dotfiles/main.sh instalar             # enlaces repo → $HOME
alias dotfiles='~/.dotfiles/main.sh'     # en ~/.zshrc

# Empezar a versionar configuración que ya está en la máquina
dotfiles adoptar -p kate --dry-run       # simular primero
dotfiles adoptar -p kate                 # mueve el archivo al repo y deja el enlace
git -C ~/.dotfiles diff                  # revisar antes de confirmar

# Uso diario
dotfiles estado                          # enlaces y git
dotfiles sync-pull                       # traer cambios y volver a enlazar
dotfiles sync-push                       # escáner de datos sensibles, commit y push
```

| comando | qué hace |
|---|---|
| `instalar` | crea los enlaces del repo hacia `$HOME` |
| `adoptar` | mueve al repo la configuración de `$HOME` y deja el enlace |
| `actualizar` | vuelve a aplicar los enlaces |
| `eliminar` | quita los enlaces sin tocar el repo |
| `sync-push` | escanea datos sensibles, confirma todo lo modificado y sube |
| `sync-pull` | baja cambios de GitHub y vuelve a enlazar |
| `estado` | estado de los enlaces y de git |
| `backup` | respaldo manual de la configuración actual |
| `seguridad` | escanea los archivos versionados en busca de credenciales |
| `instalar-deps` | instala dependencias según la distribución y, al final, las fuentes |
| `instalar-fuentes` | instala las fuentes de usuario de `USER_FONTS` en `~/.local/share/fonts`, sin sudo |

Opciones globales: `-p, --packages a,b` (solo esos paquetes; los nombres se validan contra
`STOW_PACKAGES`), `-n, --dry-run`, `-v, --verbose`, `-f, --force` (reemplazar sin preguntar,
con respaldo), `--no-backup`, `-h, --help`, `--version`. Sin argumentos, `main.sh` abre un menú.
Sin terminal interactiva, cada pregunta toma la opción segura; en scripts, pásese siempre `-p`.

**Problemas frecuentes.**

- *Hay un archivo real donde debería ir un enlace*: `dotfiles estado` dice dónde; `adoptar -p
  <paquete>` se queda con el de la máquina, `instalar -p <paquete> -f` con el del repo (antes,
  `dotfiles backup`).
- *El escáner detiene `sync-push`*: `dotfiles seguridad` muestra qué y dónde; se quita el dato o,
  si es un falso positivo revisado, se añade a `SENSITIVE_SCAN_ALLOWLIST` en `config.sh`.
- *Enlaces rotos*: `dotfiles actualizar`.
- *calibre o KOReader dejaron conflictos tras usarlos*: escriben de forma atómica y sustituyen
  el enlace; `dotfiles adoptar -p <paquete>` lo repone.
- *Falla el push*: comprobar `git -C ~/.dotfiles remote -v`; el commit queda guardado en local.

## Estructura

| carpeta o archivo | qué es | dueño / generador |
|---|---|---|
| `main.sh` | punto de entrada: carga los módulos y despacha el comando | a mano |
| `config.sh` | constantes, `STOW_PACKAGES`, `PACKAGE_FILES`, patrones sensibles, `USER_FONTS` | a mano |
| `lib/` | módulos del gestor ([docs/arquitectura.md](docs/arquitectura.md)) | a mano |
| `git/` `shell/` `kde/` `konsole/` `positron/` `obsidian/` `calibre/` `kate/` `texstudio/` `okular/` `rstudio/` `xournalpp/` `koreader/` | un paquete por aplicación, con la estructura de `$HOME` dentro | las aplicaciones, a través del enlace |
| `docs/` | referencia, explicación y decisiones | a mano; índice por `core/docs.py` |
| `.backups/`, `.logs/` | respaldos y registros del gestor, ignorados por git | el gestor |

## Documentación

| pregunta | documento |
|---|---|
| qué cubre cada paquete, qué se excluye y cómo se añade uno | [docs/paquetes.md](docs/paquetes.md) |
| cómo funciona el gestor y quién depende de este repo | [docs/arquitectura.md](docs/arquitectura.md) |
| los atajos de teclado de KDE | [docs/atajos-kde.md](docs/atajos-kde.md) |
| por qué se decidió así y qué está pendiente | [docs/decisiones.md](docs/decisiones.md) |
| todo, con su tipo y estado | [docs/README.md](docs/README.md) |

## Límite honesto

- La configuración se adoptó de una instalación de Kubuntu; la rama de pacman de `instalar-deps`
  no se ha comprobado en este repo.
- Los archivos híbridos (KDE, TeXstudio) arrastran algo de estado: cada diferencia se lee antes de
  confirmar, y `sync-push` confirma todo lo modificado.
- El escáner busca credenciales con forma `clave=valor`; no detecta rutas ni nombres privados.
- El historial de git conserva archivos que ya no se versionan. Lo que queda por decidir sobre él
  está en [docs/decisiones.md](docs/decisiones.md) §Pendientes. Licencia: MIT (`LICENSE`).
- El paquete `obsidian` supone que el vault es `~/Documents`; en otra máquina con otro vault hay
  que ajustar su estructura.
