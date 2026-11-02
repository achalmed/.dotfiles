// VistaDiferencia — la comparación de un archivo lado a lado, como Meld o Kompare: arriba qué es cada lado («Repositorio»
// · «HOME», «Último commit» · «Repositorio»…), las notas (híbrido, filtro clean, secretos ocultos) y debajo las filas
// con sus números de línea; una línea quitada y una añadida contiguas van en la misma fila. Viene de Git Studio
// (`git-studio/studio/git_app/qml/componentes/VistaDiferencia.qml`) sin los botones por trozo: aquí solo se lee.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

ColumnLayout {
    id: raiz

    property var diferencia                   // {ruta, izquierda, derecha, filas, anadidas, quitadas, binario, vacia, notas…}
    property string mensajeVacio: "Elija un archivo para ver su comparación"

    spacing: 0
    readonly property real anchoNumero: Kirigami.Units.gridUnit * 2.6
    readonly property bool hay: !!raiz.diferencia && !!raiz.diferencia.ruta

    // qué es cada lado
    Item {
        Layout.fillWidth: true
        visible: raiz.hay
        implicitHeight: lados.implicitHeight + Kirigami.Units.smallSpacing * 2
        Rectangle { anchors.fill: parent; color: Kirigami.Theme.alternateBackgroundColor }
        RowLayout {
            id: lados
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing
            spacing: 0
            Lado { texto: raiz.hay ? raiz.diferencia.izquierda : ""; icono: "go-previous"; Layout.preferredWidth: (parent.width - 1) / 2 }
            Kirigami.Separator { Layout.fillHeight: true }
            Lado { texto: raiz.hay ? raiz.diferencia.derecha : ""; icono: "go-next"; Layout.fillWidth: true }
            QQC2.Label {
                visible: raiz.hay && !raiz.diferencia.binario && !raiz.diferencia.vacia
                text: raiz.hay ? "+" + raiz.diferencia.anadidas + "  −" + raiz.diferencia.quitadas : ""
                color: Kirigami.Theme.disabledTextColor
                font: Kirigami.Theme.smallFont
                rightPadding: Kirigami.Units.smallSpacing
            }
        }
    }
    Repeater {
        model: raiz.hay ? raiz.diferencia.notas || [] : []
        delegate: Kirigami.InlineMessage {
            required property string modelData
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.smallSpacing
            Layout.bottomMargin: 0
            visible: true
            type: modelData.indexOf("secreto") >= 0 ? Kirigami.MessageType.Warning : Kirigami.MessageType.Information
            text: modelData
        }
    }
    Kirigami.InlineMessage {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        visible: raiz.hay && raiz.diferencia.recortado
        type: Kirigami.MessageType.Information
        text: "La diferencia es muy larga: se muestran las primeras filas. Ábrala en su editor para verla entera."
    }

    ListView {
        id: lista
        Layout.fillWidth: true
        Layout.fillHeight: true
        visible: raiz.hay && !raiz.diferencia.vacia
        clip: true
        model: raiz.hay ? raiz.diferencia.filas : null
        reuseItems: true
        boundsBehavior: Flickable.StopAtBounds
        QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
        Accessible.name: "Comparación de " + (raiz.hay ? raiz.diferencia.ruta : "")
        delegate: Loader {
            required property string tipo
            required property int izqNum
            required property string izq
            required property string izqTipo
            required property int derNum
            required property string der
            required property string derTipo
            width: ListView.view.width
            sourceComponent: tipo === "trozo" ? cTrozo : cLinea
        }
    }
    Kirigami.PlaceholderMessage {
        Layout.fillWidth: true
        Layout.fillHeight: true
        visible: !raiz.hay || raiz.diferencia.vacia
        text: !raiz.hay ? raiz.mensajeVacio : raiz.diferencia.binario ? "Archivo binario: no se compara línea a línea" : "Nada que comparar"
        icon.name: raiz.hay && raiz.diferencia.binario ? "application-octet-stream" : "document-compare"
    }

    function fondo(tipo) {
        switch (tipo) {
        case "quitada": return Kirigami.Theme.negativeBackgroundColor
        case "anadida": return Kirigami.Theme.positiveBackgroundColor
        case "vacia": return Qt.alpha(Kirigami.Theme.textColor, 0.04)
        default: return "transparent"
        }
    }

    component Lado: RowLayout {
        property string texto: ""
        property string icono: ""
        spacing: Kirigami.Units.smallSpacing
        Kirigami.Icon { source: parent.icono; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
        QQC2.Label { text: parent.texto; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
    }

    Component {
        id: cTrozo
        Rectangle {
            readonly property var f: parent
            implicitHeight: etiqueta.implicitHeight + Kirigami.Units.smallSpacing
            color: Qt.alpha(Kirigami.Theme.textColor, 0.06)
            QQC2.Label {
                id: etiqueta
                anchors.fill: parent
                anchors.leftMargin: Kirigami.Units.smallSpacing
                verticalAlignment: Text.AlignVCenter
                text: f.izq + (f.der ? "  " + f.der : "")
                font: Kirigami.Theme.fixedWidthFont
                color: Kirigami.Theme.disabledTextColor
                elide: Text.ElideRight
            }
        }
    }

    Component {
        id: cLinea
        Item {
            readonly property var f: parent
            implicitHeight: Math.max(izquierda.implicitHeight, derecha.implicitHeight)
            Mitad { id: izquierda; numero: f.izqNum; texto: f.izq; tipo: f.izqTipo; x: 0; width: Math.floor((parent.width - 1) / 2); height: parent.height }
            Kirigami.Separator { x: izquierda.width; height: parent.height }
            Mitad { id: derecha; numero: f.derNum; texto: f.der; tipo: f.derTipo; x: izquierda.width + 1; width: parent.width - x; height: parent.height }
        }
    }

    component Mitad: Rectangle {
        id: mitad
        property int numero: 0
        property string texto: ""
        property string tipo: "igual"
        color: raiz.fondo(tipo)
        implicitHeight: contenido.implicitHeight
        QQC2.Label {
            id: numeroLinea
            width: raiz.anchoNumero
            text: mitad.numero > 0 ? mitad.numero : ""
            horizontalAlignment: Text.AlignRight
            rightPadding: Kirigami.Units.smallSpacing
            font: Kirigami.Theme.fixedWidthFont
            color: Kirigami.Theme.disabledTextColor
            Accessible.ignored: true
        }
        QQC2.Label {
            id: contenido
            anchors.left: numeroLinea.right
            anchors.right: parent.right
            leftPadding: Kirigami.Units.smallSpacing
            text: mitad.tipo === "aviso" ? mitad.texto : mitad.texto.replace(/\t/g, "    ")
            textFormat: Text.PlainText
            wrapMode: Text.WrapAnywhere
            font: Kirigami.Theme.fixedWidthFont
            color: mitad.tipo === "aviso" ? Kirigami.Theme.disabledTextColor : Kirigami.Theme.textColor
        }
    }
}
