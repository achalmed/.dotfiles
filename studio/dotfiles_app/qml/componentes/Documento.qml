// Documento — Guía › Documento: título, tipo, estado y ruta del documento elegido, y abrirlo con el sistema.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: pagina
    readonly property var g: studio.guia
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.FormLayout {
            Layout.fillWidth: true
            QQC2.Label { Kirigami.FormData.label: "Título:"; text: pagina.g.titulo; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Tipo:"; visible: pagina.g.tipo !== ""; text: pagina.g.tipo }
            QQC2.Label { Kirigami.FormData.label: "Estado:"; visible: pagina.g.estadoDoc !== ""; text: pagina.g.estadoDoc }
            QQC2.Label { Kirigami.FormData.label: "Archivo:"; text: pagina.g.actual; color: Kirigami.Theme.disabledTextColor }
        }
        QQC2.Label {
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            text: "La Guía muestra los documentos del repo tal como están; para editarlos, ábrelos con el sistema."
            color: Kirigami.Theme.disabledTextColor
            font: Kirigami.Theme.smallFont
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            Item { Layout.fillWidth: true }
            BotonAccion { accion: studio.acciones.accion("herr.ejecutar"); conTexto: false }
            BotonAccion { accion: studio.acciones.accion("guia.abrir") }
        }
    }
}
