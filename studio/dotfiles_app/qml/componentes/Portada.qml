// Portada — la forma propia aprobada el 2026-11-18: arriba, los paquetes como tarjetas (el título de la categoría con su
// recuento y la cuadrícula de dos o tres columnas según el ancho); abajo, la terminal con la simulación de lo que se ve
// (`main.sh instalar --dry-run`, el «stow -n» de este gestor; Ctrl+Mayús+Intro), que nunca escribe. Un divisor reparte el
// alto entre las dos y se recuerda. La categoría y la búsqueda las fija la ventana en studio.catalogo; pulsar una tarjeta
// abre la página del paquete. Si config.sh no se lee, el vacío lo explica (el error ya fue a las notificaciones).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import QtCore
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.SplitView {
    id: raiz
    readonly property var catalogo: studio.catalogo
    readonly property var filtroActual: catalogo.filtros.find(f => f.nombre === catalogo.filtro) || { texto: "Paquetes", contador: 0 }
    property real altoTerminal: Kirigami.Units.gridUnit * 11
    signal abrir(string nombre, string operacion)

    orientation: Qt.Vertical
    Settings { category: "portada"; property alias divisor: raiz.altoTerminal }

    ColumnLayout {
        QQC2.SplitView.fillHeight: true
        QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 8
        spacing: 0

        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.largeSpacing
            Kirigami.Heading {
                level: 1
                text: raiz.filtroActual.texto
                Layout.fillWidth: true
                elide: Text.ElideRight
            }
            QQC2.Label {
                text: raiz.catalogo.tarjetas.length + (raiz.catalogo.tarjetas.length === 1 ? " paquete" : " paquetes")
                      + (raiz.catalogo.texto ? " con «" + raiz.catalogo.texto + "»" : "")
                color: Kirigami.Theme.disabledTextColor
            }
        }

        GridView {
            id: cuadricula
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            clip: true
            model: raiz.catalogo.tarjetas
            readonly property int columnas: Math.max(1, Math.floor(width / (Kirigami.Units.gridUnit * 22)))
            cellWidth: Math.floor(width / columnas)
            cellHeight: Kirigami.Units.gridUnit * 6
            keyNavigationEnabled: true
            boundsBehavior: Flickable.StopAtBounds
            QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
            Accessible.name: "Paquetes"
            Accessible.role: Accessible.List
            delegate: Item {
                required property var modelData
                width: cuadricula.cellWidth
                height: cuadricula.cellHeight
                TarjetaPaquete {
                    anchors.fill: parent
                    anchors.rightMargin: Kirigami.Units.largeSpacing
                    anchors.bottomMargin: Kirigami.Units.largeSpacing
                    datos: parent.modelData
                    onAbrir: (nombre, operacion) => raiz.abrir(nombre, operacion)
                }
            }
            Kirigami.PlaceholderMessage {
                anchors.centerIn: parent
                width: parent.width - Kirigami.Units.gridUnit * 4
                visible: cuadricula.count === 0
                icon.name: raiz.catalogo.error !== "" ? "dialog-error"
                         : raiz.catalogo.filtro === "atencion" ? "checkmark" : "package-x-generic"
                text: raiz.catalogo.error !== "" ? "No se pudo leer config.sh"
                    : raiz.catalogo.texto !== "" ? "Ningún paquete ni archivo casa con «" + raiz.catalogo.texto + "»"
                    : raiz.catalogo.filtro === "atencion" ? "Todo en orden: ningún paquete pide atención"
                    : raiz.catalogo.filtro === "cambios" ? "Ningún paquete tiene cambios sin confirmar"
                    : raiz.catalogo.filtro === "activos" ? "Ningún paquete está enlazado del todo" : "Sin paquetes en STOW_PACKAGES"
                explanation: raiz.catalogo.error
            }
        }
    }

    // 2026-11-19: sin salida, la terminal es una línea (la orden y «Simular lo que se ve»); antes, un vacío de un tercio
    // de la ventana que cortaba las tarjetas. Con salida, su alto de siempre (y se recuerda)
    readonly property bool conSalida: raiz.catalogo.salidaPortada.length > 0 || studio.tareas.activa
    QQC2.ToolBar {
        visible: !raiz.conSalida
        QQC2.SplitView.minimumHeight: implicitHeight
        QQC2.SplitView.maximumHeight: implicitHeight
        position: QQC2.ToolBar.Footer
        RowLayout {
            anchors.fill: parent
            Kirigami.Icon { source: "utilities-terminal"; isMask: true; color: Kirigami.Theme.disabledTextColor; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth; Layout.leftMargin: Kirigami.Units.largeSpacing }
            QQC2.Label { text: "Simulación"; font.weight: Font.DemiBold }
            QQC2.Label { text: raiz.catalogo.ordenPortada; font: Kirigami.Theme.fixedWidthFont; color: Kirigami.Theme.disabledTextColor; elide: Text.ElideMiddle; Layout.fillWidth: true }
            BotonAccion { accion: studio.acciones.accion("paq.simular"); conTexto: true }
        }
    }
    TerminalSimulacion {
        visible: raiz.conSalida
        QQC2.SplitView.preferredHeight: raiz.altoTerminal
        QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 5
        onHeightChanged: if (raiz.resizing) raiz.altoTerminal = height
        titulo: "Simulación"
        orden: raiz.catalogo.salidaPortadaDe || raiz.catalogo.ordenPortada
        lineas: raiz.catalogo.salidaPortada
        accion: studio.acciones.accion("paq.simular")
        nombreAccesible: "Salida de la simulación de los paquetes a la vista"
        mensajeVacio: "Sin simular todavía"
        explicacionVacia: "Simular (Ctrl+Mayús+Intro) corre la instalación de los paquetes a la vista con --dry-run: "
                          + "main.sh dice qué enlazaría y qué saltaría, sin tocar el disco."
    }
}
