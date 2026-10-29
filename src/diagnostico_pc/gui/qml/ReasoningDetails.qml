import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SurfaceCard {
    id: raiz
    objectName: "detalleRazonamiento"
    property var nodo: ({})
    fondo: "#FFFFFF"
    borde: "#E4DEF3"

    Flickable {
        id: desplazamiento
        anchors.fill: parent
        anchors.margins: 2
        clip: true
        contentWidth: width
        contentHeight: contenido.implicitHeight + 32
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AlwaysOff; width: 7
            background: Rectangle { radius: 4; color: "#F2EFFA" }
            contentItem: Rectangle { radius: 4; color: "#C9C3E5" }
        }
        ColumnLayout {
            id: contenido
            x: 14
            y: 14
            width: Math.max(0, desplazamiento.width - 28)
            spacing: 9
            Label {
                Layout.fillWidth: true
                text: Object.keys(raiz.nodo).length ? "Detalle del nodo" : "Selecciona un nodo"
                color: "#292544"
                font.family: "Segoe UI"
                font.pixelSize: 18
                font.bold: true
                wrapMode: Text.WordWrap
            }
            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: "#EBE7F4" }
            Label {
                Layout.fillWidth: true
                visible: !!raiz.nodo.id
                text: raiz.nodo.etiqueta || ""
                color: "#6355FF"
                font.pixelSize: 15
                font.bold: true
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "regla"
                text: raiz.nodo.referencia || ""
                color: "#6F6B83"
                wrapMode: Text.WordWrap
            }
            StatusTag {
                visible: raiz.nodo.tipo === "observacion"
                estado: raiz.nodo.estado || "desconocido"
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "observacion" && !!raiz.nodo.descripcion
                text: "Descripción"
                color: "#292544"
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "observacion" && !!raiz.nodo.descripcion
                text: raiz.nodo.descripcion || ""
                color: "#615D75"
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: !!raiz.nodo.detalle && raiz.nodo.tipo !== "observacion"
                text: raiz.nodo.tipo === "regla" ? "Descripción"
                    : raiz.nodo.tipo === "derivado" ? "Explicación" : "Explicación"
                color: "#292544"
                font.bold: true
            }
            Rectangle {
                Layout.fillWidth: true
                visible: !!raiz.nodo.detalle && raiz.nodo.tipo !== "observacion"
                implicitHeight: descripcion.implicitHeight + 20
                radius: 10
                color: "#F7F5FC"
                Label {
                    id: descripcion
                    anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                    anchors.margins: 10
                    text: raiz.nodo.tipo === "observacion" ? "" : (raiz.nodo.detalle || "")
                    color: "#3D3859"
                    wrapMode: Text.WordWrap
                }
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "observacion" && !!raiz.nodo.pregunta
                text: "Pregunta asociada"
                color: "#292544"
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "observacion" && !!raiz.nodo.pregunta
                text: raiz.nodo.pregunta || ""
                color: "#615D75"
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "regla"
                text: "Condiciones verificadas"
                color: "#292544"
                font.bold: true
            }
            Repeater {
                model: raiz.nodo.tipo === "regla" ? (raiz.nodo.condiciones || []) : []
                delegate: Rectangle {
                    required property var modelData
                    Layout.fillWidth: true
                    implicitHeight: condicionTexto.implicitHeight + 18
                    radius: 10
                    color: "#FAF9FE"
                    border.color: "#EAE5F5"
                    Label {
                        id: condicionTexto
                        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                        anchors.margins: 9
                        text: modelData.nombre + " (" + modelData.hechoId + ") = " + modelData.estado
                        color: "#504A69"
                        wrapMode: Text.WordWrap
                    }
                }
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "regla"
                text: "Conclusión"
                color: "#292544"
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "regla"
                text: raiz.nodo.conclusion
                      ? (raiz.nodo.conclusion.tipo === "hecho" ? "Genera el hecho derivado: " : "Sustenta la hipótesis: ")
                        + raiz.nodo.conclusion.nombre + " (" + raiz.nodo.conclusion.id + ")"
                        + (raiz.nodo.conclusion.estado ? " = " + raiz.nodo.conclusion.estado : "") : ""
                color: "#615D75"
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "derivado"
                text: "Reglas que lo generaron"
                color: "#292544"
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "derivado"
                text: (raiz.nodo.generadoras || []).length
                      ? raiz.nodo.generadoras.join(", ") : "No consta una regla productora en la traza disponible."
                color: "#615D75"
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "hipotesis" && !!raiz.nodo.criterio && !!raiz.nodo.criterio.diagnosticoId
                text: "Criterios ordinales"
                color: "#292544"
                font.bold: true
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "hipotesis" && !!raiz.nodo.criterio && !!raiz.nodo.criterio.diagnosticoId
                text: raiz.nodo.criterio ? raiz.nodo.criterio.calidadTexto
                      + " · " + raiz.nodo.criterio.especificidad + " observaciones originales · "
                      + raiz.nodo.criterio.prioridadTexto : ""
                color: "#615D75"
                wrapMode: Text.WordWrap
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.nodo.tipo === "hipotesis"
                text: "Soportes registrados"
                color: "#292544"
                font.bold: true
            }
            Repeater {
                model: raiz.nodo.tipo === "hipotesis" && raiz.nodo.soportesDetalle ? [
                    {titulo: "Observaciones", valores: raiz.nodo.soportesDetalle.observacion || []},
                    {titulo: "Reglas", valores: raiz.nodo.soportesDetalle.regla || []},
                    {titulo: "Hechos derivados", valores: raiz.nodo.soportesDetalle.derivado || []}
                ] : []
                delegate: ColumnLayout {
                    required property var modelData
                    Layout.fillWidth: true
                    spacing: 3
                    Label {
                        Layout.fillWidth: true
                        text: modelData.titulo + " · " + modelData.valores.length
                        color: "#6355FF"
                        font.bold: true
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }
                    Repeater {
                        model: modelData.valores
                        delegate: Label {
                            required property string modelData
                            Layout.fillWidth: true
                            text: "• " + modelData
                            color: "#615D75"
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }
}
