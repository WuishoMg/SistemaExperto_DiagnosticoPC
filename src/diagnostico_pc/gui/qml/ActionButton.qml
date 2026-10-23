import QtQuick
import QtQuick.Controls
import QtQuick.Window

AbstractButton {
    id: control
    property string icono: ""
    property bool secundario: false

    hoverEnabled: true
    focusPolicy: Qt.StrongFocus
    implicitWidth: contentItem.implicitWidth + leftPadding + rightPadding
    implicitHeight: 42
    leftPadding: 18
    rightPadding: 18
    topPadding: 10
    bottomPadding: 10
    font.family: "Segoe UI"
    font.pixelSize: 15
    font.bold: true
    scale: !enabled ? 1 : down ? 0.97 : hovered ? 1.03 : 1
    transformOrigin: Item.Center
    Behavior on scale { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

    Accessible.role: Accessible.Button
    Accessible.name: text
    Keys.onReturnPressed: (event) => { control.click(); event.accepted = true }
    Keys.onEnterPressed: (event) => { control.click(); event.accepted = true }
    onClicked: {
        const ventana = control.Window.window
        if (ventana && typeof ventana.reproducirSonidoBoton === "function")
            ventana.reproducirSonidoBoton()
    }

    background: Item {
        Rectangle {
            anchors.fill: face
            anchors.topMargin: 4
            anchors.bottomMargin: -4
            radius: face.radius
            color: "#352A80"
            opacity: control.enabled && control.hovered ? 0.14 : 0.06
            Behavior on opacity { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
        }
        Rectangle {
            id: face
            anchors.fill: parent
            radius: 11
            color: !control.enabled ? "#E8E4F1"
                : control.secundario ? (control.hovered ? "#EDEAFF" : "#F5F3FF")
                : control.down ? "#4E40DE" : control.hovered ? "#766AFF" : "#6355FF"
            border.color: control.secundario ? "#DDD8FA" : "transparent"
            Behavior on color { ColorAnimation { duration: 180; easing.type: Easing.OutCubic } }
        }
        Rectangle {
            anchors.fill: face
            anchors.margins: -3
            radius: face.radius + 3
            color: "transparent"
            border.width: 2
            border.color: "#6355FF"
            visible: control.visualFocus
        }
    }

    contentItem: Item {
        implicitWidth: contenido.implicitWidth
        implicitHeight: Math.max(20, contenido.implicitHeight)
        Row {
            id: contenido
            anchors.centerIn: parent
            spacing: control.icono.length > 0 ? 10 : 0
            Item {
                visible: control.icono.length > 0
                width: visible ? 17 : 0
                height: etiqueta.implicitHeight
                FaIcon {
                    anchors.centerIn: parent
                    nombre: control.icono
                    blanco: control.enabled && !control.secundario
                    width: 17
                    height: 17
                    opacity: control.enabled ? 1 : 0.7
                }
            }
            Text {
                id: etiqueta
                text: control.text
                color: !control.enabled ? "#514B68" : control.secundario ? "#5145C9" : "#FFFFFF"
                font: control.font
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}
