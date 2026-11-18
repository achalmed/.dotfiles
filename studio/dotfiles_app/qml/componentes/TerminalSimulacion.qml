// TerminalSimulacion — la salida de una simulación de main.sh (--dry-run, el «stow -n» de este gestor) como una
// terminal. Desde gui-comun 4.1 es la `TerminalSalida` de la base (que nació de esta pieza) con lo propio de main.sh:
// un archivo real en HOME, en negativo como un error; lo que haría («[dry-run]») y cada sección, en el color del texto;
// lo demás, tenue. Las reglas comunes (error, saltado, advertido, hecho) van en medio, en el orden de antes: un
// conflicto manda sobre «[dry-run]». La usan la portada (abajo de las tarjetas) y la pestaña Simulación de la página
// del paquete. No ejecuta nada: la salida la pone el controlador (studio.catalogo).
import GuiComun

TerminalSalida {
    titulo: "Simulación"
    mensajeVacio: "Sin simular todavía"
    nombreAccesible: "Salida de la simulación"
    nivelPorOmision: "inactivo"
    reglas: [{ contiene: "Archivo real existe", nivel: "negativo" }]
        .concat(reglasComunes)
        .concat([{ contiene: "[dry-run]", nivel: "" }, { contiene: "[SECTION", nivel: "" }])
}
