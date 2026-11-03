// TarjetaPaquete — un paquete en la portada, como una aplicación en Discover: el icono de su aplicación, el nombre, qué
// guarda, su estado y sus cifras (enlaces, híbridos, cambios sin confirmar) y, a la derecha, la operación que pide.
// Pulsar la tarjeta abre la página del paquete; el botón también, con esa operación elegida: nada se aplica desde aquí,
// porque antes hay que ver la comparación y el plan.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ItemDelegate {
    id: raiz
    property var datos: ({})
    signal abrir(string nombre, string operacion)

    hoverEnabled: true
    padding: Kirigami.Units.largeSpacing
    onClicked: raiz.abrir(datos.nombre || "", "")
    Accessible.name: (datos.nombre || "") + ", " + (datos.textoEstado || "") + ". " + (datos.descripcion || "")
    Accessible.role: Accessible.Button

    background: Rectangle {
        radius: Kirigami.Units.cornerRadius
        color: raiz.hovered || raiz.visualFocus ? Qt.alpha(Kirigami.Theme.highlightColor, 0.10) : Kirigami.Theme.backgroundColor
        border.width: 1
        border.color: raiz.visualFocus ? Kirigami.Theme.focusColor : Qt.alpha(Kirigami.Theme.textColor, 0.15)
    }

    contentItem: RowLayout {
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Icon {
            source: raiz.datos.icono || "package-x-generic"
            fallback: "package-x-generic"
            Layout.preferredWidth: Kirigami.Units.iconSizes.large
            Layout.preferredHeight: Kirigami.Units.iconSizes.large
            Layout.alignment: Qt.AlignTop
            opacity: raiz.datos.instalada === false ? 0.5 : 1
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing / 2
            RowLayout {
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Heading {
                    level: 3
                    text: raiz.datos.nombre || ""
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
            }
            QQC2.Label {
                text: (raiz.datos.aplicacion || "") + (raiz.datos.descripcion ? " · " + raiz.datos.descripcion : "")
                color: Kirigami.Theme.disabledTextColor
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            Flow {
                Layout.fillWidth: true
                Layout.topMargin: Kirigami.Units.smallSpacing
                spacing: Kirigami.Units.smallSpacing
                EtiquetaNivel { visible: text !== ""; text: raiz.datos.textoEstado || ""; nivel: raiz.datos.nivel || "" }
                EtiquetaNivel {
                    visible: text !== ""
                    text: raiz.datos.total ? raiz.datos.enlazados + "/" + raiz.datos.total + " enlazados" : ""
                    icono: "emblem-symbolic-link"
                }
                EtiquetaNivel { visible: text !== ""; text: raiz.datos.hibridos ? raiz.datos.hibridos + " híbrido" + (raiz.datos.hibridos > 1 ? "s" : "") : ""; icono: "document-edit" }
                EtiquetaNivel { visible: text !== ""; text: raiz.datos.cambios ? raiz.datos.cambios + " sin confirmar" : ""; icono: "vcs-locally-modified"; nivel: "neutro" }
                EtiquetaNivel { visible: text !== ""; text: raiz.datos.instalada === false ? "aplicación no instalada" : ""; icono: "dialog-information" }
            }
        }
        QQC2.Button {
            visible: (raiz.datos.textoPide || "") !== ""
            text: (raiz.datos.textoPide || "") + "…"
            icon.name: raiz.datos.pide === "adoptar" ? "document-import" : "emblem-symbolic-link"
            Layout.alignment: Qt.AlignTop
            onClicked: raiz.abrir(raiz.datos.nombre, raiz.datos.pide)
            QQC2.ToolTip.text: "Abre la comparación y el plan antes de " + (raiz.datos.textoPide || "").toLowerCase()
            QQC2.ToolTip.visible: hovered
            QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
        }
    }
}
