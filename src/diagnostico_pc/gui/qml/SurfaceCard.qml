import QtQuick

Item {
    id: root
    default property alias contenido: panel.data
    property color fondo: "#FFFFFF"
    property color borde: "#ECE9F5"
    implicitHeight: panel.implicitHeight
    Rectangle { anchors.fill: panel; anchors.topMargin: 6; anchors.leftMargin: 2; anchors.rightMargin: -2; radius: 18; color: "#170E4B"; opacity: 0.055 }
    Rectangle {
        id: panel
        anchors.fill: parent
        radius: 18; color: root.fondo; border.color: root.borde
    }
}
