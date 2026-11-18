// TerminalSimulacion — la salida de una simulación de main.sh (--dry-run, el «stow -n» de este gestor) como una
// terminal: la orden arriba, en monoespaciada; cada línea con el color de estado de lo que dice (un conflicto, en
// negativo; lo saltado o advertido, en neutro; lo hecho, en positivo; lo que haría, en el color del texto; el resto,
// tenue) y la acción que simula a la derecha. La usan la portada (abajo de las tarjetas) y la pestaña Simulación de la
// página del paquete. No ejecuta nada: la salida la pone el controlador (studio.catalogo).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    property var lineas: []
    property string orden: ""              // la orden que produjo la salida (o la que se correría)
    property string titulo: "Simulación"
    property var accion: null              // la Accion que simula (un botón con texto a la derecha)
    property string mensajeVacio: "Sin simular todavía"
    property string explicacionVacia: ""
    property string nombreAccesible: "Salida de la simulación"

    spacing: 0

    // el color de estado de una línea de main.sh (lib/stow_ops.sh y lib/logging.sh)
    function colorDe(linea) {
        if (linea.indexOf("[ERROR") >= 0 || linea.indexOf("Archivo real existe") >= 0 || linea.indexOf("✗") >= 0)
            return Kirigami.Theme.negativeTextColor
        if (linea.indexOf("Saltado") >= 0 || linea.indexOf("[WARN") >= 0)
            return Kirigami.Theme.neutralTextColor
        if (linea.indexOf("✓") >= 0 || linea.indexOf("[SUCCESS") >= 0)
            return Kirigami.Theme.positiveTextColor
        if (linea.indexOf("[dry-run]") >= 0 || linea.indexOf("[SECTION") >= 0)
            return Kirigami.Theme.textColor
        return Kirigami.Theme.disabledTextColor
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.leftMargin: Kirigami.Units.largeSpacing
        Layout.rightMargin: Kirigami.Units.smallSpacing
        Layout.topMargin: Kirigami.Units.smallSpacing
        Layout.bottomMargin: Kirigami.Units.smallSpacing
        spacing: Kirigami.Units.smallSpacing
        Kirigami.Icon {
            source: "utilities-terminal"
            implicitWidth: Kirigami.Units.iconSizes.small
            implicitHeight: implicitWidth
        }
        QQC2.Label { text: raiz.titulo; font.bold: true }
        QQC2.Label {
            Layout.fillWidth: true
            text: raiz.orden
            font: Kirigami.Theme.fixedWidthFont
            color: Kirigami.Theme.disabledTextColor
            elide: Text.ElideMiddle
            textFormat: Text.PlainText
            QQC2.ToolTip.text: raiz.orden
            QQC2.ToolTip.visible: raiz.orden !== "" && zonaOrden.containsMouse && truncated
            QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
            MouseArea { id: zonaOrden; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
        }
        QQC2.Label {
            visible: raiz.lineas.length > 0
            text: raiz.lineas.length + (raiz.lineas.length === 1 ? " línea" : " líneas")
            color: Kirigami.Theme.disabledTextColor
            font: Kirigami.Theme.smallFont
        }
        BotonAccion { accion: raiz.accion; conTexto: true }
    }
    Kirigami.Separator { Layout.fillWidth: true }

    // el fondo de vista, como el de una terminal o un editor del esquema activo
    Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        Kirigami.Theme.colorSet: Kirigami.Theme.View
        Kirigami.Theme.inherit: false
        color: Kirigami.Theme.backgroundColor

        ListView {
            id: vista
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing
            clip: true
            model: raiz.lineas
            boundsBehavior: Flickable.StopAtBounds
            QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
            onCountChanged: positionViewAtEnd()
            Accessible.name: raiz.nombreAccesible
            Accessible.role: Accessible.List
            delegate: QQC2.Label {
                required property string modelData
                width: ListView.view.width
                leftPadding: Kirigami.Units.smallSpacing
                text: modelData
                textFormat: Text.PlainText
                wrapMode: Text.WrapAnywhere
                font: Kirigami.Theme.fixedWidthFont
                color: raiz.colorDe(modelData)
            }
            Kirigami.PlaceholderMessage {
                anchors.centerIn: parent
                width: parent.width - Kirigami.Units.gridUnit * 4
                visible: vista.count === 0
                icon.name: "view-preview"
                text: raiz.mensajeVacio
                explanation: raiz.explicacionVacia
            }
        }
    }
}
