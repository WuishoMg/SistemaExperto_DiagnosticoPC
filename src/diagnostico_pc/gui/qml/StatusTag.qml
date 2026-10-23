import QtQuick
import QtQuick.Controls

Rectangle {
    id: tag
    property string estado: "desconocido"
    property string texto: estado
    implicitWidth: etiqueta.implicitWidth + 20
    implicitHeight: 27
    radius: 13
    color: estado === "verdadero" ? "#E8F6F0" : estado === "falso" ? "#FFF0F0" : "#F0EDFF"
    Label {
        id: etiqueta
        anchors.centerIn: parent
        text: tag.texto
        color: tag.estado === "verdadero" ? "#147653" : tag.estado === "falso" ? "#A73F4A" : "#5D50B9"
        font.pixelSize: 12; font.bold: true
    }
}
