// TarjetaPaquete — un paquete en la portada (la forma propia aprobada el 2026-11-18): el icono de su aplicación, del
// tema de iconos; el nombre con su estado de stow como un punto de color de estado (enlazado en positivo; a medias, sin
// enlazar o solo en HOME en neutro; un conflicto, un archivo real en HOME, en negativo aunque el paquete esté a medias;
// sin configuración, tenue); qué guarda; y una línea tenue con el número de archivos, los enlazados, los híbridos y lo
// que hay sin confirmar. A la derecha, la operación que pide. Pulsar la tarjeta abre la página del paquete; el botón
// también, con esa operación elegida: nada se aplica desde aquí, porque antes hay que ver la comparación y el plan.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ItemDelegate {
    id: raiz
    property var datos: ({})
    signal abrir(string nombre, string operacion)

    // el color del punto: el del estado de stow del paquete (calculado en Python: catalogo._tarjeta, «punto»)
    function colorPunto(nivel) {
        switch (nivel) {
        case "positivo": return Kirigami.Theme.positiveTextColor
        case "neutro": return Kirigami.Theme.neutralTextColor
        case "negativo": return Kirigami.Theme.negativeTextColor
        default: return Kirigami.Theme.disabledTextColor
        }
    }

    hoverEnabled: true
    padding: Kirigami.Units.largeSpacing
    onClicked: raiz.abrir(datos.nombre || "", "")
    Accessible.name: (datos.nombre || "") + ", " + (datos.textoEstado || "") + ". " + (datos.cifras || "")
    Accessible.description: datos.descripcion || ""
    Accessible.role: Accessible.Button

    background: Rectangle {
        color: raiz.hovered || raiz.visualFocus ? Kirigami.ColorUtils.tintWithAlpha(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, 0.05) : Kirigami.Theme.backgroundColor
        border.width: 1
        border.color: raiz.visualFocus ? Kirigami.Theme.focusColor : Qt.alpha(Kirigami.Theme.textColor, raiz.hovered ? 0.28 : 0.15)
        radius: Kirigami.Units.cornerRadius * 2
    }

    contentItem: RowLayout {
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Icon {
            source: raiz.datos.icono || "package-x-generic"
            fallback: "package-x-generic"
            Layout.preferredWidth: Kirigami.Units.iconSizes.large
            Layout.preferredHeight: Kirigami.Units.iconSizes.large
            Layout.alignment: Qt.AlignVCenter
            opacity: raiz.datos.instalada === false ? 0.5 : 1
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing / 2
            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Heading {
                    level: 3
                    text: raiz.datos.nombre || ""
                    elide: Text.ElideRight
                }
                // 2026-11-19: el estado como etiqueta de su nivel (la misma de la página del paquete), no un punto y texto de color
                EtiquetaNivel {
                    visible: text !== ""
                    text: raiz.datos.textoEstado || ""
                    nivel: (raiz.datos.punto || "") === "inactivo" ? "" : raiz.datos.punto || ""
                }
                Item { Layout.fillWidth: true }
            }
            QQC2.Label {
                text: (raiz.datos.aplicacion || "") + (raiz.datos.descripcion ? " · " + raiz.datos.descripcion : "")
                color: Kirigami.Theme.disabledTextColor
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            QQC2.Label {
                text: raiz.datos.cifras || ""
                color: Kirigami.Theme.disabledTextColor
                font: Kirigami.Theme.smallFont
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }
        QQC2.Button {
            visible: (raiz.datos.textoPide || "") !== ""
            text: (raiz.datos.textoPide || "") + "…"
            icon.name: raiz.datos.pide === "adoptar" ? "document-import" : "insert-link"
            Layout.alignment: Qt.AlignVCenter
            onClicked: raiz.abrir(raiz.datos.nombre, raiz.datos.pide)
            QQC2.ToolTip.text: "Abre la comparación y el plan antes de " + (raiz.datos.textoPide || "").toLowerCase()
            QQC2.ToolTip.visible: hovered
            QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
        }
    }
}
