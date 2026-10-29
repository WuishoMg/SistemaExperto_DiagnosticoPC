import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: raiz
    property var dato: ({})
    property bool seleccionado: false
    property bool atenuado: false
    signal elegido(string identificador)

    x: dato.x || 0
    y: dato.y || 0
    width: dato.ancho || 224
    height: dato.alto || 162
    opacity: atenuado ? 0.42 : 1
    Behavior on opacity { NumberAnimation { duration: 150 } }

    readonly property color acento: dato.tipo === "observacion" ? "#21895B"
                                    : dato.tipo === "derivado" ? "#287AD9"
                                    : dato.tipo === "regla" ? "#6355FF"
                                    : dato.orden === 1 ? "#5D48EF" : "#77708E"

    Rectangle {
        anchors.fill: tarjeta
        anchors.topMargin: 5
        anchors.leftMargin: 2
        anchors.rightMargin: -2
        radius: 16
        color: "#221858"
        opacity: 0.07
    }
    Rectangle {
        id: tarjeta
        anchors.fill: parent
        anchors.bottomMargin: 4
        radius: 16
        color: raiz.dato.tipo === "observacion" ? "#FFFFFF"
             : raiz.dato.tipo === "derivado" ? "#F8FCFF"
             : raiz.dato.tipo === "regla" ? "#F9F6FF"
             : raiz.dato.orden === 1 ? "#F2EAFF" : "#FFFFFF"
        border.width: raiz.seleccionado || (raiz.dato.tipo === "hipotesis" && raiz.dato.orden === 1) ? 2 : 1
        border.color: raiz.seleccionado ? "#6355FF"
                    : raiz.dato.tipo === "observacion" ? "#AFE0C3"
                    : raiz.dato.tipo === "derivado" ? "#AED4FF"
                    : raiz.dato.tipo === "hipotesis" && raiz.dato.orden === 1 ? "#A996FF"
                    : raiz.dato.tipo === "hipotesis" ? "#E0DDEA" : "#D7C9FF"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 5
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                Rectangle {
                    Layout.preferredWidth: 26; Layout.preferredHeight: 26; radius: 9
                    color: raiz.dato.tipo === "observacion" ? "#E1F6E9"
                         : raiz.dato.tipo === "derivado" ? "#DDEEFF"
                         : raiz.dato.tipo === "regla" ? "#EAE3FF"
                         : raiz.dato.orden === 1 ? "#6355FF" : "#E8E6F0"
                    Label {
                        anchors.centerIn: parent
                        text: raiz.dato.tipo === "observacion"
                              ? raiz.dato.estado === "verdadero" ? "✓" : raiz.dato.estado === "falso" ? "×" : "?"
                              : raiz.dato.tipo === "derivado" ? "✦" : raiz.dato.tipo === "regla" ? "◆" : "✧"
                        color: raiz.dato.tipo === "hipotesis" && raiz.dato.orden === 1 ? "#FFFFFF" : raiz.acento
                        font.pixelSize: 17
                        font.bold: true
                    }
                }
                Label {
                    Layout.fillWidth: true
                    text: raiz.dato.tipo === "observacion" ? "OBSERVACIÓN"
                        : raiz.dato.tipo === "derivado" ? "HECHO DERIVADO"
                        : raiz.dato.tipo === "regla" ? "REGLA ACTIVADA"
                        : raiz.dato.orden === 1 ? "HIPÓTESIS PRINCIPAL" : "ALTERNATIVA " + (raiz.dato.orden - 1)
                    color: raiz.acento
                    font.family: "Segoe UI"
                    font.pixelSize: 10
                    font.bold: true
                    elide: Text.ElideRight
                }
            }
            Label {
                Layout.fillWidth: true
                text: raiz.dato.etiqueta || ""
                color: "#292544"
                font.family: "Segoe UI"
                font.pixelSize: raiz.dato.tipo === "hipotesis" ? 15 : 13
                font.bold: true
                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                maximumLineCount: raiz.dato.tipo === "hipotesis" ? 6 : 5
                elide: Text.ElideRight
            }
            Label {
                Layout.fillWidth: true
                visible: raiz.dato.tipo !== "observacion" && !!raiz.dato.resumen
                text: raiz.dato.resumen || ""
                color: "#615D75"
                font.pixelSize: 11
                wrapMode: Text.WordWrap
                maximumLineCount: 3
                elide: Text.ElideRight
            }
            Item { Layout.fillHeight: true }
            StatusTag {
                visible: raiz.dato.tipo === "observacion" || raiz.dato.tipo === "derivado"
                estado: raiz.dato.estado || "desconocido"
                texto: raiz.dato.estado || "desconocido"
            }
            Label {
                visible: raiz.dato.tipo === "hipotesis"
                text: raiz.dato.orden === 1 ? "Prioridad 1" : "Prioridad " + raiz.dato.orden
                color: raiz.dato.orden === 1 ? "#6355FF" : "#77708E"
                font.bold: true
                font.pixelSize: 11
            }
        }
    }
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: raiz.elegido(raiz.dato.id)
    }
}
