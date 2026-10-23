import QtQuick

Image {
    property string nombre: ""
    property bool blanco: false
    property bool lavanda: false
    source: nombre ? "../assets/icons/" + (blanco ? "white/" : lavanda ? "lavender/" : "") + nombre + ".svg" : ""
    sourceSize.width: width * Screen.devicePixelRatio
    sourceSize.height: height * Screen.devicePixelRatio
    fillMode: Image.PreserveAspectFit
    smooth: true
    asynchronous: true
}
