---
tipo: doc
titulo: 'Atajos de teclado de KDE Plasma: convenciones y tabla de referencia'
estado: activo
---
# Atajos de teclado de KDE Plasma

Referencia de los atajos globales que versiona el paquete `kde` en
`kde/.config/kglobalshortcutsrc`. Entorno: Plasma 6 sobre Wayland, con Krohnkite (mosaico) y
KZones (zonas), en un portátil sin teclado numérico. Por qué se asignaron así:
[decisiones.md](decisiones.md) §Atajos de KDE.

## Convenciones

`Meta` es la tecla Windows/Super. La misma tecla base hace lo mismo en cada nivel:

| prefijo | rol | ejemplo |
|---|---|---|
| `Meta` + letra | actuar y enfocar (HJKL al estilo vim) | `Meta+J` enfoca abajo |
| `Meta` + número | ir al escritorio N | `Meta+2` |
| `Meta+Shift` | mover | `Meta+Shift+J` mueve la ventana abajo; `Meta+Shift+2` la manda al escritorio 2 |
| `Meta+Ctrl` | administrar y redimensionar | `Meta+Ctrl+J` la agranda hacia abajo |
| `Meta+Alt` | lanzar aplicaciones y navegar zonas | `Meta+Alt+O` Obsidian; `Meta+Alt+2` ventana a la zona 2 |
| teclas multimedia | sin modificar | volumen, brillo, suspensión |

Para cambiar o revertir un atajo: Preferencias del Sistema → Atajos de teclado; el archivo del
repo recoge el cambio por el enlace simbólico.

## Aplicaciones

| atajo | acción |
|---|---|
| `Meta+Return` | Konsole |
| `Meta+E` | Dolphin |
| `Meta+Alt+B` | Zen Browser |
| `Meta+Alt+E` | Kate |
| `Meta+Alt+K` | Krusader (traer al frente) |
| `Meta+Alt+O` | Obsidian |
| `Meta+Alt+P` | Positron |
| `Meta` | lanzador de aplicaciones |

## Foco y ventanas (Krohnkite)

| atajo | acción |
|---|---|
| `Meta+H / J / K / L` | foco ← ↓ ↑ → |
| `Meta+Shift+H / J / K / L` | mover ventana ← ↓ ↑ → |
| `Meta+Ctrl+H / J / K / L` | encoger ancho / crecer alto / encoger alto / crecer ancho |
| `Meta+Shift+Return` | convertir en ventana maestra |
| `Meta+F` | flotar / anclar ventana |
| `Meta+Shift+F` | flotar todas |
| `Meta+M` | disposición monocle |
| `Meta+.` / `Meta+,` | disposición siguiente / anterior |

## Ventanas (KWin)

| atajo | acción |
|---|---|
| `Meta+Q` (o `Alt+F4`) | cerrar ventana |
| `Meta+Shift+M` | pantalla completa |
| `Meta+PgUp` / `Meta+PgDown` | maximizar / minimizar |
| `Meta+flechas` | mosaico rápido a los bordes |
| `Meta+Tab` / `Alt+Tab` | recorrer ventanas |
| `` Meta+` `` | ventanas de la misma aplicación |
| `Meta+D` | vistazo al escritorio |
| `Meta+Shift+D` | minimizar todas |
| `Meta+Shift+O` | minimizar las demás |
| `Meta+Ctrl+Esc` | matar ventana |
| `Meta+Ctrl+A` | ventana que pide atención |
| `Meta+T` | editor de mosaico nativo |

## KZones

| atajo | acción |
|---|---|
| `Meta+Z` | mostrar u ocultar el overlay de zonas |
| `Meta+Shift+Z` | ajustar la ventana activa |
| `Meta+Ctrl+Z` | ajustar todas las ventanas |
| `Meta+Alt+Z` (`+Shift`, inverso) | recorrer disposiciones de zonas |
| `Meta+Alt+1..9` | mover la ventana a la zona N |
| `Meta+Alt+←` / `→` | ventana a la zona anterior / siguiente |
| `Meta+Alt+↑` / `↓` | recorrer ventanas dentro de la zona |

## Escritorios virtuales y pantallas

| atajo | acción |
|---|---|
| `Meta+1..4` | ir al escritorio N |
| `Meta+Shift+1..4` | ventana al escritorio N |
| `Meta+Ctrl+←` / `→` | escritorio anterior / siguiente |
| `Meta+Ctrl+Shift+←` / `→` | ventana al escritorio anterior / siguiente |
| `Meta+Shift+←` / `→` | ventana al monitor anterior / siguiente |

## Vistas, sistema y accesibilidad

| atajo | acción |
|---|---|
| `Meta+W` | Overview |
| `Meta+G` | vista de cuadrícula |
| `Meta+C` | cubo |
| `Ctrl+Alt+L` | bloquear sesión |
| `Ctrl+Alt+Del` | pantalla de cierre de sesión |
| `Meta+B` | perfil de energía |
| `Meta+N` | no molestar |
| `Meta+V` | historial del portapapeles |
| `Meta+Ctrl+X` | acciones del portapapeles |
| `Meta++` / `Meta+-` / `Meta+0` | zoom: acercar / alejar / tamaño real |
| `Meta+Alt+S` | lector de pantalla |
| `Meta+F5` / `Meta+F6` | ratón al foco / al centro |

Las teclas multimedia y de hardware (volumen, micrófono —`Shift+` da pasos de 1 %—, brillo,
reproducción, suspensión) conservan su función de fábrica.
