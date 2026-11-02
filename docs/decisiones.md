---
tipo: decision
titulo: 'Decisiones del repo dotfiles, por tema y con fecha, y sus pendientes'
estado: activo
---
# Decisiones

Registro acumulativo: una entrada por decisión, agrupadas por tema, con su fecha. Lo que se hizo
en cada cambio está en el mensaje de commit; aquí queda por qué.

## Qué se versiona

- **Mínima captura** (2026-07-06). Solo se versiona la personalización hecha a mano; caché,
  historial, recientes, geometría, estado, identificadores de máquina y credenciales, nunca. La
  selección es positiva (`PACKAGE_FILES` en `config.sh`) y `.gitignore` es la segunda defensa.
  Una auditoría retiró ese día los archivos dominados por estado (lista en
  [paquetes.md](paquetes.md) §Exclusiones deliberadas) y los devolvió a `$HOME` como archivos
  reales.
- **Híbridos admitidos** (2026-07-06). `kdeglobals`, `kwinrc`, `konsolerc` y `texstudio.ini` se
  versionan aunque arrastren algo de estado, porque las preferencias dominan y no se pueden
  separar. `texstudio.ini` pasa desde el 2026-10-04 por un filtro `clean` de git
  (`lib/filtros/texstudio_ini.sh`) que retira las claves de archivos recientes, último documento y
  último directorio: lo confirmado no lleva rutas privadas; la historia anterior sí (§Pendientes).
- **Plugins de Obsidian como directorios** (2026-09-15). Cada plugin de la comunidad se enlaza
  como directorio; se versionan `data.json` y `manifest.json`, y `main.js`/`styles.css` se ignoran
  porque son código que se reinstala desde `community-plugins.json`. El mapa describe el disco:
  un cambio de layout en `$HOME` se refleja en `PACKAGE_FILES` en el mismo commit.
- **Fuentes de usuario como receta** (2026-09-17). Las familias que no llegan por el gestor de
  paquetes ni por TeX Live se instalan con `instalar-fuentes` desde su release oficial,
  verificando el sha256; el repo guarda la receta (`USER_FONTS`), no los binarios. La primera es
  Source Serif 4, que pide la capa de diseño editorial del espacio de trabajo.

## Cómo se enlaza

- **Sin stow como dependencia** (2026-07-06). Enlaces directos con `ln -sfn` según el mapa,
  con layout compatible con stow. No se reintroduce una dependencia obligatoria de stow.
- **Autonomía respecto de `~/Documents`** (2026-09-15). El repo reproduce la máquina, no el
  espacio de trabajo: el paquete que versionaba el vault OS salió de aquí y se versiona en el
  repo `ecosistema`, con su historial; los datos de lectura de KOReader tienen repo propio. El
  registro y los respaldos duplican a propósito la biblioteca de shell del espacio de trabajo
  para que el gestor arranque solo.

## Documentación

- **`docs/` y una sola puerta** (2026-10-04). El README es la puerta (uso y estructura); la
  referencia de paquetes, la arquitectura, los atajos de KDE y estas decisiones viven en `docs/`.
  Ningún `.md` va dentro de un directorio de paquete, porque `stow <paquete>` lo enlazaría a
  `$HOME`. La guía del asistente es `CLAUDE.md`, en español, con `AGENTS.md` como enlace.

## Atajos de KDE

- **Esquema por prefijos** (2026-07-15). La misma tecla base hace lo mismo en cada nivel:
  `Meta` actúa, `+Shift` mueve, `+Ctrl` administra, `+Alt` lanza y navega zonas, número =
  escritorio ([atajos-kde.md](atajos-kde.md)).
- **Sin teclado numérico**. Ningún atajo usa el numpad; mover a zona es `Meta+Alt+1..9`.
- **HJKL completo para Krohnkite**. Krusader pasó a `Meta+Alt+K` y el bloqueo de sesión a
  `Ctrl+Alt+L` para liberar `Meta+K` y `Meta+L`.
- **KZones bajo `Z` y `Meta+Alt`**. No comparte combinaciones con Krohnkite y deja libres
  `Ctrl+Alt+*` (multicursor y combinaciones de edición de los IDE).
- **Escritorios en `Meta+1..4`**. Se retiraron `Ctrl+F1..F4` (chocaban con cerrar pestaña y las
  teclas de función de las aplicaciones) y las entradas numeradas del gestor de tareas.
- **Sin atajos huérfanos**. Se liberaron los de actividades (hay una sola), el cambio de
  distribución de teclado (hay una sola) y los de Expose que duplicaban Overview; `Meta+Q` cierra
  la ventana.
- **Se respetan** los atajos del lápiz y la tableta, y los valores por defecto de KDE que no
  están escritos en el archivo.
- **Cómo se aplican**. En Wayland, KWin es el dueño del servicio de atajos: editar el archivo a
  mano no recarga y puede ser sobrescrito. Se cambian desde Preferencias del Sistema o por DBus
  (`org.kde.KGlobalAccel.setForeignShortcutKeys`), que actualiza memoria y archivo a la vez.

## Fuera de `$HOME`

- **zram en `instalar-deps`** (2026-10-27). Sin swap, al llenarse la RAM el *OOM killer* del
  kernel cerraba aplicaciones antes de que diera tiempo a elegir cuál cerrar; Ubuntu no trae
  swap comprimida configurada a la medida. Se reproduce como receta (`ZRAM_*` en `config.sh`), no
  como paquete enlazado: `/etc/systemd/zram-generator.conf` es de root, systemd lo lee al
  arrancar y un archivo del sistema no debe depender de uno de `$HOME`. La mitad de la RAM con `zstd`:
  comprime más que `lzo-rle` a cambio de algo de CPU, y en esta máquina lo que falta es RAM.

