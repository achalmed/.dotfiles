// PaginaCambios — lo que las aplicaciones reescribieron en el repo, como las actualizaciones pendientes de Discover: la
// lista de archivos con cambios sin confirmar (con los híbridos señalados), la diferencia del elegido lado a lado
// (último commit ⟷ repo, con el filtro clean de texstudio.ini y los secretos ocultos) y, debajo, el mensaje y
// «Confirmar este archivo» (escáner → git add -- ruta → git commit -- ruta; nunca git add .). Subir a GitHub es una
// publicación y pide confirmación (acción repo.subir).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var cambios: studio.cambios
    readonly property var registro: studio.acciones
    property var ventana: null

    function enfocarMensaje() { mensaje.forceActiveFocus() }
    function seleccionar(fila) { tabla.seleccionarFila(fila, true); cambios.fijarFila(fila) }
    function confirmar() {
        const e = cambios.confirmar(mensaje.text)
        if (e) { if (ventana) ventana.notificar(e, "aviso"); mensaje.forceActiveFocus() } else mensaje.text = ""
    }

    spacing: 0

    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.largeSpacing
        Kirigami.Heading { level: 1; text: "Cambios sin confirmar"; Layout.fillWidth: true }
        QQC2.Label {
            text: "rama " + raiz.cambios.rama + (raiz.cambios.adelante ? " · " + raiz.cambios.adelante + " commit(s) sin subir" : "")
                  + (raiz.cambios.atras ? " · " + raiz.cambios.atras + " por traer" : "")
            color: Kirigami.Theme.disabledTextColor
        }
        BotonAccion { accion: raiz.registro.accion("repo.subir"); conTexto: true }
    }
    Kirigami.Separator { Layout.fillWidth: true }

    QQC2.SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        orientation: Qt.Horizontal

        TablaDatos {
            id: tabla
            QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 27
            QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 14
            modelo: raiz.cambios.modelo
            claveAjustes: "cambios"
            umbralEstrecho: Kirigami.Units.gridUnit * 30
            mensajeVacio: "Sin cambios: el repo está al día"
            iconoVacio: "vcs-normal"
            columnas: [
                { ancho: 0, minimo: 12, conIcono: true },
                { ancho: 7, secundaria: true },
                { ancho: 8, semantica: true, conIcono: true },
                { ancho: 12, secundaria: true, estrecho: true }
            ]
            onOrdenar: (columna, descendente) => raiz.cambios.modelo.ordenar(columna, descendente)
            onFilaActualCambiada: fila => raiz.cambios.fijarFila(fila)
        }

        ColumnLayout {
            QQC2.SplitView.fillWidth: true
            spacing: 0
            VistaComparacion {
                Layout.fillWidth: true
                Layout.fillHeight: true
                diferencia: raiz.cambios.comparacion
                mensajeVacio: raiz.cambios.hayCambios ? "Elija un archivo para ver su diferencia entera antes de confirmarlo" : "Nada que confirmar"
            }
            Kirigami.Separator { Layout.fillWidth: true }
            RowLayout {
                Layout.fillWidth: true
                Layout.margins: Kirigami.Units.smallSpacing
                enabled: raiz.cambios.ruta !== ""
                QQC2.TextField {
                    id: mensaje
                    Layout.fillWidth: true
                    placeholderText: "Mensaje del commit, en español: qué cambió y por qué"
                    text: raiz.cambios.mensajeSugerido
                    Accessible.name: "Mensaje del commit"
                    Keys.onReturnPressed: event => { if (event.modifiers & Qt.ControlModifier) raiz.confirmar(); else event.accepted = false }
                    Connections { target: raiz.cambios; function onFilaCambiada() { mensaje.text = raiz.cambios.mensajeSugerido } }
                }
                QQC2.Button {
                    text: "Confirmar este archivo"
                    icon.name: "vcs-commit"
                    highlighted: true
                    onClicked: raiz.confirmar()
                    QQC2.ToolTip.text: "Escanea credenciales y, si sale limpio, confirma solo " + raiz.cambios.ruta + " (Ctrl+Intro)"
                    QQC2.ToolTip.visible: hovered
                }
            }
        }
    }
}
