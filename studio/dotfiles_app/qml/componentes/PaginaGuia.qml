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
            id: documento
            required property var modelData
            width: ListView.view.width
            text: modelData.texto
            highlighted: modelData.nombre === raiz.guia.nombreActual
            hoverEnabled: true
            leftInset: Kirigami.Units.smallSpacing / 2
            rightInset: Kirigami.Units.smallSpacing / 2
            leftPadding: Kirigami.Units.largeSpacing
            background: FondoFila { fila: documento }
            // 2026-11-19: el documento elegido teñido (dos bloques llenos, el de la barra y este, competían)
            contentItem: RowLayout {
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Icon { source: "view-list-text"; isMask: true; color: Kirigami.Theme.disabledTextColor; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
                QQC2.Label { text: documento.text; elide: Text.ElideRight; Layout.fillWidth: true; font.weight: documento.highlighted ? Font.DemiBold : Font.Normal }
            }
            onClicked: raiz.guia.fijarDocumento(modelData.ruta)
        }
    }
    ColumnLayout {
        QQC2.SplitView.fillWidth: true
        spacing: 0
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.smallSpacing
            Kirigami.Heading { level: 4; text: raiz.guia.titulo; elide: Text.ElideRight; Layout.fillWidth: true; Layout.leftMargin: Kirigami.Units.smallSpacing }
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
