---
tipo: doc
titulo: 'Arquitectura del gestor: módulos, enlaces sin stow, escáner de datos sensibles, respaldos, fuentes de usuario y consumidores'
estado: activo
---
# Arquitectura del gestor

Cómo funciona por dentro `main.sh`, el gestor que enlaza los paquetes en `$HOME`. Qué paquetes
hay y por qué, en [paquetes.md](paquetes.md); por qué se decidió cada cosa, en
[decisiones.md](decisiones.md).

## Módulos

`main.sh` no contiene lógica: carga los módulos en orden de dependencia, interpreta los
argumentos y despacha el comando a una función. La función se invoca dentro de un `if`, de modo
que un fallo se informa con su código en lugar de cortar el script por `set -e`.

| archivo | responsabilidad |
|---|---|
| `config.sh` | constantes: rutas (`DOTFILES_DIR`, derivada de `$HOME` y sobrescribible por entorno), versión, distribución y gestor de paquetes, `STOW_PACKAGES`, `PACKAGE_FILES`, patrones sensibles y su lista de excepciones, fuentes de usuario. Se carga primero |
| `lib/logger.sh` | registro por niveles en consola y en un archivo diario dentro de `.logs/` |
| `lib/validator.sh` | comprobaciones previas (git instalado y configurado, directorio, conexión, árbol limpio) y el escáner de datos sensibles |
| `lib/cli.sh` | argumentos (valida los nombres de `-p` contra `STOW_PACKAGES`), ayuda, menú y confirmaciones |
| `lib/stow_ops.sh` | adoptar, instalar, actualizar y eliminar enlaces; estado de los enlaces |
| `lib/git_ops.sh` | `sync-push`, `sync-pull` y estado de git |
| `lib/tools.sh` | respaldos, instalación de dependencias por distribución y de fuentes de usuario |

## Enlaces sin stow

El gestor no invoca GNU Stow: crea cada enlace con `ln -sfn`, archivo por archivo (o directorio
por directorio, si la entrada de `PACKAGE_FILES` es un directorio), según el mapa. El layout de
cada paquete sigue siendo compatible con stow —`stow <paquete>` funcionaría—, pero enlazaría el
paquete entero sin el control fino del mapa. `instalar-deps` sigue ofreciendo stow como
dependencia opcional para quien quiera usarlo a mano.

Ante un archivo real donde debería ir un enlace, `adoptar` lo lleva al repo y `instalar` lo
sustituye por la versión del repo; en ambos casos, antes, hace un respaldo. Sin terminal
interactiva, toda pregunta toma la opción segura (saltar, no borrar).

## Escáner de datos sensibles

`./main.sh seguridad`, y siempre `sync-push` antes de confirmar, recorren los archivos
versionados y los nuevos no ignorados con patrones de tipo `clave=valor` (contraseñas, claves de
API, tokens, claves privadas). Si hay coincidencias, `sync-push` se detiene; los falsos positivos
revisados se declaran en `SENSITIVE_SCAN_ALLOWLIST`. El escáner no ve rutas ni nombres privados
dentro de una lista de archivos recientes: eso lo detiene solo la lectura del diff.

`sync-push` confirma con `git add .`, es decir, todo lo modificado. Con una diferencia retenida a
propósito en el árbol, se confirma a mano por ruta y no se usa `sync-push`.

## Respaldos

Antes de instalar o adoptar, `lib/tools.sh` guarda un tarball «quirúrgico» con solo los
archivos de `$HOME` que tocan los paquetes elegidos; `./main.sh backup` hace uno manual. Viven
en `.backups/` (fuera de git) y se conservan los últimos 15. Son respaldos de emergencia, no
sustituyen un respaldo del sistema.

## Fuentes de usuario

Las familias que la máquina necesita y que no llegan por el gestor de paquetes ni por TeX Live
se describen en `USER_FONTS` (`config.sh`) como receta: carpeta, URL del release oficial, sha256
y patrón dentro del zip. `./main.sh instalar-fuentes` (y el final de `instalar-deps`) las
descarga en `~/.local/share/fonts/<carpeta>/`, comprueba el sha256 y refresca fontconfig, sin
sudo. Los binarios no entran en el repo.

## Swap comprimida (zram)

`instalar-deps` instala `zram-generator` (`systemd-zram-generator` en apt) y escribe
`ZRAM_CONF_FILE` con `ZRAM_TAMANO` y `ZRAM_ALGORITMO` (`config.sh`). Es el único archivo fuera de
`$HOME` que toca el repo: es de root y systemd lo lee al arrancar, así que se copia con sudo en vez
de enlazarse. Si ya coincide no se toca; si difiere, el anterior queda como `.bak-<fecha>` a su
lado. Una zram que ya es swap no se reinicia (habría que devolver su contenido a la RAM): el
cambio se aplica al próximo arranque. `ZRAM_TAMANO=""` deja la zram como esté.

## Autonomía respecto de `~/Documents`

Este repo reproduce la máquina, no el espacio de trabajo: se instala antes de que exista
`~/Documents` y nada del gestor depende de él. Por eso el registro y los respaldos duplican a
propósito la biblioteca de shell del espacio de trabajo (mismo formato de línea). La única
excepción son los alias del shell (el paquete `obsidian` se retiró en la ola 8: la configuración de la
aplicación vive en el vault, `~/Documents/.obsidian/`, como archivos reales). Si un archivo solo tiene sentido con `~/Documents`, no va
aquí.

## Consumidores

| consumidor | qué usa | contrato |
|---|---|---|
| la capa de diseño editorial (`sistema-editorial`) | Source Serif 4 instalada por `instalar-fuentes` | la familia y su versión las fija `USER_FONTS`; cambiarlas obliga a avisar a ese consumidor |
