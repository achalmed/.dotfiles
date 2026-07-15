# Atajos de teclado de KDE Plasma — Documentación de diseño

> Archivo gestionado: `kde/.config/kglobalshortcutsrc` (symlink desde `~/.config/`).
> Entorno: Plasma 6.6 · Wayland · KWin gestiona los atajos globales (kglobalacceld no corre como proceso separado).
> Hardware: HP Pavilion x360 (portátil **sin teclado numérico**, con lápiz táctil).
> Guía rápida imprimible: [ATAJOS-CHEATSHEET.md](ATAJOS-CHEATSHEET.md).

## Filosofía de asignación

| Prefijo                      | Rol                                                     | Ejemplos                                                                                           |
| ---------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `Meta` + letra               | Acciones frecuentes y foco (vim HJKL)                   | `Meta+J` foco abajo, `Meta+M` monocle, `Meta+Z` overlay de zonas                                   |
| `Meta` + número              | Ir al escritorio virtual N                              | `Meta+1..4`                                                                                        |
| `Meta+Shift`                 | **Mover** (la variante "con Shift arrastra la ventana") | `Meta+Shift+J` mover ventana, `Meta+Shift+2` ventana al escritorio 2, `Meta+Shift+Z` snap a zona   |
| `Meta+Ctrl`                  | Administración y redimensionado                         | `Meta+Ctrl+J/K/H/L` resize, `Meta+Ctrl+flechas` escritorio relativo, `Meta+Ctrl+Esc` matar ventana |
| `Meta+Alt`                   | Lanzar aplicaciones y navegación de zonas               | `Meta+Alt+O` Obsidian, `Meta+Alt+3` ventana a zona 3                                               |
| Teclas multimedia / hardware | Sin modificar (volumen, brillo, suspensión)             | —                                                                                                  |

Regla nemotécnica central: **la misma tecla base hace lo mismo en los tres niveles**.
Ej.: `Meta+J` enfoca abajo → `Meta+Shift+J` mueve la ventana abajo → `Meta+Ctrl+J` la agranda hacia abajo. `Meta+2` va al escritorio 2 → `Meta+Shift+2` manda la ventana al 2 → `Meta+Alt+2` la manda a la zona 2.

## Informe de auditoría (problemas encontrados y corrección)

1. **Teclas muertas de KZones (crítico).** `Activate layout 1–9` usaba `Meta+Num+N` y `Move to zone 1–9` usaba `Ctrl+Alt+Num+N`: teclas del _numpad_, inexistente en este portátil. Nunca pudieron funcionar. → Mover a zona ahora es `Meta+Alt+1..9`; la activación numerada de layouts se retiró (el ciclo `Meta+Alt+Z` + overlay `Meta+Z` la cubre).
2. **Navegación vim de Krohnkite incompleta (crítico).** Solo existían `Meta+H` (izquierda) y `Meta+J` (abajo); _Focus Up_ y _Focus Right_ estaban sin asignar porque `Meta+K` la ocupaba Krusader y `Meta+L` el bloqueo de sesión. → HJKL completo: Krusader pasó a `Meta+Alt+K` y el bloqueo a `Ctrl+Alt+L` (atajo clásico de KDE; KWin rechazó `Meta+Esc` en Wayland).
3. **KZones pisaba atajos de aplicaciones.** `Ctrl+Alt+flechas` (mover/ciclar en zonas) choca con el multicursor de VS Code/Positron; `Ctrl+Alt+C/D` con combos de edición. → Toda la gestión de zonas vive ahora bajo `Meta(+Shift/Ctrl/Alt)+Z` y `Meta+Alt+flechas/números`, espacio que ninguna aplicación usa.
4. **`Ctrl+F1–F4` cambiaban de escritorio.** Herencia de X11 que rompe `Ctrl+F4` (cerrar pestaña en Firefox/Zen) y las F-keys de ayuda. → Escritorios en `Meta+1..4`.
5. **`Meta+1..9` activaban entradas del gestor de tareas.** En un flujo tiling (Krohnkite+KZones) los números rinden más como escritorios (estándar i3/sway/Hyprland). → Reasignados; las entradas del panel quedaron sin tecla (recuperables en Preferencias del Sistema si se echan de menos).
6. **Selector de distribución de teclado inútil.** `Meta+Alt+K/L` cambiaban de distribución, pero el sistema tiene **una sola** distribución configurada (no existe `kxkbrc`). → Liberados; `Meta+Alt+K` ahora trae Krusader al frente.
7. **Sin atajos de lanzamiento de aplicaciones.** Para un flujo centrado en teclado faltaba lo esencial. → Nueva sección `[services]`: Konsole `Meta+Return` (estándar de todos los WM tiling; el _Set master_ de Krohnkite que la ocupaba pasó a `Meta+Shift+Return`, convención dwm), Dolphin `Meta+E` (default KDE, no aparece en el archivo por ser igual al default), y `Meta+Alt+letra` para el resto.
8. **Expose duplicado con Overview.** `Meta+F7/F9/F10` + `Ctrl+F7/F9/F10` duplicaban lo que ya hacen Overview (`Meta+W`) y Grid View (`Meta+G`), ocupando seis combinaciones y chocando con F-keys de apps. → Desasignados.
9. **Actividades fantasma.** Existe una única actividad («Default»), pero `Meta+Q`, `Meta+A` y `Meta+Shift+A` estaban dedicadas a cambiar entre actividades. → Liberadas; `Meta+Q` ahora **cierra la ventana** (estándar tiling; `Alt+F4` se mantiene como alternativa).
10. **Entradas huérfanas.** Seis `activate widget NN` de paneles antiguos. Se limpiaron; plasmashell re-registra en runtime las del widget actual (sin tecla, inofensivas — no confundir con basura nueva).
11. **Huecos funcionales cubiertos.** Pantalla completa sin atajo → `Meta+Shift+M` (pareja de `Meta+M` monocle); «No molestar» sin atajo → `Meta+N`; ciclo de layouts de Krohnkite en `Meta+\` (incómodo en teclado ES) → `Meta+.` / `Meta+,`.

## Decisiones que conviene conocer

- **Convivencia Krohnkite/KZones**: Krohnkite conserva las letras (foco/mover/resize/layouts); KZones queda íntegro bajo la letra `Z` y `Meta+Alt`. No comparten ninguna combinación.
- **Wacom/lápiz**: el módulo de tableta está instalado y sus atajos `Meta+Ctrl+F/M/N/P/S/T/1/2` se respetaron tal cual.
- **Compatibilidad con apps**: se evitó ocupar `Ctrl+Alt+*` (VS Code/Positron/LibreOffice), `Ctrl+F1..F12` (Firefox/Zen, Kate) y `Alt+*` (Neovim/terminales). Los defaults no escritos en el archivo (KRunner `Alt+Space`, Spectacle `Impr Pant`, `Meta+P` pantallas) siguen intactos.
- **Cómo se aplicó**: en Wayland Plasma 6.6 KWin es el dueño del servicio de atajos; editar el archivo a mano no recarga (y el demonio puede sobrescribirlo). Los cambios se aplicaron vía DBus (`org.kde.KGlobalAccel.setForeignShortcutKeys`), que actualiza memoria y archivo a la vez. Para futuros cambios: usar Preferencias del Sistema → Atajos, o el mismo método DBus.

## Cómo revertir un cambio puntual

Preferencias del Sistema → Atajos de teclado → buscar la acción → «Valor por defecto», o reasignar la combinación deseada. El archivo del repo recogerá el cambio automáticamente (symlink).
