---
tipo: doc
titulo: 'Paquetes: qué configuración reproduce cada uno, qué se excluye y por qué'
estado: activo
---
# Paquetes

Un paquete es un directorio por aplicación (`git/`, `shell/`, `kde/`…) que replica, por
dentro, la estructura de `$HOME`. **La fuente de verdad es `config.sh`**: `STOW_PACKAGES` es la
lista de paquetes y `PACKAGE_FILES` el mapa exacto de archivos de cada uno; lo que no figura
ahí no se enlaza ni se versiona. Este documento dice qué función cumple cada paquete y el
criterio que decide qué entra; para la lista de archivos, léase `config.sh`.

## Criterio de inclusión (mínima captura)

Un archivo entra si representa una personalización hecha a mano que se quiere reproducir en
otra máquina: preferencias, apariencia, temas, atajos, plantillas, configuración de editores,
del shell y de plugins (texto, nunca binarios). No entran caché, logs, bloqueos, bases de datos,
índices, historial, listas de archivos recientes, geometría de ventanas, identificadores de
máquina, estado de sesión, credenciales ni nada regenerable. La selección es positiva
(`PACKAGE_FILES`); `.gitignore` es la segunda línea de defensa.

## Qué cubre cada paquete

| paquete | función |
|---|---|
| `git` | identidad y preferencias de git, sin credenciales (se usa un `credential.helper`) |
| `shell` | zsh (Oh My Zsh y alias) y la configuración de starship en su ruta XDG, que está versionada pero inactiva: el `.zshrc` no la inicializa |
| `kde` | preferencias globales de Plasma: tema y colores, atajos globales ([atajos-kde.md](atajos-kde.md)), KWin, Dolphin, región y aplicaciones predeterminadas; solo archivos dominados por preferencias |
| `konsole` | el perfil y el esquema de color, que es donde vive la personalización; `konsolerc` solo aporta el perfil por defecto, referido por nombre |
| `positron` | ajustes del IDE Positron |
| `obsidian` | configuración de la aplicación para el vault (`~/Documents`): apariencia, atajos, plugins activos, fragmentos CSS y la configuración de cada plugin de la comunidad, enlazado como directorio (se versionan sus `data.json` y `manifest.json`; el código del plugin se reinstala) |
| `calibre` | preferencias de calibre y de su visor y editor |
| `kate` | editor, cliente LSP y herramientas externas |
| `texstudio` | configuración completa del editor (híbrido; ver abajo) |
| `okular` | solo las preferencias de visualización |
| `rstudio` | preferencias del editor |
| `xournalpp` | ajustes de la aplicación |
| `koreader` | ajustes de lectura propios por el mecanismo oficial de KOReader (sobrescrituras de usuario, gestos, teclas, valores por carpeta) |

## Archivos híbridos

KDE y TeXstudio mezclan preferencias y estado en el mismo archivo. Se versionan
`kdeglobals`, `kwinrc`, `konsolerc` y `texstudio.ini` porque las preferencias dominan, y tras usar
las aplicaciones aparecen diferencias pequeñas que se revisan antes de confirmar. `texstudio.ini`
contiene además la lista de archivos recientes, el último documento y el último directorio, con
rutas privadas: un filtro `clean` de git (`lib/filtros/texstudio_ini.sh`, activado por
`.gitattributes` y por `./main.sh instalar`) las quita de lo que se confirma; en el disco siguen.

## Exclusiones deliberadas

Archivos que se versionaban y se retiraron porque el estado domina sobre la configuración. Sus
configuraciones siguen como archivos reales en `$HOME`; en otra máquina se configuran a mano o
con el mecanismo propio de la aplicación.

| aplicación | archivo | motivo |
|---|---|---|
| digiKam | `digikamrc` | índices, geometría, rutas y credencial de la base de datos |
| Krusader | `krusaderrc` | URL frecuentes, historial de pestañas, estado binario |
| Zotero | `prefs.js` | marcas de sincronización y geometría; la ruta del perfil no es portable |
| Okular | `okularrc` | archivos recientes y geometría (las preferencias están en `okularpartrc`) |
| LibreOffice | `registrymodifications.xcu` | recientes, posiciones y rutas locales en un archivo que cambia en cada uso |
| Plasma | `plasma-org.kde.plasma.desktop-appletsrc`, `plasmashellrc` | disposición de paneles y estado por monitor |
| Konsole | `konsolesshconfig` | estado de plugin, sin personalización |
| Obsidian | `workspace.json`, `core-plugins-migration.json`, `vault-stats.json`, código de plugins | estado de ventanas y de migración; el código se reinstala desde `community-plugins.json` |
| calibre | `gui.json`, `gui.py.json` | geometría y modelo del monitor; historial de búsquedas |
| KOReader | `settings.reader.lua`, `history.lua`, estadísticas | último archivo abierto y geometría; historial |
| VSCode | paquete entero | sustituido por Positron |

## Aplicaciones que rompen el enlace

calibre y KOReader guardan escribiendo un archivo nuevo y renombrándolo, lo que sustituye el
enlace simbólico por un archivo real. Por eso sus archivos más volátiles quedaron fuera. Si
`./main.sh estado` muestra conflictos en esos paquetes después de usarlos,
`./main.sh adoptar -p <paquete>` vuelve a llevar al repo los archivos que sí se versionan.

## Añadir un paquete

1. Añadir el nombre a `STOW_PACKAGES` y sus rutas (relativas a `$HOME`) a `PACKAGE_FILES`, en
   `config.sh`. Solo preferencias; ante la duda, observar el archivo unos días con `git diff`.
2. `./main.sh adoptar -p <paquete>` si la configuración está en la máquina, o
   `./main.sh instalar -p <paquete>` si ya está en el repo; antes, con `--dry-run`.
3. Revisar `git diff` antes de confirmar: ni rutas absolutas, ni historial, ni credenciales.

Un archivo que empieza a cambiar en cada uso es señal de que la aplicación le mete estado. Si
las preferencias ya no dominan: quitarlo de `PACKAGE_FILES`, borrar el enlace, devolver el
archivo a `$HOME` y `git rm --cached` la ruta.

Nunca se pone documentación dentro de un directorio de paquete: un `stow <paquete>` la
enlazaría a `$HOME`. La documentación de un paquete va a `docs/`.
