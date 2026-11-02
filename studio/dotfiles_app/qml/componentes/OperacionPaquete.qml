// OperacionPaquete — Paquetes › Operación: qué hará F5 (simular) y Ctrl+Intro (aplicar) sobre los paquetes
// seleccionados: Instalar · Adoptar · Eliminar (una marcada), «Detallado», «Reemplazar los archivos reales», la orden
// exacta de main.sh y el aviso de cuándo se abre en una terminal. Las mismas acciones del menú Acción.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: pagina
    readonly property var p: studio.paquetes
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.FormLayout {
            Layout.fillWidth: true
            QQC2.RadioButton { Kirigami.FormData.label: "Operación:"; text: "Instalar (repo → HOME)"; checked: pagina.p.operacion === "instalar"; onClicked: pagina.p.fijarOperacion("instalar") }
            QQC2.RadioButton { text: "Adoptar (HOME → repo)"; checked: pagina.p.operacion === "adoptar"; onClicked: pagina.p.fijarOperacion("adoptar") }
            QQC2.RadioButton { text: "Eliminar los enlaces"; checked: pagina.p.operacion === "eliminar"; onClicked: pagina.p.fijarOperacion("eliminar") }
            QQC2.Label { Kirigami.FormData.label: "Qué hace:"; text: pagina.p.descripcionOperacion; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            QQC2.CheckBox { Kirigami.FormData.label: "Opciones:"; text: "Salida detallada (--verbose)"; checked: pagina.p.detallado; onToggled: pagina.p.detallado = checked }
            QQC2.CheckBox { text: "Reemplazar los archivos reales de HOME (--force, con respaldo)"; enabled: pagina.p.operacion === "instalar"; checked: pagina.p.forzar; onToggled: pagina.p.forzar = checked }
            QQC2.Label { Kirigami.FormData.label: "Sobre:"; text: pagina.p.haySeleccion ? pagina.p.paquetesSeleccionados.join(", ") : "(selecciona un paquete en el árbol)"; wrapMode: Text.WordWrap; Layout.fillWidth: true; color: pagina.p.haySeleccion ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor }
            QQC2.Label { Kirigami.FormData.label: "F5 simula:"; text: pagina.p.ordenSimular; font: Kirigami.Theme.fixedWidthFont; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Ctrl+Intro aplica:"; text: pagina.p.ordenAplicar; font: Kirigami.Theme.fixedWidthFont; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
        }
        QQC2.Label {
            visible: pagina.p.necesitaTerminal
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            text: pagina.p.conflictosSeleccion + " archivo(s) existen en HOME y en el repo: al adoptar, main.sh pregunta cuál conservar, así que Aplicar lo abre en una terminal."
            color: Kirigami.Theme.neutralTextColor
            font: Kirigami.Theme.smallFont
        }
        QQC2.Label {
            visible: pagina.p.operacion === "eliminar"
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            text: "Eliminar no respalda: solo quita enlaces; los archivos siguen en el repo."
            color: Kirigami.Theme.disabledTextColor
            font: Kirigami.Theme.smallFont
        }
        BotonesAccion {}
    }
}
