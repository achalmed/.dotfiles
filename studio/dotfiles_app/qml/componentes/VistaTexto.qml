// VistaTexto — texto de solo lectura: el diff de un cambio (monoespaciado, con resaltado `Diff` de KSyntaxHighlighting
// si el módulo está) o un documento en Markdown (la Guía). Con mensaje de vacío. Candidato a GuiComun.VistaTexto.
import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

QQC2.Control {
    id: raiz
    property string texto: ""
    property bool markdown: false
    property string definicion: "Diff"                   // la definición de resaltado (solo sin markdown)
    property string mensajeVacio: ""
    property string iconoVacio: "text-x-generic"
    property string nombreAccesible: markdown ? "Documento" : "Texto"
    padding: 0
    Kirigami.Theme.colorSet: Kirigami.Theme.View
    Kirigami.Theme.inherit: false
    background: Rectangle { color: Kirigami.Theme.backgroundColor }
    contentItem: QQC2.ScrollView {
        QQC2.ScrollBar.horizontal.policy: raiz.markdown ? QQC2.ScrollBar.AlwaysOff : QQC2.ScrollBar.AsNeeded
        QQC2.TextArea {
            id: area
            readOnly: true
            text: raiz.texto
            textFormat: raiz.markdown ? TextEdit.MarkdownText : TextEdit.PlainText
            font: raiz.markdown ? Kirigami.Theme.defaultFont : Kirigami.Theme.fixedWidthFont
            wrapMode: raiz.markdown ? TextEdit.Wrap : TextEdit.NoWrap
            selectByMouse: true
            background: null
            leftPadding: Kirigami.Units.largeSpacing * (raiz.markdown ? 3 : 1)
            rightPadding: leftPadding
            topPadding: Kirigami.Units.largeSpacing
            onLinkActivated: enlace => Qt.openUrlExternally(enlace)
            Accessible.name: raiz.nombreAccesible
            Loader {
                active: !raiz.markdown && raiz.definicion !== ""
                source: "Resaltado.qml"
                onLoaded: { item.nombreDefinicion = raiz.definicion; item.textEdit = area }
            }
        }
    }
    Kirigami.PlaceholderMessage {
        anchors.centerIn: parent
        width: parent.width - Kirigami.Units.gridUnit * 4
        visible: raiz.texto === "" && raiz.mensajeVacio !== ""
        text: raiz.mensajeVacio
        icon.name: raiz.iconoVacio
    }
}
