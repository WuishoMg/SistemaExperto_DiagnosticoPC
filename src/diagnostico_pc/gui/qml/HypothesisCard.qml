import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SurfaceCard {
    id: raiz
    property var hipotesis: ({})
    property bool principal: false
    fondo: principal ? "#F5F2FF" : "#FFFFFF"
    borde: principal ? "#DDD6FF" : "#ECE9F5"
    implicitHeight: cuerpo.implicitHeight + 36
    ColumnLayout {
        id: cuerpo
        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 18
        spacing: 10
        RowLayout {
            Layout.fillWidth: true
            FaIcon { nombre: raiz.principal ? "lightbulb" : "magnifying-glass"; Layout.preferredWidth: 18; Layout.preferredHeight: 18 }
            Label { text: raiz.principal ? "HIPÓTESIS PRINCIPAL" : "HIPÓTESIS ALTERNATIVA"; color: "#6355FF"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 1 }
            Item { Layout.fillWidth: true }
            StatusTag { estado: "desconocido"; texto: "Para revisar" }
        }
        Label { text: raiz.hipotesis.nombre || ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#292544"; font.pixelSize: raiz.principal ? 22 : 19; font.bold: true }
        Label { text: raiz.hipotesis.descripcion || ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#6F6B83" }
        Label { text: "ACCIONES RECOMENDADAS"; color: "#6355FF"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 1; visible: (raiz.hipotesis.recomendaciones || []).length > 0 }
        Repeater {
            model: raiz.hipotesis.recomendaciones || []
            delegate: RowLayout {
                required property string modelData
                Layout.fillWidth: true; spacing: 10
                FaIcon { nombre: "circle-check"; Layout.preferredWidth: 14; Layout.preferredHeight: 14; Layout.alignment: Qt.AlignTop }
                Label { text: modelData; color: "#292544"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
        }
    }
}
