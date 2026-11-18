// BarraLateral — la columna de Discover: arriba, las categorías de paquetes con su recuento; después, las páginas del
// repositorio (Cambios con lo que hay sin confirmar, Seguridad, Sistema) y la Guía; abajo, la rama y lo que falta subir.
// Rediseño del 2026-11-18: un recuento que pide algo lleva su color de estado (lo que pide atención, en neutro; los
// hallazgos del escáner, en negativo); en la fila elegida, el del texto resaltado.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Rectangle {
    id: raiz
    readonly property var catalogo: studio.catalogo
    readonly property var espacio: studio.espacio
    readonly property var cambios: studio.cambios
    signal elegirFiltro(string nombre)
    signal elegirPagina(string nombre)

    color: Kirigami.Theme.backgroundColor
    Kirigami.Theme.colorSet: Kirigami.Theme.View
    implicitWidth: Kirigami.Units.gridUnit * 13

    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        Kirigami.ListSectionHeader { text: "Paquetes"; Layout.fillWidth: true }
        Repeater {
            model: raiz.catalogo.filtros
            delegate: Entrada {
                required property var modelData
                texto: modelData.texto
                icono: modelData.icono
                contador: modelData.contador
                nivel: modelData.nombre === "atencion" ? "neutro" : ""
                elegida: raiz.espacio.vista === "paquetes" && raiz.catalogo.filtro === modelData.nombre && raiz.catalogo.abierto === ""
                onClicked: raiz.elegirFiltro(modelData.nombre)
            }
        }
        Kirigami.ListSectionHeader { text: "Repositorio"; Layout.fillWidth: true }
        Entrada {
            texto: "Cambios sin confirmar"; icono: "vcs-locally-modified"; contador: raiz.cambios.cuantos
            elegida: raiz.espacio.vista === "cambios"; onClicked: raiz.elegirPagina("cambios")
        }
        Entrada {
            texto: "Seguridad"; icono: "security-high"; contador: studio.seguridad.escaneado ? studio.seguridad.cuantos : -1
            nivel: "negativo"
            elegida: raiz.espacio.vista === "seguridad"; onClicked: raiz.elegirPagina("seguridad")
        }
        Entrada { texto: "Sistema"; icono: "preferences-system"; elegida: raiz.espacio.vista === "sistema"; onClicked: raiz.elegirPagina("sistema") }
        Entrada { texto: "Guía"; icono: "help-contents"; elegida: raiz.espacio.vista === "guia"; onClicked: raiz.elegirPagina("guia") }
        Item { Layout.fillHeight: true }
        Kirigami.Separator { Layout.fillWidth: true }
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.largeSpacing
            Kirigami.Icon { source: "vcs-branch"; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
            QQC2.Label {
                Layout.fillWidth: true
                elide: Text.ElideRight
                text: raiz.cambios.rama + (raiz.cambios.adelante ? " · " + raiz.cambios.adelante + " sin subir" : " · al día con su remoto")
                color: Kirigami.Theme.disabledTextColor
                font: Kirigami.Theme.smallFont
            }
        }
    }

    component Entrada: QQC2.ItemDelegate {
        property string texto: ""
        property string icono: ""
        property int contador: -1
        property bool elegida: false
        property string nivel: ""               // el color del recuento cuando no es cero
        Layout.fillWidth: true
        highlighted: elegida
        text: texto
        icon.name: icono
        Accessible.name: texto + (contador >= 0 ? ", " + contador : "")
        contentItem: RowLayout {
            spacing: Kirigami.Units.smallSpacing
            Kirigami.Icon { source: parent.parent.icono; implicitWidth: Kirigami.Units.iconSizes.smallMedium; implicitHeight: implicitWidth }
            QQC2.Label { text: parent.parent.texto; elide: Text.ElideRight; Layout.fillWidth: true }
            QQC2.Label {
                readonly property var entrada: parent.parent
                visible: entrada.contador >= 0
                text: entrada.contador
                color: entrada.highlighted ? Kirigami.Theme.highlightedTextColor
                     : entrada.contador > 0 && entrada.nivel === "neutro" ? Kirigami.Theme.neutralTextColor
                     : entrada.contador > 0 && entrada.nivel === "negativo" ? Kirigami.Theme.negativeTextColor
                     : Kirigami.Theme.disabledTextColor
            }
        }
    }
}
