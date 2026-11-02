// Main.qml — Dotfiles Studio (reingeniería 2026-11-02): un gestor de paquetes de configuración sobre
// GuiComun.VentanaBase, con la forma de Discover y no la de Dolphin. A la izquierda, las categorías de paquetes y las
// páginas del repositorio; arriba, volver, la búsqueda y las acciones de la página; en el centro, la portada de
// tarjetas o la página del paquete abierto (comparación y plan antes de cada operación), Cambios, Seguridad, Sistema o
// la Guía; la salida, plegada (F4). Ninguna orden se ejecuta aquí: todo lo hacen los controladores de Python
// (studio.*) y toda orden es main.sh o git. Ver docs/reingenieria.md.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import QtCore
import org.kde.kirigami as Kirigami
import GuiComun
import "componentes"

VentanaBase {
    id: ventana

    readonly property var espacio: studio.espacio
    readonly property var catalogo: studio.catalogo
    readonly property var registro: studio.acciones
    property bool mostrarSalida: false
    property alias pestanaPaquete: paginaPaquete.pestana
    readonly property int indice: espacio.vista === "paquetes" ? (catalogo.abierto ? 1 : 0)
                                : ({ cambios: 2, seguridad: 3, sistema: 4, guia: 5 })[espacio.vista] ?? 0

    title: espacio.nombreRepo + " — Dotfiles Studio"
    width: 1360
    height: 860
    minimumWidth: 980
    acciones: registro
    tareas: studio.tareas
    consola: studio.consola
    descripcion: descripcionStudio
    autor: "Edison Achalma (@achalmed)"
    sitio: "https://github.com/achalmed/.dotfiles"
    claveAjustes: "ventana"

    Settings {
        category: "gestor"
        property alias salida: ventana.mostrarSalida
    }
    onMostrarSalidaChanged: registro.marcar("ver.salida", mostrarSalida)
    Component.onCompleted: registro.marcar("ver.salida", mostrarSalida)

    function abrirPaquete(nombre, operacion) {
        espacio.fijarVista("paquetes")
        catalogo.abrir(nombre)
        if (operacion) catalogo.fijarOperacion(operacion)
    }

    // ------------------------------------------------------------------ lo que Python pide a la interfaz
    Connections {
        target: studio.interfaz
        function onPedir(nombre, datos) {
            switch (nombre) {
            case "buscar": busqueda.forceActiveFocus(); busqueda.selectAll(); break
            case "salida": ventana.mostrarSalida = !ventana.mostrarSalida; break
            case "confirmar": paginaCambios.confirmar(); break
            case "seleccionar_cambio": paginaCambios.seleccionar(datos.fila); break
            case "paleta": ventana.paleta.abrir(datos.texto || ""); break
            }
        }
    }
    Connections { target: ventana.espacio; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: ventana.catalogo; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: studio.cambios; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: studio.seguridad; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: studio.sistema; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Shortcut {
        sequence: "Esc"
        enabled: ventana.catalogo.abierto !== "" && ventana.espacio.vista === "paquetes" && !busqueda.activeFocus
        onActivated: ventana.catalogo.cerrar()
    }

    // ------------------------------------------------------------------ cabecera: volver, búsqueda y acciones
    header: QQC2.ToolBar {
        RowLayout {
            anchors.fill: parent
            spacing: Kirigami.Units.smallSpacing
            BotonAccion { accion: ventana.registro.accion("ver.portada"); conTexto: false; visible: ventana.indice === 1 }
            QQC2.Label {
                text: ventana.indice === 1 ? "Paquetes › " + ventana.catalogo.abierto : ventana.espacio.textoVista
                font.bold: true
                elide: Text.ElideRight
                Layout.leftMargin: Kirigami.Units.smallSpacing
            }
            Item { Layout.fillWidth: true }
            Kirigami.SearchField {
                id: busqueda
                Layout.preferredWidth: Kirigami.Units.gridUnit * 16
                placeholderText: "Buscar paquetes, aplicaciones o archivos (Ctrl+F)"
                onTextChanged: {
                    ventana.catalogo.buscar(text)
                    if (text !== "") { ventana.catalogo.cerrar(); ventana.espacio.fijarVista("paquetes") }
                }
                Keys.onEscapePressed: text = ""
                Accessible.name: "Buscar paquetes"
            }
            QQC2.ToolSeparator {}
            BotonAccion { accion: ventana.registro.accion("repo.releer"); conTexto: false }
            BotonAccion { accion: ventana.registro.accion("seg.escanear"); conTexto: false }
            BotonAccion { accion: ventana.registro.accion("ver.salida"); conTexto: false }
        }
    }

    // ------------------------------------------------------------------ barra lateral | páginas
    QQC2.SplitView {
        anchors.fill: parent
        orientation: Qt.Vertical

        RowLayout {
            QQC2.SplitView.fillHeight: true
            spacing: 0
            BarraLateral {
                Layout.fillHeight: true
                onElegirFiltro: nombre => { ventana.catalogo.fijarFiltro(nombre); ventana.catalogo.cerrar(); ventana.espacio.fijarVista("paquetes") }
                onElegirPagina: nombre => ventana.espacio.fijarVista(nombre)
            }
            Kirigami.Separator { Layout.fillHeight: true }
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: ventana.indice
                Portada { onAbrir: (nombre, operacion) => ventana.abrirPaquete(nombre, operacion) }
                PaginaPaquete { id: paginaPaquete }
                PaginaCambios { id: paginaCambios; ventana: ventana }
                PaginaSeguridad {}
                PaginaSistema {}
                PaginaGuia {}
            }
        }
        PanelInferior {
            visible: ventana.mostrarSalida
            QQC2.SplitView.preferredHeight: Kirigami.Units.gridUnit * 9
            QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 5
            consola: studio.consola
            onCerrar: ventana.mostrarSalida = false
        }
    }

    footer: BarraEstado {
        resumen: ventana.espacio.resumen
        contexto: ventana.espacio.contexto
        tareas: studio.tareas
        onProgresoPulsado: ventana.mostrarSalida = true
    }

    dialogoAjustes: DialogoAjustesStudio {}
}
