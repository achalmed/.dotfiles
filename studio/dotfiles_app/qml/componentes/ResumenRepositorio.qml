// ResumenRepositorio — Cambios › Repositorio: la rama, los commits sin subir y por bajar, los cambios y los híbridos;
// releer, escanear credenciales y subir a GitHub.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: pagina
    readonly property var c: studio.cambios
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.FormLayout {
            Layout.fillWidth: true
            QQC2.Label { Kirigami.FormData.label: "Repo:"; text: studio.espacio.nombreRepo }
            QQC2.Label { Kirigami.FormData.label: "Rama:"; text: pagina.c.rama }
            QQC2.Label { Kirigami.FormData.label: "Sin subir:"; text: pagina.c.adelante + " commit(s)"; color: pagina.c.adelante > 0 ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.textColor }
            QQC2.Label { Kirigami.FormData.label: "Por bajar:"; text: pagina.c.atras + " commit(s)"; color: pagina.c.atras > 0 ? Kirigami.Theme.activeTextColor : Kirigami.Theme.textColor }
            QQC2.Label { Kirigami.FormData.label: "Cambios:"; text: pagina.c.cuantos + " sin confirmar" + (pagina.c.hibridos > 0 ? " · " + pagina.c.hibridos + " híbrido(s)" : "") }
        }
        QQC2.Label {
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            text: "Se confirma por ruta, con el diff entero a la vista y tras el escáner de credenciales; nunca todo de una vez. El repo es público."
            color: Kirigami.Theme.disabledTextColor
            font: Kirigami.Theme.smallFont
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            Item { Layout.fillWidth: true }
            BotonAccion { accion: studio.acciones.accion("repo.releer"); conTexto: false }
            BotonAccion { accion: studio.acciones.accion("repo.seguridad") }
            BotonAccion { accion: studio.acciones.accion("repo.subir") }
        }
    }
}
