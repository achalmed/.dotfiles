// EtiquetaEstado — una etiqueta redondeada con el estado de un paquete o de un archivo («Enlazado», «Solo en HOME»,
// «Híbrido»…), con el color semántico del tema según su nivel (positivo · neutro · negativo · vacío = neutro apagado).
import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Rectangle {
    id: raiz
    property string texto: ""
    property string nivel: ""
    property string icono: ""

    visible: texto !== ""
    implicitWidth: fila.implicitWidth + Kirigami.Units.smallSpacing * 3
    implicitHeight: fila.implicitHeight + Kirigami.Units.smallSpacing
    radius: height / 2
    color: nivel === "positivo" ? Kirigami.Theme.positiveBackgroundColor
         : nivel === "negativo" ? Kirigami.Theme.negativeBackgroundColor
         : nivel === "neutro" ? Kirigami.Theme.neutralBackgroundColor
         : Qt.alpha(Kirigami.Theme.textColor, 0.08)
    readonly property color colorTexto: nivel === "positivo" ? Kirigami.Theme.positiveTextColor
         : nivel === "negativo" ? Kirigami.Theme.negativeTextColor
         : nivel === "neutro" ? Kirigami.Theme.neutralTextColor
         : Kirigami.Theme.disabledTextColor
    Accessible.role: Accessible.StaticText
    Accessible.name: texto

    Row {
        id: fila
        anchors.centerIn: parent
        spacing: Kirigami.Units.smallSpacing / 2
        Kirigami.Icon {
            visible: raiz.icono !== ""
            source: raiz.icono
            width: Kirigami.Units.iconSizes.small
            height: width
            color: raiz.colorTexto
            anchors.verticalCenter: parent.verticalCenter
        }
        QQC2.Label {
            text: raiz.texto
            color: raiz.colorTexto
            font: Kirigami.Theme.smallFont
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
