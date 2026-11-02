// Main.qml — Dotfiles Studio: los paquetes del repo y lo que main.sh hace con ellos, en un espacio de trabajo al estilo
// Dolphin/Kate sobre GuiComun.VentanaStudio. Navegación (filtros de paquetes, cambios, guía) · centro (el árbol de
// paquetes, la tabla de cambios o el documento) · detalles (selección y operación, diferencia y repositorio,
// documento) · panel inferior (Salida, Registro) · barra de estado. Ninguna orden se ejecuta aquí: todo lo hacen los
// controladores de Python (studio.*), y toda orden es main.sh o git.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun
import "componentes"

VentanaStudio {
    id: ventana

    readonly property var espacio: studio.espacio
    readonly property var registro: studio.acciones
    readonly property var paquetes: studio.paquetes
    readonly property var cambios: studio.cambios
    readonly property string vista: espacio.vista
    readonly property int indice: espacio.indiceVista
    readonly property var sel: paquetes.seleccion

    title: espacio.nombreRepo + " — Dotfiles Studio"
    acciones: registro
    tareas: studio.tareas
    consola: studio.consola
    descripcion: descripcionStudio
    autor: "Edison Achalma (@achalmed)"
    sitio: "https://github.com/achalmed/.dotfiles"
    resumen: espacio.resumen
    contexto: espacio.contexto
    claveAjustes: "ventana"

    function accion(nombre) { return registro.accion(nombre) }
    function vistaActual() { return centro.children[ventana.indice] }
    function irAPestana(i) { ventana.mostrarDetalles = true; const d = detalles.children[ventana.indice]; if (d) d.pestanaActual = i }
    // la fila raíz de un paquete (la de su modelo) → la fila que ocupa en el árbol expandido (la de la vista)
    function seleccionarPaquete(filaRaiz) {
        if (filaRaiz < 0) return
        const filaVista = arbolPaquetes.vista.rowAtIndex(paquetes.modelo.index(filaRaiz, 0))
        if (filaVista < 0) return
        arbolPaquetes.seleccionarFila(filaVista, true)
        paquetes.seleccionarActual(arbolPaquetes.indiceDe(filaVista))
    }
    function nombreNavegacion() {
        if (ventana.vista === "paquetes") return "filtro:" + paquetes.filtro
        if (ventana.vista === "cambios") return "cambios"
        return studio.guia.nombreActual
    }

    // ------------------------------------------------------------------ lo que Python pide a la interfaz
    Connections {
        target: studio.interfaz
        function onPedir(nombre, datos) {
            switch (nombre) {
            case "filtrar": filtro.forceActiveFocus(); filtro.selectAll(); break
            case "seleccionar_todo": { const v = vistaActual(); if (v && v.seleccionarTodo) v.seleccionarTodo(); break }
            case "seleccionar_paquete": ventana.seleccionarPaquete(datos.fila); arbolPaquetes.forceActiveFocus(); break
            case "seleccionar_fila":
                if (datos.fila >= 0) { tablaCambios.seleccionarFila(datos.fila, true); cambios.fijarFila(datos.fila) }
                break
            case "pestana": irAPestana(datos.indice || 0); break
            case "expandir": arbolPaquetes.expandirTodo(-1); break
            case "contraer": arbolPaquetes.contraerTodo(); break
            case "aplicar":
                if (ventana.vista === "paquetes") dialogoAplicar.abrir()
                else if (ventana.vista === "cambios") { ventana.mostrarDetalles = true; irAPestana(0); diferencia.confirmar() }
                break
            case "subir": dialogoSubir.open(); break
            case "sistema": dialogoSistema.abrir(datos.nombre); break
            case "paleta": ventana.paleta.abrir(datos.texto || ""); break
            }
        }
    }
    Connections { target: espacio; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections {
        target: paquetes
        function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) }
        function onFilaRepuesta(fila) { Qt.callLater(() => ventana.seleccionarPaquete(fila)) }
    }
    Connections { target: cambios; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections { target: studio.sistema; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections { target: espacio; function onVistaCambiada() { filtro.text = ""; navegacion.actual = Qt.binding(() => ventana.nombreNavegacion()) } }

    // ------------------------------------------------------------------ barra: el filtro
    herramientasExtra: [
        Kirigami.SearchField {
            id: filtro
            Layout.preferredWidth: Kirigami.Units.gridUnit * 12
            placeholderText: ventana.vista === "paquetes" ? "Filtrar paquetes (Ctrl+F)" : "Filtrar (Ctrl+F)"
            enabled: ventana.vista !== "guia"
            onTextChanged: { if (ventana.vista === "paquetes") paquetes.fijarTexto(text); else if (ventana.vista === "cambios") cambios.modelo.filtrar(text) }
            Keys.onEscapePressed: { text = ""; const v = vistaActual(); if (v) v.forceActiveFocus() }
            Accessible.name: "Filtrar"
        }
    ]

    // ------------------------------------------------------------------ navegación: paquetes, repositorio y guía
    navegacion: PanelNavegacion {
        id: navegacion
        actual: ventana.nombreNavegacion()
        secciones: [
            { titulo: "Paquetes", filas: paquetes.filtros },
            { titulo: "Repositorio", filas: [{ nombre: "cambios", texto: "Cambios sin confirmar", icono: "vcs-commit", contador: cambios.cuantos }] },
            { titulo: "Guía", filas: studio.guia.documentos }
        ]
        onElegida: nombre => {
            if (nombre.startsWith("filtro:")) { paquetes.fijarFiltro(nombre); espacio.fijarVista("paquetes") }
            else if (nombre === "cambios") espacio.fijarVista("cambios")
            else if (nombre.startsWith("doc:")) { studio.guia.fijarDocumento(nombre); espacio.fijarVista("guia") }
            actual = Qt.binding(() => ventana.nombreNavegacion())
        }
    }

    // ------------------------------------------------------------------ centro: el árbol, la tabla o el documento
    centro: StackLayout {
        id: centro
        currentIndex: ventana.indice

        ArbolDatos {                                              // 0 · Paquetes
            id: arbolPaquetes
            modelo: paquetes.modelo
            expandirAlCargar: 1
            umbralEstrecho: Kirigami.Units.gridUnit * 30
            mensajeVacio: paquetes.error !== "" ? "No se pudo leer config.sh: " + paquetes.error
                        : paquetes.texto !== "" ? "Ningún paquete ni archivo casa con «" + paquetes.texto + "»"
                        : paquetes.filtro === "atencion" ? "Todo enlazado: ningún paquete pide atención"
                        : paquetes.filtro === "activos" ? "Ningún paquete está enlazado del todo" : "Sin paquetes en STOW_PACKAGES"
            iconoVacio: paquetes.filtro === "atencion" ? "vcs-normal" : "package-x-generic"
            columnas: [
                { ancho: 0, minimo: 14, conIcono: true },
                { ancho: 8, semantica: true, conIcono: true },
                { ancho: 18, secundaria: true, estrecho: true }
            ]
            onSeleccionCambiada: paquetes.seleccionar(indicesSeleccionados())
            onFilaActualCambiada: fila => paquetes.seleccionarActual(fila >= 0 ? indiceDe(fila) : null)
            onActivada: indice => ventana.irAPestana(0)
            menuContextual: MenuAcciones {
                acciones: ventana.registro
                conAtajos: false
                elementos: [
                    { tipo: "accion", nombre: "herr.ejecutar" }, { tipo: "accion", nombre: "herr.aplicar" },
                    { tipo: "separador" },
                    { tipo: "accion", nombre: "op.instalar" }, { tipo: "accion", nombre: "op.adoptar" }, { tipo: "accion", nombre: "op.eliminar" },
                    { tipo: "separador" },
                    { tipo: "accion", nombre: "archivo.dolphin" }, { tipo: "accion", nombre: "archivo.terminal" }, { tipo: "accion", nombre: "archivo.copiar" },
                    { tipo: "separador" },
                    { tipo: "accion", nombre: "editar.expandir" }, { tipo: "accion", nombre: "editar.contraer" }
                ]
            }
        }
        TablaDatos {                                              // 1 · Cambios
            id: tablaCambios
            modelo: cambios.modelo
            claveAjustes: "cambios"
            umbralEstrecho: Kirigami.Units.gridUnit * 36
            mensajeVacio: "Sin cambios: el repo está al día" + (cambios.adelante > 0 ? " (" + cambios.adelante + " commit(s) sin subir: Repositorio › Subir a GitHub…)" : "")
            iconoVacio: "vcs-normal"
            columnas: [
                { ancho: 0, minimo: 14, conIcono: true },
                { ancho: 7, secundaria: true },
                { ancho: 8, semantica: true, conIcono: true },
                { ancho: 20, secundaria: true, estrecho: true }
            ]
            onOrdenar: (columna, descendente) => cambios.modelo.ordenar(columna, descendente)
            onFilaActualCambiada: fila => cambios.fijarFila(fila)
            onActivada: fila => ventana.irAPestana(0)
            menuContextual: MenuAcciones {
                acciones: ventana.registro
                conAtajos: false
                elementos: [{ tipo: "accion", nombre: "herr.aplicar" }, { tipo: "accion", nombre: "repo.seguridad" }, { tipo: "separador" },
                            { tipo: "accion", nombre: "archivo.dolphin" }, { tipo: "accion", nombre: "archivo.copiar" }]
            }
        }
        VistaTexto {                                              // 2 · Guía
            texto: studio.guia.texto
            markdown: true
            mensajeVacio: "Elige un documento en la navegación"
            iconoVacio: "help-contents"
        }
    }

    // ------------------------------------------------------------------ detalles por vista
    detalles: StackLayout {
        id: detalles
        property int anchoPreferido: Kirigami.Units.gridUnit * 24
        property int anchoMinimo: Kirigami.Units.gridUnit * 18
        currentIndex: ventana.indice

        PanelDetalles {                                           // 0 · Paquetes
            titulo: ventana.sel.paquete || "Paquetes"
            subtitulo: ventana.sel.tipo === "archivo" ? ventana.sel.rutaHome : (ventana.sel.detalle || paquetes.resumen)
            icono: ventana.sel.tipo === "archivo" ? "text-x-generic" : "package-x-generic"
            accionesCabecera: [ventana.accion("archivo.dolphin"), ventana.accion("archivo.copiar")]
            pestanas: [{ titulo: "Selección" }, { titulo: "Operación" }]
            SeleccionPaquete {}
            OperacionPaquete {}
        }
        PanelDetalles {                                           // 1 · Cambios
            titulo: cambios.ruta ? cambios.ruta.split("/").pop() : "Cambios"
            subtitulo: cambios.ruta || cambios.contexto
            icono: "vcs-commit"
            accionesCabecera: [ventana.accion("archivo.dolphin"), ventana.accion("archivo.copiar")]
            pestanas: [{ titulo: "Diferencia" }, { titulo: "Repositorio" }]
            Diferencia { id: diferencia }
            ResumenRepositorio {}
        }
        PanelDetalles {                                           // 2 · Guía
            titulo: studio.guia.titulo
            subtitulo: studio.guia.actual
            icono: "text-markdown"
            accionesCabecera: [ventana.accion("guia.abrir")]
            pestanas: [{ titulo: "Documento" }]
            Documento {}
        }
    }

    // ------------------------------------------------------------------ panel inferior
    inferior: PanelInferior { consola: studio.consola }

    // ------------------------------------------------------------------ diálogos
    Kirigami.PromptDialog {
        id: dialogoAplicar
        standardButtons: Kirigami.Dialog.Cancel
        property string verbo: "Aplicar"
        customFooterActions: [Kirigami.Action { text: dialogoAplicar.verbo; icon.name: ventana.accion("herr.aplicar").icono; onTriggered: { paquetes.aplicar(); dialogoAplicar.close() } }]
        function abrir() {
            if (!paquetes.haySeleccion) { ventana.mensajes.mostrar("Selecciona un paquete (o un archivo suyo) en el árbol.", "informacion"); return }
            const op = paquetes.operacion
            title = op.charAt(0).toUpperCase() + op.slice(1) + " " + paquetes.paquetesSeleccionados.join(", ")
            verbo = paquetes.necesitaTerminal ? "Abrir en una terminal" : op.charAt(0).toUpperCase() + op.slice(1)
            subtitle = paquetes.textoConfirmacion + (op === "eliminar" ? "" : "\n\nAntes se hace un respaldo en .backups/.") + "\n\n" + paquetes.ordenAplicar
            open()
        }
    }
    Kirigami.PromptDialog {
        id: dialogoSubir
        title: "Subir a GitHub"
        subtitle: "¿Subir " + cambios.adelante + " commit(s) de la rama " + cambios.rama + " a GitHub?\nEl repo es público: lo confirmado se publica."
        standardButtons: Kirigami.Dialog.Cancel
        customFooterActions: [Kirigami.Action { text: "Subir"; icon.name: "cloud-upload"; enabled: cambios.hayParaSubir; onTriggered: { cambios.subir(); dialogoSubir.close() } }]
    }
    DialogoSistema { id: dialogoSistema }
    dialogoAjustes: DialogoAjustesStudio {}
}
