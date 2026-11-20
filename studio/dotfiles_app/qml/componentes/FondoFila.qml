// FondoFila — el fondo de una fila de las listas propias de Dotfiles Studio (la barra lateral, los archivos de un
// paquete, los documentos de la guía) con el lenguaje de gui-comun 4.2: la elegida, un tinte del acento con su marca a la izquierda (no el
// bloque lleno del color de selección: el texto conserva su color); al pasar el ratón, un velo tenue; con el foco, un
// borde. Es la fila elegida de PanelNavegacion; cuando la base la ofrezca como pieza, esta se retira.
//     QQC2.ItemDelegate { id: fila; background: FondoFila { fila: fila } }
import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: raiz
    property var fila: null
    // la marca a la izquierda; sin ella, solo el tinte (donde algo ya ocupa ese borde)
    property bool conMarca: true
    readonly property bool elegida: !!fila && fila.highlighted
    readonly property bool encima: !!fila && fila.hovered
    readonly property bool pulsada: !!fila && fila.pressed

    radius: Kirigami.Units.cornerRadius
    color: elegida ? Kirigami.ColorUtils.tintWithAlpha(Kirigami.Theme.backgroundColor, Kirigami.Theme.highlightColor, encima || pulsada ? 0.30 : 0.22)
         : pulsada ? Kirigami.ColorUtils.tintWithAlpha(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, 0.14)
         : encima ? Kirigami.ColorUtils.tintWithAlpha(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, 0.07)
         : "transparent"
    border.width: !!fila && fila.visualFocus ? 1 : 0
    border.color: Kirigami.Theme.focusColor
    Behavior on color { ColorAnimation { duration: Kirigami.Units.shortDuration } }

    Rectangle {                                   // la marca de la elegida
        visible: raiz.elegida && raiz.conMarca
        anchors.left: parent.left
        anchors.leftMargin: Kirigami.Units.smallSpacing / 2
        anchors.verticalCenter: parent.verticalCenter
        width: Kirigami.Units.smallSpacing * 0.75
        height: Math.max(Kirigami.Units.smallSpacing * 2, parent.height - Kirigami.Units.smallSpacing * 2.5)
        radius: width / 2
        color: Kirigami.Theme.highlightColor
    }
}
