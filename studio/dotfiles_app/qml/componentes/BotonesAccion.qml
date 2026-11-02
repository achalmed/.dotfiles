// BotonesAccion — el pie de las páginas de detalles: Ejecutar (F5) y Aplicar (Ctrl+Intro), ligados a las mismas
// acciones de la barra (una sola definición en Python), para quien trabaja con el ratón.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

RowLayout {
    property bool conAplicar: true
    Layout.fillWidth: true
    spacing: Kirigami.Units.smallSpacing
    Item { Layout.fillWidth: true }
    QQC2.Button {
        readonly property var a: studio.acciones.accion("herr.ejecutar")
        text: a.textoPlano; icon.name: a.icono; enabled: a.habilitada
        onClicked: a.disparar()
        QQC2.ToolTip.text: a.descripcion + " (" + a.atajoTexto + ")"; QQC2.ToolTip.visible: hovered
    }
    QQC2.Button {
        readonly property var a: studio.acciones.accion("herr.aplicar")
        visible: conAplicar && a.visible
        highlighted: true
        text: a.textoPlano; icon.name: a.icono; enabled: a.habilitada
        onClicked: a.disparar()
        QQC2.ToolTip.text: a.descripcion + " (" + a.atajoTexto + ")"; QQC2.ToolTip.visible: hovered
    }
}
