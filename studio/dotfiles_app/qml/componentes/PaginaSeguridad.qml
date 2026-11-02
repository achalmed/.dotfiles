// PaginaSeguridad — el escáner de credenciales, como un informe de gitleaks: qué se busca (los tipos de config.sh y los
// .env versionados), la orden de la terminal, y cada hallazgo con archivo, línea, tipo y una huella de la sesión.
// **El valor nunca aparece**: ni aquí, ni en la consola, ni en el informe copiado.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var seguridad: studio.seguridad
    readonly property var registro: studio.acciones

    spacing: 0

    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Icon {
            source: !raiz.seguridad.escaneado ? "security-medium" : raiz.seguridad.cuantos ? "security-low" : "security-high"
            Layout.preferredWidth: Kirigami.Units.iconSizes.huge
            Layout.preferredHeight: Kirigami.Units.iconSizes.huge
        }
        ColumnLayout {
            Layout.fillWidth: true
            Kirigami.Heading {
                level: 1
                text: !raiz.seguridad.escaneado ? "Escáner de credenciales"
                    : raiz.seguridad.cuantos ? raiz.seguridad.cuantos + " posible(s) dato(s) sensible(s)" : "Sin datos sensibles"
                Layout.fillWidth: true
            }
            QQC2.Label {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                color: Kirigami.Theme.disabledTextColor
                text: "Revisa lo que subiría un «git add .» (lo versionado y lo nuevo sin ignorar) con los patrones de config.sh, "
                      + "los mismos que «" + raiz.seguridad.orden + "». Se informa archivo, línea, tipo y una huella; el valor no se muestra."
            }
        }
        BotonAccion { accion: raiz.registro.accion("seg.escanear"); conTexto: true }
        BotonAccion { accion: raiz.registro.accion("seg.main"); conTexto: true }
        BotonAccion { accion: raiz.registro.accion("seg.copiar"); conTexto: true }
    }
    Kirigami.Separator { Layout.fillWidth: true }

    QQC2.SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        orientation: Qt.Horizontal

        ListView {
            id: lista
            QQC2.SplitView.fillWidth: true
            clip: true
            model: raiz.seguridad.hallazgos
            boundsBehavior: Flickable.StopAtBounds
            QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
            Accessible.name: "Hallazgos del escáner"
            header: RowLayout {
                width: ListView.view.width - Kirigami.Units.largeSpacing * 2      // el relleno del ItemDelegate de las filas
                x: Kirigami.Units.largeSpacing
                visible: lista.count > 0
                spacing: 0
                Cabecera { texto: "Archivo"; Layout.preferredWidth: parent.width - Kirigami.Units.gridUnit * 27 }
                Cabecera { texto: "Línea"; Layout.preferredWidth: Kirigami.Units.gridUnit * 4 }
                Cabecera { texto: "Tipo"; Layout.preferredWidth: Kirigami.Units.gridUnit * 14 }
                Cabecera { texto: "Huella"; Layout.preferredWidth: Kirigami.Units.gridUnit * 9 }
            }
            delegate: QQC2.ItemDelegate {
                id: fila
                required property var modelData
                width: ListView.view.width
                onDoubleClicked: studio.espacio.abrirDolphin(raiz.seguridad.rutaDe(modelData.archivo))
                Accessible.name: modelData.archivo + ", línea " + modelData.linea + ": " + modelData.tipo
                contentItem: RowLayout {
                    spacing: 0
                    QQC2.Label {
                        text: fila.modelData.archivo
                        elide: Text.ElideMiddle
                        font: Kirigami.Theme.fixedWidthFont
                        Layout.preferredWidth: fila.availableWidth - Kirigami.Units.gridUnit * 27
                    }
                    QQC2.Label { text: fila.modelData.linea || "—"; Layout.preferredWidth: Kirigami.Units.gridUnit * 4 }
                    RowLayout {
                        Layout.preferredWidth: Kirigami.Units.gridUnit * 14
                        EtiquetaEstado { texto: fila.modelData.tipo; nivel: "negativo" }
                        Item { Layout.fillWidth: true }
                    }
                    QQC2.Label {
                        text: fila.modelData.huella
                        color: Kirigami.Theme.disabledTextColor
                        font: Kirigami.Theme.fixedWidthFont
                        Layout.preferredWidth: Kirigami.Units.gridUnit * 9
                    }
                }
            }
            Kirigami.PlaceholderMessage {
                anchors.centerIn: parent
                width: parent.width - Kirigami.Units.gridUnit * 4
                visible: lista.count === 0
                icon.name: raiz.seguridad.escaneado ? "security-high" : "security-medium"
                text: raiz.seguridad.escaneado ? "Nada que revisar" : "Sin escanear todavía"
                explanation: raiz.seguridad.escaneado ? "Ningún patrón casa en lo que se subiría."
                                                      : "Escanear (Ctrl+Alt+S) lee los archivos sin cambiar nada. Hágalo antes de confirmar."
            }
        }

        ColumnLayout {
            QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 16
            spacing: 0
            Kirigami.ListSectionHeader { text: "Qué se busca"; Layout.fillWidth: true }
            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: raiz.seguridad.tipos
                QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
                Accessible.name: "Tipos de secreto que reconoce el escáner"
                delegate: QQC2.Label {
                    required property string modelData
                    width: ListView.view.width
                    leftPadding: Kirigami.Units.largeSpacing
                    topPadding: Kirigami.Units.smallSpacing / 2
                    text: "• " + modelData
                    elide: Text.ElideRight
                }
            }
            QQC2.Label {
                Layout.fillWidth: true
                Layout.margins: Kirigami.Units.smallSpacing
                wrapMode: Text.WordWrap
                font: Kirigami.Theme.smallFont
                color: Kirigami.Theme.disabledTextColor
                text: "Un falso positivo revisado se añade a SENSITIVE_SCAN_ALLOWLIST en config.sh. La huella vale solo en esta sesión: "
                      + "sirve para ver que dos hallazgos son el mismo secreto, no para recuperarlo."
            }
        }
    }

    component Cabecera: QQC2.Label {
        property string texto: ""
        text: texto
        font.bold: true
        padding: Kirigami.Units.smallSpacing
    }
}
