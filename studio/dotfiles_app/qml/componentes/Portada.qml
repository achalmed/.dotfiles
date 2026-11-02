// Portada — los paquetes como tarjetas, como la portada de Discover: el título de la categoría con su recuento, la
// cuadrícula (dos o tres columnas según el ancho) y el vacío explicado. La categoría y la búsqueda las fija la ventana
// en studio.catalogo; pulsar una tarjeta abre la página del paquete.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

ColumnLayout {
    id: raiz
    readonly property var catalogo: studio.catalogo
    readonly property var filtroActual: catalogo.filtros.find(f => f.nombre === catalogo.filtro) || { texto: "Paquetes", contador: 0 }
    signal abrir(string nombre, string operacion)

    spacing: 0

    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.largeSpacing
        Kirigami.Heading {
            level: 1
            text: raiz.filtroActual.texto
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
        QQC2.Label {
            text: raiz.catalogo.tarjetas.length + (raiz.catalogo.tarjetas.length === 1 ? " paquete" : " paquetes")
                  + (raiz.catalogo.texto ? " con «" + raiz.catalogo.texto + "»" : "")
            color: Kirigami.Theme.disabledTextColor
        }
    }
    Kirigami.InlineMessage {
        Layout.fillWidth: true
        Layout.leftMargin: Kirigami.Units.largeSpacing
        Layout.rightMargin: Kirigami.Units.largeSpacing
        visible: raiz.catalogo.error !== ""
        type: Kirigami.MessageType.Error
        text: "No se pudo leer config.sh: " + raiz.catalogo.error
    }

    GridView {
        id: cuadricula
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin: Kirigami.Units.largeSpacing
        clip: true
        model: raiz.catalogo.tarjetas
        readonly property int columnas: Math.max(1, Math.floor(width / (Kirigami.Units.gridUnit * 22)))
        cellWidth: Math.floor(width / columnas)
        cellHeight: Kirigami.Units.gridUnit * 7
        keyNavigationEnabled: true
        boundsBehavior: Flickable.StopAtBounds
        QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
        Accessible.name: "Paquetes"
        Accessible.role: Accessible.List
        delegate: Item {
            required property var modelData
            width: cuadricula.cellWidth
            height: cuadricula.cellHeight
            TarjetaPaquete {
                anchors.fill: parent
                anchors.rightMargin: Kirigami.Units.largeSpacing
                anchors.bottomMargin: Kirigami.Units.largeSpacing
                datos: parent.modelData
                onAbrir: (nombre, operacion) => raiz.abrir(nombre, operacion)
            }
        }
        Kirigami.PlaceholderMessage {
            anchors.centerIn: parent
            width: parent.width - Kirigami.Units.gridUnit * 4
            visible: cuadricula.count === 0 && raiz.catalogo.error === ""
            icon.name: raiz.catalogo.filtro === "atencion" ? "checkmark" : "package-x-generic"
            text: raiz.catalogo.texto !== "" ? "Ningún paquete ni archivo casa con «" + raiz.catalogo.texto + "»"
                : raiz.catalogo.filtro === "atencion" ? "Todo en orden: ningún paquete pide atención"
                : raiz.catalogo.filtro === "cambios" ? "Ningún paquete tiene cambios sin confirmar"
                : raiz.catalogo.filtro === "activos" ? "Ningún paquete está enlazado del todo" : "Sin paquetes en STOW_PACKAGES"
        }
    }
}
