// DialogoSistema — las operaciones del menú Herramientas (fuentes de usuario, dependencias, respaldo): qué hace, la
// orden, y dos salidas: «Simular» (--dry-run, al panel inferior) y «Aplicar» (lo que pide sudo, en una terminal).
import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Kirigami.PromptDialog {
    id: dialogo
    property string nombre: ""
    property var info: ({})
    standardButtons: Kirigami.Dialog.Cancel
    customFooterActions: [
        Kirigami.Action { text: "Simular"; icon.name: "system-run"; visible: dialogo.info.simulable === true; onTriggered: { studio.sistema.correr(dialogo.nombre, true); dialogo.close() } },
        Kirigami.Action { text: dialogo.info.sudo === true ? "Aplicar en una terminal" : "Aplicar"; icon.name: dialogo.info.sudo === true ? "utilities-terminal" : "dialog-ok-apply"; onTriggered: { studio.sistema.correr(dialogo.nombre, false); dialogo.close() } }
    ]
    function abrir(n) {
        nombre = n
        info = studio.sistema.info(n)
        title = info.titulo
        subtitle = info.texto + "\n\n" + (info.simulable ? "Simular: " + info.ordenSimular + "\n" : "") + "Aplicar: " + info.orden + (info.sudo ? "   (pide sudo: se abre en una terminal)" : "")
        open()
    }
}
