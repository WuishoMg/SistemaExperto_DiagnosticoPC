import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SurfaceCard {
    id: raiz
    property var traza: ({})
    property bool abierto: false
    implicitHeight: contenido.implicitHeight + 28
    ColumnLayout {
        id: contenido
        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14
        spacing: 10
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            FaIcon { nombre: "sitemap"; Layout.preferredWidth: 17; Layout.preferredHeight: 17 }
            Label { text: "Nivel " + raiz.traza.nivel + " · " + raiz.traza.reglaId; color: "#292544"; font.bold: true; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            FaIcon { nombre: "chevron-down"; Layout.preferredWidth: 13; Layout.preferredHeight: 13; rotation: raiz.abierto ? 180 : 0; Behavior on rotation { NumberAnimation { duration: 160 } } }
        }
        Label { visible: raiz.abierto; text: raiz.traza.explicacion || ""; color: "#6F6B83"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        Repeater {
            model: raiz.abierto ? (raiz.traza.condiciones || []) : []
            delegate: RowLayout {
                required property var modelData
                Layout.fillWidth: true
                Label { text: modelData.nombre + " (" + modelData.hechoId + ")"; color: "#6F6B83"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                StatusTag { estado: modelData.estado }
            }
        }
        RowLayout {
            visible: raiz.abierto; Layout.fillWidth: true
            Label { text: "Conclusión: " + raiz.traza.conclusionId; color: "#292544"; font.bold: true; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            StatusTag { estado: raiz.traza.conclusionEstado || "desconocido"; visible: !!raiz.traza.conclusionEstado }
        }
    }
    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: raiz.abierto = !raiz.abierto }
}
