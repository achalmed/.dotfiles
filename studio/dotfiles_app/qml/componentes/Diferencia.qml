// Diferencia — Cambios › Diferencia: el diff ENTERO del archivo elegido (o su contenido, si es nuevo) con resaltado
// Diff, y al pie el mensaje del commit y «Confirmar» (Ctrl+Intro): escáner → git add -- ruta → git commit -- ruta.
// Patrón de Kate y de Git Studio: la operación vive junto a su contexto.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var c: studio.cambios
    spacing: 0

    function confirmar() {
        const error = raiz.c.confirmar(campo.text)
        if (error) { ventana.mensajes.mostrar(error, "informacion"); campo.forceActiveFocus() }
        else campo.text = ""
    }
    Connections { target: raiz.c; function onFilaCambiada() { if (campo.text.trim() === "" || campo.text === raiz.c.mensajeSugeridoPrevio) campo.text = raiz.c.mensajeSugerido } }

    VistaTexto {
        Layout.fillWidth: true
        Layout.fillHeight: true
        texto: raiz.c.diferencia
        definicion: "Diff"
        nombreAccesible: "Diferencia"
        mensajeVacio: raiz.c.hayCambios ? "Selecciona un archivo: su diff entero aparece aquí antes de confirmarlo" : "Sin cambios que confirmar"
        iconoVacio: "vcs-diff"
    }
    QQC2.Label {
        visible: raiz.c.datos.hibrido === true
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        wrapMode: Text.WordWrap
        text: "Híbrido: la aplicación mezcla preferencias y estado en este archivo. Léelo entero: ni rutas privadas ni recientes."
        color: Kirigami.Theme.neutralTextColor
        font: Kirigami.Theme.smallFont
    }
    Kirigami.Separator { Layout.fillWidth: true }
    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        spacing: Kirigami.Units.smallSpacing
        QQC2.TextField {
            id: campo
            Layout.fillWidth: true
            placeholderText: "Mensaje del commit, en español (Ctrl+Intro)"
            enabled: raiz.c.ruta !== ""
            text: raiz.c.mensajeSugerido
            Keys.onPressed: event => { if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && (event.modifiers & Qt.ControlModifier)) { raiz.confirmar(); event.accepted = true } }
            Accessible.name: "Mensaje del commit"
        }
        QQC2.Button {
            readonly property var a: studio.acciones.accion("herr.aplicar")
            text: "Confirmar"
            icon.name: "vcs-commit"
            highlighted: true
            enabled: campo.enabled && campo.text.trim() !== "" && a.habilitada
            onClicked: raiz.confirmar()
            QQC2.ToolTip.text: "Escáner de credenciales y commit solo de este archivo (" + a.atajoTexto + ")"; QQC2.ToolTip.visible: hovered
        }
    }
}