## La ventana

- **Dotfiles Studio, opcional y sin `~/Documents`** (2026-11-01; propuesta aprobada por el autor en el espacio de
  trabajo). La familia de studios encuentra su marco (`gui-comun`) subiendo carpetas hasta `~/Documents`; aquí eso
  rompería la autonomía del repo, así que `gui-comun` entra como paquete de pip desde su repo público y con versión
  fija, y la ventana es opcional: sin ella, `main.sh` hace todo. Corre `main.sh` para lo que cambia algo; eliminar se
  pasa con `--force` porque la ventana ya preguntó (sin terminal, `confirm_action` respondería «no»); instalar nunca
  lleva `--force`. Los cambios se confirman de uno en uno, con su diff entero y tras el escáner; no hay `sync-push`.
- **Dotfiles Studio en QML + Kirigami, como el resto de la familia** (2026-11-02; fase 5 de la modernización de los
  studios sobre el diseño que el autor aprobó con el piloto Git Studio; [rediseno.md](rediseno.md)). Las seis
  páginas de Widgets se reescriben como una sola ventana sobre `GuiComun.VentanaStudio` (`gui-comun` 2.1) con tres
  vistas (Paquetes, Cambios, Guía) y las operaciones en el menú: **F5 simula y Ctrl+Intro aplica tras confirmar**
  (regla 3 del espacio de trabajo). Corre con el Python del sistema porque su Qt es el que trae Kirigami; `gui-comun`
  sigue entrando por pip con versión fija, y además por la variable explícita `GUI_COMUN_DIR` para desarrollar contra
  una copia local, nunca subiendo carpetas. `--force` va con eliminar siempre (también al simular: `confirm_action`
  lee la entrada estándar) y con instalar solo si se marca «Reemplazar los archivos reales»; adoptar con un archivo
  en los dos lados e `instalar-deps` se abren en una terminal porque `main.sh` pregunta por `/dev/tty` o pide `sudo`.
  La preferencia `ui/tema` deja de ofrecerse (el tema es del escritorio). Los pendientes del repo pasan a `estado.md`
  §Por hacer (regla 10 del espacio de trabajo); esta tabla conserva las decisiones abiertas del autor anteriores.

- **Dotfiles Studio como gestor de paquetes de configuración** (2026-11-02; reingeniería de los diez studios encargada
  por el autor, decidida por el director con el criterio más conservador; [reingenieria.md](reingenieria.md)). La
  ventana deja de ser una variación de Dolphin y toma la forma de Discover, sobre `GuiComun.VentanaBase`
  (`gui-comun` 3.0): portada de tarjetas y página por paquete. **Nada se aplica sin ver antes** la comparación
  repo ⟷ HOME, el plan por archivo (que reproduce `lib/stow_ops.sh`) y la orden exacta. Aplicar pide confirmación
  con esas consecuencias y su estado de operación (instalación, escritura, eliminación o publicación), y después
  verifica que cada archivo quedó como el plan decía. Atajos de gestor: Ctrl+Mayús+Intro simula, Ctrl+Intro aplica,
  F5 relee.

  `actualizar` se ofrece por primera vez, pero bloqueada cuando borraría un archivo real sin respaldo (`ln -sfn`).
  Se añade el estado «local» (solo en HOME), que `main.sh estado` cuenta como ausente.

  El escáner pasa de 5 a 16 patrones con nombre, más la regla de los `.env` versionados. Informa archivo, línea y
  tipo, nunca el valor; en la ventana, con una huella HMAC de la sesión. Las comparaciones ocultan las líneas con un
  secreto. Ninguno de los patrones nuevos casa nada en el repo real (comprobado con `grep -l`, sin mostrar
  contenido).

  El defecto de `--dry-run` que creaba carpetas se corrige en `lib/stow_ops.sh` en un commit propio.

## Pendientes

| prioridad | pendiente | anotado | dueño |
|---|---|---|---|
| **alta** | ~~`texstudio.ini` versiona la lista de archivos recientes…~~ *Resuelto el 2026-10-04 con el filtro `clean`* para lo que se confirma desde hoy. Sigue abierto: las rutas ya publicadas en la historia del remoto (decidir si se reescribe) | 2026-10-04 | autor |
| **alta** | el historial público conserva archivos y rutas privadas de etapas anteriores del repo (incluida la credencial de base de datos ya conocida). Decidir si se reescribe el historial y se fuerza el push, y rotar lo que corresponda | 2026-10-04 | autor |
| **alta** | el visor de calibre versiona su historial de lectura y varias configuraciones guardan rutas absolutas de la máquina (calibre, Positron): contra la mínima captura y no portables. Decidir si salen del mapa | 2026-10-04 | autor |
| — | ~~el repo es público y no tiene `LICENSE`~~ cerrado el 2026-10-04 por decisión del autor: MIT (`LICENSE`) | 2026-10-04 | autor |
| media | `sync-push` confirma con `git add .`: arrastra cualquier diferencia retenida. Valorar que confirme solo las rutas de `PACKAGE_FILES` | 2026-10-04 | autor |
| baja | `validate_stow_installed` (`lib/validator.sh`) no se llama desde ningún sitio: borrarla o usarla | 2026-10-04 | autor |
