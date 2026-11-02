// DialogoAjustesStudio — «Configurar Dotfiles Studio…» (Ctrl+Mayús+,): General. La preferencia `ui/tema` de 1.x ya no
// se ofrece (el tema es del escritorio); su clave queda en el archivo sin uso.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard
import GuiComun

DialogoAjustes {
    id: dialogo
    title: "Configurar Dotfiles Studio"
    readonly property var a: studio.ajustes
    modulos: [{ titulo: "General", icono: "configure", pagina: paginaGeneral }]
    onGuardado: { dialogo.a.guardar(); ventana.mensajes.mostrar("Preferencias guardadas.", "positivo") }

    Component {
        id: paginaGeneral
        ColumnLayout {
            function guardar() { dialogo.a.detallado = detallado.checked; studio.paquetes.detallado = detallado.checked; dialogo.a.terminal = terminal.text }
            FormCard.FormHeader { title: "Operaciones de main.sh" }
            FormCard.FormCard {
                FormCard.FormCheckDelegate { id: detallado; text: "Salida detallada (--verbose) por omisión"; description: "Lo que simular, instalar, adoptar y eliminar escriben en el panel inferior"; checked: dialogo.a.detallado }
                FormCard.FormTextFieldDelegate { id: terminal; label: "Terminal para lo que pregunta o pide sudo"; text: dialogo.a.terminal; placeholderText: "konsole" }
            }
            FormCard.FormHeader { title: "Lo que no se configura aquí" }
            FormCard.FormCard {
                FormCard.FormTextDelegate { text: "El tema, las fuentes y los iconos son los del escritorio (Preferencias del sistema). Los paquetes y sus archivos, en config.sh." }
            }
        }
    }
}
