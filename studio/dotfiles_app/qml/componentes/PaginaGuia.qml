// PaginaGuia — los documentos del repo (README y docs/): la lista a la izquierda y el elegido a la derecha, sin su
// frontmatter. «Abrir el documento con el sistema» (guia.abrir) lo lleva al editor.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.SplitView {
    id: raiz
    readonly property var guia: studio.guia
    orientation: Qt.Horizontal

    ListView {
        QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 14
        clip: true
        model: raiz.guia.documentos
        Accessible.name: "Documentos del repo"
        header: Kirigami.ListSectionHeader { text: "Documentos"; width: ListView.view.width }
        delegate: QQC2.ItemDelegate {
            required property var modelData
            width: ListView.view.width
            text: modelData.texto
            icon.name: modelData.icono
            highlighted: modelData.nombre === raiz.guia.nombreActual
            onClicked: raiz.guia.fijarDocumento(modelData.ruta)
        }
    }
    ColumnLayout {
        QQC2.SplitView.fillWidth: true
        spacing: 0
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.smallSpacing
            QQC2.Label { text: raiz.guia.titulo; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
            BotonAccion { accion: studio.acciones.accion("guia.abrir"); conTexto: false }
        }
        VistaTexto {
            Layout.fillWidth: true
            Layout.fillHeight: true
            texto: raiz.guia.texto
            markdown: true
            mensajeVacio: "Elija un documento"
            iconoVacio: "help-contents"
        }
    }
}
