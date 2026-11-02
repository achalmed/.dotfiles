// SeleccionPaquete — Paquetes › Selección: el paquete con el foco (estado, archivos por estado, cada archivo con su
// explicación, la nota de calibre y KOReader) o el archivo (ruta en HOME y en el repo, estado, a dónde apunta el
// enlace, híbrido). El color solo en el estado, semántico.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: pagina
    readonly property var s: studio.paquetes.seleccion
    readonly property bool hay: s.tipo !== undefined
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff

    function colorEstado(estado) {
        switch (estado) {
        case "activo": return Kirigami.Theme.positiveTextColor
        case "conflicto": return Kirigami.Theme.negativeTextColor
        case "pendiente": return Kirigami.Theme.activeTextColor
        case "parcial": return Kirigami.Theme.neutralTextColor
        default: return Kirigami.Theme.disabledTextColor
        }
    }

    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.PlaceholderMessage {
            Layout.fillWidth: true
            visible: !pagina.hay
            text: "Selecciona un paquete o un archivo"
            explanation: "Aquí se ve qué está enlazado, qué pide atención y por qué; la pestaña Operación dice qué hará F5 y Ctrl+Intro."
            icon.name: "package-x-generic"
        }
        Kirigami.FormLayout {
            Layout.fillWidth: true
            visible: pagina.hay && pagina.s.tipo === "archivo"
            QQC2.Label { Kirigami.FormData.label: "Paquete:"; text: pagina.s.paquete || "" }
            QQC2.Label { Kirigami.FormData.label: "En HOME:"; text: pagina.s.rutaHome || ""; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "En el repo:"; text: (pagina.s.rutaRepo || "") + (pagina.s.enRepo ? "" : " (no existe)"); wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Estado:"; text: pagina.s.estado || ""; color: pagina.colorEstado(pagina.s.estado) }
            QQC2.Label { Kirigami.FormData.label: "Qué significa:"; text: pagina.s.explicacion || ""; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "El enlace apunta a:"; visible: (pagina.s.destino || "") !== ""; text: pagina.s.destino || ""; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true; font: Kirigami.Theme.smallFont }
            QQC2.Label { Kirigami.FormData.label: "Híbrido:"; visible: pagina.s.hibrido === true; text: "sí: mezcla preferencias y estado; su diff se lee entero antes de confirmar"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        Kirigami.FormLayout {
            Layout.fillWidth: true
            visible: pagina.hay && pagina.s.tipo === "paquete"
            QQC2.Label { Kirigami.FormData.label: "Estado:"; text: pagina.s.estado || ""; color: pagina.colorEstado(pagina.s.estado) }
            QQC2.Label { Kirigami.FormData.label: "Archivos:"; text: (pagina.s.total || 0) + " en PACKAGE_FILES · " + (pagina.s.detalle || "") }
            QQC2.Label { Kirigami.FormData.label: "Carpeta:"; text: pagina.s.rutaRepo || ""; color: Kirigami.Theme.disabledTextColor }
        }
        QQC2.Label {
            visible: pagina.hay && pagina.s.sustituye === true
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            text: (pagina.s.paquete || "") + " guarda de forma atómica y sustituye el enlace por un archivo real al usar la aplicación: «Adoptar» lo repone."
            color: Kirigami.Theme.neutralTextColor
            font: Kirigami.Theme.smallFont
        }
        Kirigami.Separator { visible: pagina.hay && pagina.s.tipo === "paquete"; Layout.fillWidth: true }
        Repeater {
            model: pagina.hay && pagina.s.tipo === "paquete" ? pagina.s.archivos : []
            delegate: RowLayout {
                required property var modelData
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Icon {
                    source: modelData.estado === "activo" ? "vcs-normal" : modelData.estado === "conflicto" ? "vcs-conflicting" : modelData.estado === "pendiente" ? "vcs-update-required" : "emblem-remove"
                    implicitWidth: Kirigami.Units.iconSizes.small
                    implicitHeight: implicitWidth
                }
                QQC2.Label { text: modelData.rel; Layout.fillWidth: true; elide: Text.ElideMiddle; Accessible.name: modelData.rel + ": " + modelData.estado }
                QQC2.Label { text: modelData.estado; color: pagina.colorEstado(modelData.estado); font: Kirigami.Theme.smallFont }
            }
        }
        BotonesAccion { visible: pagina.hay }
    }
}
