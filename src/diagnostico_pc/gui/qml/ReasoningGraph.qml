import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: raiz
    objectName: "pantallaRazonamiento"
    property var grafo: ({})
    property string seleccionado: ""
    property real zoom: 0.88
    property bool detallesMovil: false
    readonly property bool panelLateral: width >= 960
    readonly property var nodosResaltados: grafo.soportes && grafo.soportes[seleccionado]
                                           ? grafo.soportes[seleccionado] : []
    signal regresar()

    function nodoSeleccionado() {
        for (const nodo of grafo.nodos || [])
            if (nodo.id === seleccionado) return nodo
        return ({})
    }
    function cambiarZoom(factor) {
        zoom = Math.max(0.55, Math.min(1.8, Math.round((zoom + factor) * 100) / 100))
    }
    onSeleccionadoChanged: lienzo.requestPaint()
    onGrafoChanged: {
        const reglas = (grafo.nodos || []).filter(n => n.tipo === "regla")
        seleccionado = reglas.length ? reglas[0].id
                     : grafo.hipotesis && grafo.hipotesis.length ? grafo.hipotesis[0] : ""
        lienzo.requestPaint()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        RowLayout {
            Layout.fillWidth: true
            spacing: 16
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2
                Label {
                    Layout.fillWidth: true
                    text: "Árbol del <font color='#6355FF'>razonamiento</font>"
                    textFormat: Text.RichText
                    color: "#292544"
                    font.family: "Segoe UI"
                    font.pixelSize: raiz.width < 900 ? 24 : 29
                    font.bold: true
                    wrapMode: Text.WordWrap
                }
                Label {
                    Layout.fillWidth: true
                    text: "Hechos, reglas y conclusiones de la consulta · desplaza para explorar"
                    color: "#77718F"
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                }
            }
            Rectangle {
                visible: raiz.width >= 900
                Layout.preferredWidth: 200
                Layout.preferredHeight: 58
                radius: 12
                color: "#F5F2FF"
                border.color: "#E5DEFF"
                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 3
                    Label { text: "Consulta actual"; color: "#292544"; font.bold: true; font.pixelSize: 11 }
                    Label { text: "Categoría: " + (grafo.categoria || "—"); color: "#6F6B83"; font.pixelSize: 11 }
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            ActionButton {
                text: "Volver a resultados"
                icono: "arrow-left"
                secundario: true
                onClicked: raiz.regresar()
            }
            Item { Layout.fillWidth: true }
            Rectangle {
                visible: !raiz.panelLateral
                Layout.preferredWidth: 72; Layout.preferredHeight: 28
                radius: 8; color: "#F3F0FF"; border.color: "#E2DAFF"
                Label { anchors.centerIn: parent; text: raiz.detallesMovil ? "Ocultar" : "Detalle"; color: "#6355FF"; font.pixelSize: 11; font.bold: true }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: raiz.detallesMovil = !raiz.detallesMovil }
            }
            Label { text: "Zoom"; color: "#292544" }
            Rectangle {
                Layout.preferredWidth: 28; Layout.preferredHeight: 28
                radius: 8; color: "#F3F0FF"; border.color: "#E2DAFF"
                Label { anchors.centerIn: parent; text: "−"; color: "#6355FF"; font.bold: true }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: raiz.cambiarZoom(-0.15) }
            }
            Label { text: Math.round(raiz.zoom * 100) + "%"; color: "#6F6B83" }
            Rectangle {
                Layout.preferredWidth: 28; Layout.preferredHeight: 28
                radius: 8; color: "#F3F0FF"; border.color: "#E2DAFF"
                Label { anchors.centerIn: parent; text: "+"; color: "#6355FF"; font.bold: true }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: raiz.cambiarZoom(0.15) }
            }
            Rectangle {
                Layout.preferredWidth: 52; Layout.preferredHeight: 28
                radius: 8; color: "#F3F0FF"; border.color: "#E2DAFF"
                Label { anchors.centerIn: parent; text: "100 %"; color: "#6355FF"; font.pixelSize: 11; font.bold: true }
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: raiz.zoom = 1 }
            }
        }
        Label {
            Layout.fillWidth: true
            visible: !!grafo.explicacionSinConclusion
            text: grafo.explicacionSinConclusion || ""
            color: "#6F6B83"
            wrapMode: Text.WordWrap
        }
        Label {
            Layout.fillWidth: true
            visible: !!grafo.avisos && grafo.avisos.length > 0
            text: (grafo.avisos || []).join(" ")
            color: "#A73F4A"
            wrapMode: Text.WordWrap
        }
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14
            Flickable {
                id: desplazamiento
                objectName: "lienzoRazonamiento"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                contentWidth: Math.max(width, (grafo.ancho || 796) * raiz.zoom)
                contentHeight: (grafo.alto || 240) * raiz.zoom
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.horizontal: ScrollBar {
                    policy: ScrollBar.AlwaysOff; height: 7
                    background: Rectangle { radius: 4; color: "#F2EFFA" }
                    contentItem: Rectangle { radius: 4; color: "#C9C3E5" }
                }
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AlwaysOff; width: 7
                    background: Rectangle { radius: 4; color: "#F2EFFA" }
                    contentItem: Rectangle { radius: 4; color: "#C9C3E5" }
                }
                Rectangle { anchors.fill: parent; color: "#FDFBFF"; border.color: "#ECE9F5"; radius: 14 }
                Item {
                    x: Math.max(0, (desplazamiento.width - width * raiz.zoom) / 2)
                    width: grafo.ancho || 796
                    height: grafo.alto || 240
                    transform: Scale { xScale: raiz.zoom; yScale: raiz.zoom; origin.x: 0; origin.y: 0 }
                    Repeater {
                        model: grafo.secciones || []
                        delegate: Rectangle {
                            required property var modelData
                            x: modelData.x
                            y: modelData.y
                            width: modelData.ancho
                            height: modelData.alto
                            radius: 18
                            color: modelData.tipo === "observacion" ? "#EAF8F0"
                                 : modelData.tipo === "derivado" ? "#EAF4FF"
                                 : modelData.tipo === "regla" ? "#F4EFFF"
                                 : modelData.tipo === "alternativas" ? "#F6F6FB" : "#F4EFFF"
                            border.color: modelData.tipo === "observacion" ? "#B8E7CA"
                                        : modelData.tipo === "derivado" ? "#BDDFFF"
                                        : modelData.tipo === "regla" ? "#DDD0FF" : "#E1DAF5"
                        }
                    }
                    Canvas {
                        id: lienzo
                        anchors.fill: parent
                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            const mapa = {}
                            for (const n of grafo.nodos || []) mapa[n.id] = n
                            for (const a of grafo.conexiones || []) {
                                const origen = mapa[a.origen], destino = mapa[a.destino]
                                if (!origen || !destino) continue
                                const x1 = origen.x + origen.ancho / 2, y1 = origen.y + origen.alto - 4
                                const x2 = destino.x + destino.ancho / 2, y2 = destino.y
                                const activo = raiz.nodosResaltados.indexOf(a.origen) >= 0
                                             && raiz.nodosResaltados.indexOf(a.destino) >= 0
                                ctx.beginPath()
                                ctx.moveTo(x1, y1)
                                const curva = Math.max(28, Math.min(72, (y2 - y1) / 2))
                                ctx.bezierCurveTo(x1, y1 + curva, x2, y2 - curva, x2, y2)
                                ctx.strokeStyle = activo ? "#6355FF" : "#7885A6"
                                ctx.lineWidth = activo ? 2.5 : 1.4
                                ctx.globalAlpha = raiz.nodosResaltados.length && !activo ? 0.14
                                                : activo ? 0.8 : 0.48
                                ctx.stroke()
                                ctx.beginPath()
                                ctx.moveTo(x2 - 6, y2 - 9)
                                ctx.lineTo(x2, y2 - 1)
                                ctx.lineTo(x2 + 6, y2 - 9)
                                ctx.fillStyle = ctx.strokeStyle
                                ctx.fill()
                                ctx.globalAlpha = 1
                            }
                        }
                    }
                    Repeater {
                        model: grafo.secciones || []
                        delegate: Rectangle {
                            required property var modelData
                            x: modelData.x + 12
                            y: modelData.y + 8
                            width: modelData.ancho - 24
                            height: 34
                            color: modelData.tipo === "observacion" ? "#EAF8F0"
                                 : modelData.tipo === "derivado" ? "#EAF4FF"
                                 : modelData.tipo === "regla" ? "#F4EFFF"
                                 : modelData.tipo === "alternativas" ? "#F6F6FB" : "#F4EFFF"
                            Label {
                                anchors.fill: parent
                                anchors.leftMargin: 6
                                verticalAlignment: Text.AlignVCenter
                                text: modelData.titulo + "  ·  " + modelData.cantidad
                                color: modelData.tipo === "observacion" ? "#167947"
                                     : modelData.tipo === "derivado" ? "#1769C5" : "#5749C9"
                                font.family: "Segoe UI"
                                font.pixelSize: 16
                                font.bold: true
                                elide: Text.ElideRight
                            }
                        }
                    }
                    Repeater {
                        model: grafo.nodos || []
                        delegate: ReasoningNode {
                            required property var modelData
                            objectName: "nodoRazonamiento"
                            dato: modelData
                            seleccionado: raiz.seleccionado === modelData.id
                            atenuado: raiz.nodosResaltados.length > 0
                                      && raiz.nodosResaltados.indexOf(modelData.id) < 0
                            onElegido: identificador => {
                                raiz.seleccionado = identificador
                                if (!raiz.panelLateral) raiz.detallesMovil = true
                            }
                        }
                    }
                }
            }
            ReasoningDetails {
                visible: raiz.panelLateral
                Layout.preferredWidth: 292
                Layout.fillHeight: true
                nodo: raiz.nodoSeleccionado()
            }
        }
        ReasoningDetails {
            visible: !raiz.panelLateral && raiz.detallesMovil
            Layout.fillWidth: true
            Layout.preferredHeight: 180
            nodo: raiz.nodoSeleccionado()
        }
    }
}
