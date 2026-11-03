// PaginaSistema — lo que no es de un paquete, como la parte de software de las Preferencias del sistema: lo que el
// gestor necesita de la distribución (con su estado) y tres operaciones con su orden visible: dependencias (pide sudo:
// se abre en una terminal), fuentes de usuario y respaldo. Cada una se simula aquí mismo o se aplica tras la
// confirmación de su acción (sistema.<nombre>), que nombra sus consecuencias.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: raiz
    readonly property var sistema: studio.sistema
    readonly property var registro: studio.acciones
    clip: true
    contentWidth: availableWidth

    ColumnLayout {
        width: raiz.availableWidth
        spacing: Kirigami.Units.largeSpacing

        Kirigami.Heading { level: 1; text: "Sistema"; Layout.margins: Kirigami.Units.largeSpacing; Layout.bottomMargin: 0 }

        Kirigami.ListSectionHeader { text: "Lo que el gestor necesita de la distribución"; Layout.fillWidth: true }
        Flow {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            spacing: Kirigami.Units.smallSpacing
            Repeater {
                model: raiz.sistema.dependencias
                delegate: EtiquetaNivel {
                    required property var modelData
                    visible: text !== ""
                    text: modelData.nombre + (modelData.instalada ? "" : ": falta")
                    nivel: modelData.instalada ? "positivo" : "neutro"
                    icono: modelData.instalada ? "checkmark" : "dialog-warning"
                }
            }
        }

        Kirigami.ListSectionHeader { text: "Operaciones"; Layout.fillWidth: true }
        Repeater {
            model: raiz.sistema.operaciones
            delegate: Rectangle {
                id: tarjeta
                required property var modelData
                readonly property var info: raiz.sistema.info(modelData.nombre)
                readonly property var accion: raiz.registro.accion("sistema." + modelData.nombre)
                Layout.fillWidth: true
                Layout.leftMargin: Kirigami.Units.largeSpacing
                Layout.rightMargin: Kirigami.Units.largeSpacing
                implicitHeight: contenido.implicitHeight + Kirigami.Units.largeSpacing * 2
                radius: Kirigami.Units.cornerRadius
                color: Kirigami.Theme.backgroundColor
                border.width: 1
                border.color: Qt.alpha(Kirigami.Theme.textColor, 0.15)
                RowLayout {
                    id: contenido
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon {
                        source: tarjeta.accion ? tarjeta.accion.icono : "system-run"
                        Layout.preferredWidth: Kirigami.Units.iconSizes.large
                        Layout.preferredHeight: Kirigami.Units.iconSizes.large
                        Layout.alignment: Qt.AlignTop
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing
                        RowLayout {
                            Kirigami.Heading { level: 3; text: tarjeta.modelData.titulo }
                            EtiquetaNivel { visible: text !== ""; text: tarjeta.accion ? tarjeta.accion.operacionTexto : "" }
                            EtiquetaNivel { visible: text !== ""; text: tarjeta.modelData.sudo ? "pide sudo: en una terminal" : ""; icono: "utilities-terminal"; nivel: "neutro" }
                        }
                        QQC2.Label { text: tarjeta.modelData.texto; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        QQC2.Label {
                            text: tarjeta.info.orden
                            font: Kirigami.Theme.fixedWidthFont
                            color: Kirigami.Theme.disabledTextColor
                        }
                    }
                    ColumnLayout {
                        Layout.alignment: Qt.AlignTop
                        QQC2.Button {
                            text: "Simular"
                            icon.name: "view-preview"
                            enabled: !studio.tareas.activa
                            onClicked: raiz.sistema.correr(tarjeta.modelData.nombre, true)
                            QQC2.ToolTip.text: tarjeta.info.ordenSimular + " (no cambia nada; la salida, en F4)"
                            QQC2.ToolTip.visible: hovered
                        }
                        QQC2.Button {
                            text: "Aplicar…"
                            icon.name: "dialog-ok-apply"
                            enabled: tarjeta.accion ? tarjeta.accion.habilitada : false
                            onClicked: tarjeta.accion.disparar()
                        }
                    }
                }
            }
        }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }
}
