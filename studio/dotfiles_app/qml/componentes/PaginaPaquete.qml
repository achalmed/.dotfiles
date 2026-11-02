// PaginaPaquete — la página de un paquete, como la de una aplicación en Discover, pero con lo que un gestor de
// configuración necesita ver ANTES de tocar nada:
//   cabecera: la aplicación, qué guarda el paquete, su estado y sus cifras;
//   operación: Instalar · Adoptar · Actualizar · Quitar enlaces, qué hace, la orden exacta de main.sh (copiable),
//              el resumen del plan y, si no se puede, por qué; Simular y Aplicar (que pide confirmación);
//   archivos: cada archivo con su estado y lo que la operación hará con él;
//   y a la derecha, del archivo elegido: Comparación (repo ⟷ HOME lado a lado), Simulación (la salida de main.sh) y
//   Detalles (la aplicación de la que depende, rutas compartidas, huérfanos, notas, destino de cada enlace).
// Todo sale de studio.catalogo; las órdenes las corren las acciones paq.* (aplicacion.py).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var catalogo: studio.catalogo
    readonly property var registro: studio.acciones
    readonly property var p: catalogo.pagina
    readonly property var pl: catalogo.plan
    property int pestana: 0

    spacing: 0

    // ------------------------------------------------------------------ cabecera
    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Icon {
            source: raiz.p.icono || "package-x-generic"
            fallback: "package-x-generic"
            Layout.preferredWidth: Kirigami.Units.iconSizes.huge
            Layout.preferredHeight: Kirigami.Units.iconSizes.huge
        }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing / 2
            Kirigami.Heading { level: 1; text: raiz.p.nombre || ""; Layout.fillWidth: true; elide: Text.ElideRight }
            QQC2.Label {
                text: "Configuración de " + (raiz.p.aplicacion || "") + (raiz.p.descripcion ? ": " + raiz.p.descripcion : "")
                color: Kirigami.Theme.disabledTextColor
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            Flow {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                EtiquetaEstado { texto: raiz.p.textoEstado || ""; nivel: raiz.p.nivel || "" }
                EtiquetaEstado { texto: raiz.p.total ? raiz.p.enlazados + "/" + raiz.p.total + " enlazados" : ""; icono: "emblem-symbolic-link" }
                EtiquetaEstado {
                    texto: raiz.p.instalada === undefined ? "" : raiz.p.instalada ? raiz.p.aplicacion + " instalada" : raiz.p.aplicacion + " no instalada"
                    nivel: raiz.p.instalada ? "" : "neutro"
                    icono: raiz.p.instalada ? "checkmark" : "dialog-warning"
                }
                EtiquetaEstado { texto: raiz.p.hibridos ? raiz.p.hibridos + " híbrido" + (raiz.p.hibridos > 1 ? "s" : "") : ""; icono: "document-edit" }
                EtiquetaEstado { texto: raiz.p.cambios ? raiz.p.cambios + " sin confirmar" : ""; icono: "vcs-locally-modified"; nivel: "neutro" }
            }
        }
        QQC2.ToolButton {
            icon.name: "system-file-manager"
            text: "Carpeta del paquete"
            display: QQC2.AbstractButton.TextBesideIcon
            Layout.alignment: Qt.AlignTop
            onClicked: studio.espacio.abrirDolphin(raiz.p.rutaRepo || "")
            QQC2.ToolTip.text: "Muestra en Dolphin la carpeta del paquete en el repo"
            QQC2.ToolTip.visible: hovered
        }
    }

    // ------------------------------------------------------------------ la operación, su orden y su plan
    Rectangle {
        Layout.fillWidth: true
        implicitHeight: operacion.implicitHeight + Kirigami.Units.largeSpacing * 2
        color: Kirigami.Theme.alternateBackgroundColor
        ColumnLayout {
            id: operacion
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            spacing: Kirigami.Units.smallSpacing
            RowLayout {
                spacing: Kirigami.Units.smallSpacing
                QQC2.Label { text: "Operación:"; font.bold: true }
                Repeater {
                    model: raiz.catalogo.operaciones
                    delegate: QQC2.Button {
                        required property var modelData
                        text: modelData.texto
                        icon.name: raiz.registro.accion("paq." + modelData.nombre).icono
                        checkable: true
                        checked: raiz.catalogo.operacion === modelData.nombre
                        flat: !checked
                        onClicked: raiz.catalogo.fijarOperacion(modelData.nombre)
                        QQC2.ToolTip.text: modelData.queHace + (modelData.motivo ? "\n\n" + modelData.motivo : "\n\n" + modelData.resumen)
                        QQC2.ToolTip.visible: hovered
                        QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                    }
                }
                QQC2.CheckBox {
                    visible: raiz.catalogo.operacion === "instalar"
                    text: "Reemplazar los archivos reales (con respaldo)"
                    checked: raiz.catalogo.forzar
                    onToggled: raiz.catalogo.forzar = checked
                }
                Item { Layout.fillWidth: true }
            }
            QQC2.Label {
                text: raiz.pl.queHace || ""
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                QQC2.TextField {
                    id: orden
                    Layout.fillWidth: true
                    readOnly: true
                    text: raiz.catalogo.ordenAplicar
                    font: Kirigami.Theme.fixedWidthFont
                    Accessible.name: "Orden exacta que se ejecutará"
                    QQC2.ToolTip.text: "La orden que corre al aplicar (en la carpeta del repo). Simular añade --dry-run."
                    QQC2.ToolTip.visible: hovered
                }
                QQC2.ToolButton {
                    icon.name: "edit-copy"
                    onClicked: { orden.selectAll(); orden.copy(); orden.deselect() }
                    Accessible.name: "Copiar la orden"
                    QQC2.ToolTip.text: "Copiar la orden"
                    QQC2.ToolTip.visible: hovered
                }
                BotonAccion { accion: raiz.registro.accion("paq.simular"); conTexto: true }
                QQC2.Button {                                       // el botón principal, como «Instalar» en Discover
                    readonly property var accion: raiz.registro.accion("paq.aplicar")
                    text: accion.textoPlano + "…"
                    icon.name: accion.icono
                    enabled: accion.habilitada
                    highlighted: true
                    onClicked: accion.disparar()
                    QQC2.ToolTip.text: "Pide confirmación con lo que cambiará (Ctrl+Intro)"
                    QQC2.ToolTip.visible: hovered
                }
            }
            RowLayout {
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Icon { source: "view-list-details"; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
                QQC2.Label { text: "Plan: " + (raiz.pl.resumen || "—"); font.bold: true }
                EtiquetaEstado { texto: raiz.pl.respaldo ? "respaldo antes en .backups/" : ""; icono: "document-save" }
                EtiquetaEstado { texto: raiz.pl.terminal ? "pregunta: se abre en una terminal" : ""; icono: "utilities-terminal"; nivel: "neutro" }
                EtiquetaEstado { texto: raiz.pl.estadoOperacion ? studio.acciones.accion("paq." + raiz.catalogo.operacion).operacionTexto : "" }
            }
            Kirigami.InlineMessage {
                Layout.fillWidth: true
                visible: !!raiz.pl.bloqueo
                type: Kirigami.MessageType.Warning
                text: raiz.pl.bloqueo || ""
            }
        }
    }
    Kirigami.Separator { Layout.fillWidth: true }

    // ------------------------------------------------------------------ archivos | comparación, simulación, detalles
    QQC2.SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        orientation: Qt.Horizontal

        ColumnLayout {
            QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 22
            QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 14
            spacing: 0
            Kirigami.ListSectionHeader { text: "Archivos y qué les pasará"; Layout.fillWidth: true }
            ListView {
                id: archivos
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: raiz.pl.archivos || []
                currentIndex: (raiz.pl.archivos || []).findIndex(a => a.rel === raiz.catalogo.archivo)
                keyNavigationEnabled: true
                boundsBehavior: Flickable.StopAtBounds
                QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
                Accessible.name: "Archivos del paquete"
                onCurrentIndexChanged: if (currentIndex >= 0 && raiz.pl.archivos) raiz.catalogo.fijarArchivo(raiz.pl.archivos[currentIndex].rel)
                delegate: QQC2.ItemDelegate {
                    id: fila
                    required property var modelData
                    required property int index
                    width: ListView.view.width
                    highlighted: ListView.isCurrentItem
                    onClicked: { archivos.currentIndex = index; raiz.catalogo.fijarArchivo(modelData.rel) }
                    Accessible.name: modelData.rel + ": " + modelData.accion + (modelData.detalle ? ", " + modelData.detalle : "")
                    contentItem: RowLayout {
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.Icon {
                            source: ({ activo: "emblem-symbolic-link", conflicto: "emblem-warning", pendiente: "list-add",
                                       local: "document-import", ausente: "emblem-question" })[fila.modelData.estado] || "text-x-generic"
                            implicitWidth: Kirigami.Units.iconSizes.smallMedium
                            implicitHeight: implicitWidth
                            Layout.alignment: Qt.AlignTop
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0
                            RowLayout {
                                QQC2.Label {
                                    text: fila.modelData.rel
                                    elide: Text.ElideMiddle
                                    Layout.fillWidth: true
                                    font.bold: fila.highlighted
                                    color: fila.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                                }
                                EtiquetaEstado { texto: fila.modelData.hibrido ? "híbrido" : "" }
                            }
                            QQC2.Label {
                                text: fila.modelData.accion + (fila.modelData.detalle ? " · " + fila.modelData.detalle : "")
                                color: fila.highlighted ? Kirigami.Theme.highlightedTextColor
                                     : fila.modelData.nivel === "negativo" ? Kirigami.Theme.negativeTextColor
                                     : fila.modelData.nivel === "positivo" ? Kirigami.Theme.positiveTextColor
                                     : fila.modelData.nivel === "neutro" ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.disabledTextColor
                                font: Kirigami.Theme.smallFont
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }
            QQC2.Label {
                visible: (raiz.pl.huerfanos || []).length > 0
                Layout.fillWidth: true
                Layout.margins: Kirigami.Units.smallSpacing
                wrapMode: Text.WordWrap
                color: Kirigami.Theme.neutralTextColor
                text: "Huérfanos en el repo (ya no están en config.sh): " + (raiz.pl.huerfanos || []).join(", ")
            }
        }

        ColumnLayout {
            QQC2.SplitView.fillWidth: true
            spacing: 0
            QQC2.TabBar {
                id: pestanas
                Layout.fillWidth: true
                currentIndex: raiz.pestana
                onCurrentIndexChanged: raiz.pestana = currentIndex
                QQC2.TabButton { text: "Comparación"; icon.name: "document-compare" }
                QQC2.TabButton { text: "Simulación" + (raiz.catalogo.salida.length ? " (" + raiz.catalogo.salida.length + ")" : ""); icon.name: "view-preview" }
                QQC2.TabButton { text: "Detalles"; icon.name: "documentinfo" }
            }
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: pestanas.currentIndex

                // Comparación del archivo elegido
                ColumnLayout {
                    spacing: 0
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.margins: Kirigami.Units.smallSpacing
                        visible: raiz.catalogo.archivo !== ""
                        QQC2.Label { text: raiz.catalogo.archivo; font.bold: true; elide: Text.ElideMiddle; Layout.fillWidth: true }
                        QQC2.Label {
                            text: raiz.catalogo.filaPlan.accion ? "→ " + raiz.catalogo.filaPlan.accion : ""
                            color: Kirigami.Theme.disabledTextColor
                        }
                        QQC2.ToolButton {
                            icon.name: "go-home"
                            onClicked: studio.espacio.abrirDolphin(raiz.catalogo.rutaEnHome(raiz.catalogo.archivo))
                            Accessible.name: "Mostrar en Dolphin el archivo de HOME"
                            QQC2.ToolTip.text: "Mostrar en Dolphin el archivo de HOME"
                            QQC2.ToolTip.visible: hovered
                        }
                        QQC2.ToolButton {
                            icon.name: "folder-git"
                            onClicked: studio.espacio.abrirDolphin(raiz.catalogo.rutaEnRepo(raiz.catalogo.archivo))
                            Accessible.name: "Mostrar en Dolphin el archivo del repo"
                            QQC2.ToolTip.text: "Mostrar en Dolphin el archivo del repo"
                            QQC2.ToolTip.visible: hovered
                        }
                        BotonAccion { accion: raiz.registro.accion("archivo.abrir"); conTexto: false }
                    }
                    VistaDiferencia {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        diferencia: raiz.catalogo.comparacion
                        mensajeVacio: "Elija un archivo a la izquierda para comparar el repo con HOME"
                    }
                }

                // Simulación: la salida de main.sh, sin rutas de la máquina
                ColumnLayout {
                    spacing: 0
                    QQC2.Label {
                        Layout.margins: Kirigami.Units.smallSpacing
                        visible: raiz.catalogo.salidaDe !== ""
                        text: raiz.catalogo.salidaDe
                        font.bold: true
                    }
                    ListView {
                        id: salida
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: raiz.catalogo.salida
                        boundsBehavior: Flickable.StopAtBounds
                        QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
                        onCountChanged: positionViewAtEnd()
                        Accessible.name: "Salida de main.sh"
                        delegate: QQC2.Label {
                            required property string modelData
                            width: ListView.view.width
                            leftPadding: Kirigami.Units.smallSpacing
                            text: modelData
                            textFormat: Text.PlainText
                            wrapMode: Text.WrapAnywhere
                            font: Kirigami.Theme.fixedWidthFont
                            color: modelData.indexOf("[dry-run]") >= 0 ? Kirigami.Theme.textColor
                                 : modelData.indexOf("Saltado") >= 0 || modelData.indexOf("WARN") >= 0 ? Kirigami.Theme.neutralTextColor
                                 : modelData.indexOf("ERROR") >= 0 ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.disabledTextColor
                        }
                        Kirigami.PlaceholderMessage {
                            anchors.centerIn: parent
                            width: parent.width - Kirigami.Units.gridUnit * 4
                            visible: salida.count === 0
                            icon.name: "view-preview"
                            text: "Sin simular todavía"
                            explanation: "Simular (Ctrl+Mayús+Intro) corre la orden con --dry-run: main.sh dice qué haría sin tocar el disco."
                        }
                    }
                }

                // Detalles: dependencia, rutas compartidas, huérfanos, notas y enlaces
                QQC2.ScrollView {
                    clip: true
                    ColumnLayout {
                        width: parent.width
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.ListSectionHeader { text: "Depende de"; Layout.fillWidth: true }
                        Repeater {
                            model: raiz.p.dependencias || []
                            delegate: RowLayout {
                                required property var modelData
                                Layout.leftMargin: Kirigami.Units.largeSpacing
                                Kirigami.Icon { source: modelData.ok ? "checkmark" : "dialog-warning"; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
                                QQC2.Label { text: modelData.nombre + " " + modelData.detalle + ": " + modelData.texto; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            }
                        }
                        Kirigami.ListSectionHeader { text: "Conflictos con otros paquetes"; Layout.fillWidth: true }
                        QQC2.Label {
                            Layout.leftMargin: Kirigami.Units.largeSpacing
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: (raiz.p.compartidas || []).length === 0 ? "Ninguna ruta de este paquete la reclama otro."
                                : (raiz.p.compartidas || []).map(c => c.ruta + " (también en " + c.paquetes.join(", ") + ")").join("\n")
                            color: (raiz.p.compartidas || []).length ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.disabledTextColor
                        }
                        Kirigami.ListSectionHeader { text: "Archivos huérfanos en el repo"; Layout.fillWidth: true }
                        QQC2.Label {
                            Layout.leftMargin: Kirigami.Units.largeSpacing
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: (raiz.p.huerfanos || []).length === 0 ? "Ninguno: todo lo que hay en la carpeta del paquete está en config.sh."
                                : (raiz.p.huerfanos || []).join("\n") + "\n(adoptar pregunta si borrarlos; sin respuesta, se conservan)"
                            color: Kirigami.Theme.disabledTextColor
                        }
                        Kirigami.ListSectionHeader { visible: (raiz.p.notas || []).length > 0; text: "Notas"; Layout.fillWidth: true }
                        Repeater {
                            model: raiz.p.notas || []
                            delegate: QQC2.Label {
                                required property string modelData
                                Layout.leftMargin: Kirigami.Units.largeSpacing
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                text: "• " + modelData
                            }
                        }
                        Kirigami.ListSectionHeader { text: "Enlaces"; Layout.fillWidth: true }
                        Repeater {
                            model: raiz.p.archivos || []
                            delegate: QQC2.Label {
                                required property var modelData
                                Layout.leftMargin: Kirigami.Units.largeSpacing
                                Layout.fillWidth: true
                                wrapMode: Text.WrapAnywhere
                                font: Kirigami.Theme.fixedWidthFont
                                text: "~/" + modelData.rel + (modelData.destino ? "  →  " + modelData.destino : "  (" + modelData.explicacion + ")")
                                    + (modelData.carpeta ? "   [carpeta]" : "")
                            }
                        }
                    }
                }
            }
        }
    }
}
