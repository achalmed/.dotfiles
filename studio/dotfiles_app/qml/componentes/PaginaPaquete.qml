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
                EtiquetaNivel { visible: text !== ""; text: raiz.p.textoEstado || ""; nivel: raiz.p.nivel || "" }
                EtiquetaNivel { visible: text !== ""; text: raiz.p.total ? raiz.p.enlazados + "/" + raiz.p.total + " enlazados" : ""; icono: "edit-link" }
                EtiquetaNivel {
                    visible: text !== ""
                    text: raiz.p.instalada === undefined ? "" : raiz.p.instalada ? raiz.p.aplicacion + " instalada" : raiz.p.aplicacion + " no instalada"
                    nivel: raiz.p.instalada ? "" : "neutro"
                    icono: raiz.p.instalada ? "checkmark" : "dialog-warning"
                }
                EtiquetaNivel { visible: text !== ""; text: raiz.p.hibridos ? raiz.p.hibridos + " híbrido" + (raiz.p.hibridos > 1 ? "s" : "") : ""; icono: "document-edit" }
                EtiquetaNivel { visible: text !== ""; text: raiz.p.cambios ? raiz.p.cambios + " sin confirmar" : ""; icono: "document-edit"; nivel: "neutro" }
            }
        }
        QQC2.ToolButton {
            icon.name: "folder-open"
            text: "Carpeta del paquete"
            display: QQC2.AbstractButton.TextBesideIcon
            Layout.alignment: Qt.AlignTop
            onClicked: studio.espacio.abrirDolphin(raiz.p.rutaRepo || "")
            QQC2.ToolTip.text: "Muestra en Dolphin la carpeta del paquete en el repo"
            QQC2.ToolTip.visible: hovered
        }
    }

    // ------------------------------------------------------------------ la operación, su orden y su plan
    // 2026-11-19: una sola tarjeta (radio y borde del tema) en lugar de una franja gris de borde a borde: arriba, la
    // operación en un pozo con Simular y Aplicar a la derecha; debajo, qué hace, la orden como código y el plan
    Rectangle {
        Layout.fillWidth: true
        Layout.leftMargin: Kirigami.Units.largeSpacing
        Layout.rightMargin: Kirigami.Units.largeSpacing
        Layout.bottomMargin: Kirigami.Units.largeSpacing
        implicitHeight: operacion.implicitHeight + Kirigami.Units.largeSpacing * 2
        radius: Kirigami.Units.cornerRadius * 2
        readonly property bool oscuro: Kirigami.ColorUtils.brightnessForColor(Kirigami.Theme.backgroundColor) === Kirigami.ColorUtils.Dark
        color: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, oscuro ? 0.04 : 0.025)
        border.width: 1
        border.color: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, oscuro ? 0.14 : 0.11)
        ColumnLayout {
            id: operacion
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            spacing: Kirigami.Units.smallSpacing + Kirigami.Units.smallSpacing / 2
            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing
                SelectorSegmentado {
                    titulo: "Operación"
                    opciones: raiz.catalogo.operaciones.map(o => ({ clave: o.nombre, texto: o.texto, icono: raiz.registro.accion("paq." + o.nombre).icono,
                                                                   descripcion: o.queHace + (o.motivo ? "\n\n" + o.motivo : "\n\n" + o.resumen) }))
                    onElegida: clave => raiz.catalogo.fijarOperacion(clave)
                    Binding on actual { value: raiz.catalogo.operacion }
                }
                QQC2.CheckBox {
                    visible: raiz.catalogo.operacion === "instalar"
                    text: "Reemplazar los archivos reales (con respaldo)"
                    checked: raiz.catalogo.forzar
                    onToggled: raiz.catalogo.forzar = checked
                }
                Item { Layout.fillWidth: true }
                BotonAccion { accion: raiz.registro.accion("paq.simular"); conTexto: true }
                BotonPrincipal {                                    // la acción principal, como «Instalar» en Discover
                    accion: raiz.registro.accion("paq.aplicar")
                    text: accion.textoPlano + "…"
                    QQC2.ToolTip.text: "Pide confirmación con lo que cambiará (Ctrl+Intro)"
                    QQC2.ToolTip.visible: hovered
                    QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                }
            }
            QQC2.Label {
                text: raiz.pl.queHace || ""
                color: Kirigami.Theme.disabledTextColor
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            // la orden exacta, como código en un pozo, con su botón de copiar
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: filaOrden.implicitHeight + Kirigami.Units.smallSpacing * 2
                radius: Kirigami.Units.cornerRadius
                color: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, parent.parent.oscuro ? 0.08 : 0.05)
                RowLayout {
                    id: filaOrden
                    anchors.fill: parent
                    anchors.leftMargin: Kirigami.Units.largeSpacing
                    anchors.rightMargin: Kirigami.Units.smallSpacing
                    QQC2.Label {
                        id: orden
                        Layout.fillWidth: true
                        text: "$ " + raiz.catalogo.ordenAplicar
                        font: Kirigami.Theme.fixedWidthFont
                        elide: Text.ElideMiddle
                        Accessible.name: "Orden exacta que se ejecutará: " + raiz.catalogo.ordenAplicar
                        QQC2.ToolTip.text: "La orden que corre al aplicar (en la carpeta del repo). Simular añade --dry-run."
                        QQC2.ToolTip.visible: ratonOrden.hovered
                        HoverHandler { id: ratonOrden }
                    }
                    TextEdit { id: copiador; visible: false }          // solo para el portapapeles
                    QQC2.ToolButton {
                        icon.name: "edit-copy"
                        display: QQC2.AbstractButton.IconOnly
                        text: "Copiar la orden"
                        onClicked: { copiador.text = raiz.catalogo.ordenAplicar; copiador.selectAll(); copiador.copy(); copiador.text = "" }
                        Accessible.name: text
                        QQC2.ToolTip.text: text
                        QQC2.ToolTip.visible: hovered
                    }
                }
            }
            Flow {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                QQC2.Label { text: "Plan: " + (raiz.pl.resumen || "—"); font.weight: Font.DemiBold; rightPadding: Kirigami.Units.smallSpacing }
                EtiquetaNivel { visible: text !== ""; text: raiz.pl.respaldo ? "respaldo antes en .backups/" : ""; icono: "document-save" }
                EtiquetaNivel { visible: text !== ""; text: raiz.pl.terminal ? "pregunta: se abre en una terminal" : ""; icono: "utilities-terminal"; nivel: "neutro" }
                EtiquetaNivel { visible: text !== ""; text: raiz.pl.estadoOperacion ? studio.acciones.accion("paq." + raiz.catalogo.operacion).operacionTexto : "" }
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
                    hoverEnabled: true
                    leftInset: Kirigami.Units.smallSpacing / 2
                    rightInset: Kirigami.Units.smallSpacing / 2
                    topInset: 1
                    bottomInset: 1
                    leftPadding: Kirigami.Units.largeSpacing
                    background: FondoFila { fila: fila }
                    readonly property color colorNivel: modelData.nivel === "negativo" ? Kirigami.Theme.negativeTextColor
                                                     : modelData.nivel === "positivo" ? Kirigami.Theme.positiveTextColor
                                                     : modelData.nivel === "neutro" ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.disabledTextColor
                    onClicked: { archivos.currentIndex = index; raiz.catalogo.fijarArchivo(modelData.rel) }
                    Accessible.name: modelData.rel + ": " + modelData.accion + (modelData.detalle ? ", " + modelData.detalle : "")
                    contentItem: RowLayout {
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.Icon {
                            source: ({ activo: "edit-link", conflicto: "dialog-warning-symbolic", pendiente: "list-add",
                                       local: "document-import", ausente: "help-hint" })[fila.modelData.estado] || "document-edit"
                            implicitWidth: Kirigami.Units.iconSizes.small
                            implicitHeight: implicitWidth
                            Layout.alignment: Qt.AlignTop
                            Layout.topMargin: 2
                            isMask: true
                            color: fila.colorNivel
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0
                            RowLayout {
                                QQC2.Label {
                                    text: fila.modelData.rel
                                    elide: Text.ElideMiddle
                                    Layout.fillWidth: true
                                    font.weight: fila.highlighted ? Font.DemiBold : Font.Normal
                                    color: Kirigami.Theme.textColor
                                }
                                EtiquetaNivel { visible: text !== ""; text: fila.modelData.hibrido ? "híbrido" : "" }
                            }
                            QQC2.Label {
                                text: fila.modelData.accion + (fila.modelData.detalle ? " · " + fila.modelData.detalle : "")
                                color: fila.colorNivel
                                font: Kirigami.Theme.smallFont
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }
            Kirigami.ListSectionHeader {
                visible: (raiz.pl.huerfanos || []).length > 0
                Layout.fillWidth: true
                text: "Huérfanos en el repo"
            }
            RowLayout {
                visible: (raiz.pl.huerfanos || []).length > 0
                Layout.fillWidth: true
                Layout.leftMargin: Kirigami.Units.largeSpacing
                Layout.rightMargin: Kirigami.Units.largeSpacing
                Layout.bottomMargin: Kirigami.Units.largeSpacing
                spacing: Kirigami.Units.smallSpacing
                EtiquetaNivel { text: "fuera de config.sh"; nivel: "neutro"; Layout.alignment: Qt.AlignTop }
                QQC2.Label {
                    Layout.fillWidth: true
                    wrapMode: Text.WrapAnywhere
                    font: Kirigami.Theme.fixedWidthFont
                    color: Kirigami.Theme.disabledTextColor
                    text: (raiz.pl.huerfanos || []).join("\n")
                }
            }
        }

        ColumnLayout {
            QQC2.SplitView.fillWidth: true
            spacing: 0
            // 2026-11-19: las tres vistas del archivo en un pozo (gui-comun 4.2), no una tira de pestañas a medio ancho
            SelectorSegmentado {
                id: pestanas
                Layout.margins: Kirigami.Units.smallSpacing
                Layout.leftMargin: Kirigami.Units.largeSpacing
                titulo: "Vista del archivo"
                readonly property int currentIndex: raiz.pestana
                opciones: [{ clave: "0", texto: "Comparación", icono: "view-split-left-right" },
                           { clave: "1", texto: "Simulación", icono: "utilities-terminal", contador: raiz.catalogo.salida.length ? raiz.catalogo.salida.length : undefined },
                           { clave: "2", texto: "Detalles", icono: "documentinfo" }]
                onElegida: clave => raiz.pestana = parseInt(clave)
                Binding on actual { value: String(raiz.pestana) }
            }
            Kirigami.Separator { Layout.fillWidth: true }
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
                    // la versión de un conflicto al adoptar (2026-11-03): main.sh --elecciones, sin terminal. 2026-11-19: una
                    // fila con la pregunta y la elección en un pozo (antes, un aviso naranja con tres botones)
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.leftMargin: Kirigami.Units.largeSpacing
                        Layout.rightMargin: Kirigami.Units.largeSpacing
                        Layout.bottomMargin: Kirigami.Units.smallSpacing
                        visible: raiz.catalogo.operacion === "adoptar" && raiz.catalogo.filaPlan.estado === "conflicto"
                        spacing: Kirigami.Units.largeSpacing
                        EtiquetaNivel { text: "distinto en los dos lados"; nivel: "neutro" }
                        QQC2.Label { text: "¿Qué versión se queda al adoptar?"; Layout.fillWidth: true; elide: Text.ElideRight }
                        SelectorSegmentado {
                            titulo: "Versión que se queda"
                            compacto: true
                            opciones: [{ clave: "l", texto: "La de HOME", icono: "go-home", descripcion: "La de HOME pasa al repo" },
                                       { clave: "r", texto: "La del repo", icono: "folder-git", descripcion: "Se conserva la del repo" },
                                       { clave: "s", texto: "Saltar", icono: "go-next-skip", descripcion: "Este archivo no se adopta" }]
                            onElegida: clave => raiz.catalogo.fijarEleccion(raiz.catalogo.archivo, clave)
                            Binding on actual { value: raiz.catalogo.elecciones[raiz.catalogo.archivo] || "" }
                        }
                    }
                    Repeater {
                        model: raiz.catalogo.comparacion.notas || []
                        delegate: RowLayout {
                            required property string modelData
                            Layout.fillWidth: true
                            Layout.leftMargin: Kirigami.Units.largeSpacing
                            Layout.rightMargin: Kirigami.Units.largeSpacing
                            Layout.bottomMargin: Kirigami.Units.smallSpacing
                            spacing: Kirigami.Units.smallSpacing
                            readonly property bool secreto: modelData.indexOf("secreto") >= 0
                            Kirigami.Icon {
                                source: parent.secreto ? "object-locked" : "documentinfo"
                                isMask: true
                                color: parent.secreto ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.disabledTextColor
                                implicitWidth: Kirigami.Units.iconSizes.small
                                implicitHeight: implicitWidth
                                Layout.alignment: Qt.AlignTop
                            }
                            QQC2.Label { text: parent.modelData; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        }
                    }
                    VistaComparacion {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        diferencia: Object.assign({}, raiz.catalogo.comparacion, { notas: [] })
                        mensajeVacio: "Elija un archivo a la izquierda para comparar el repo con HOME"
                    }
                }

                // Simulación: la salida de main.sh, sin rutas de la máquina (la misma terminal que la portada)
                TerminalSimulacion {
                    titulo: raiz.catalogo.salidaDe || "Simulación"
                    orden: raiz.catalogo.ordenSimular
                    lineas: raiz.catalogo.salida
                    nombreAccesible: "Salida de main.sh"
                    mensajeVacio: "Sin simular todavía"
                    explicacionVacia: "Simular (Ctrl+Mayús+Intro) corre la orden con --dry-run: main.sh dice qué haría sin tocar el disco."
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
