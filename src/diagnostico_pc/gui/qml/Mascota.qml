import QtQuick
import QtQuick.Effects

Item {
    id: raiz
    property url recurso: ""
    property bool animarEntrada: false
    property bool flotar: false
    property bool sombraVioleta: false
    property int retrasoEntrada: 0
    property real desplazamiento: 0
    readonly property bool animado: recurso.toString().toLowerCase().endsWith(".gif") || recurso.toString().toLowerCase().endsWith(".webp")
    visible: recurso.toString().length > 0 && (animado ? animacion.status === Image.Ready : imagen.status === Image.Ready)
    implicitWidth: visible ? 130 : 0
    implicitHeight: visible ? 130 : 0
    layer.enabled: sombraVioleta && visible
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowColor: "#7054D6"
        shadowOpacity: 0.40
        shadowBlur: 0.72
        shadowVerticalOffset: 7
        shadowScale: 1.04
    }
    scale: 1
    transformOrigin: Item.Center
    SequentialAnimation on scale {
        running: raiz.visible && raiz.animarEntrada
        PauseAnimation { duration: raiz.retrasoEntrada }
        NumberAnimation { from: 0.88; to: 1; duration: 420; easing.type: Easing.OutCubic }
    }
    SequentialAnimation on desplazamiento {
        loops: Animation.Infinite
        running: raiz.visible && raiz.flotar
        NumberAnimation { from: 0; to: -5; duration: 1900; easing.type: Easing.InOutSine }
        NumberAnimation { from: -5; to: 0; duration: 1900; easing.type: Easing.InOutSine }
    }

    Item {
        width: parent.width
        height: parent.height
        y: raiz.desplazamiento
        AnimatedImage {
            id: animacion
            anchors.fill: parent
            source: raiz.animado ? raiz.recurso : ""
            visible: raiz.animado && status === Image.Ready
            fillMode: Image.PreserveAspectFit
            cache: false
        }
        Image {
            id: imagen
            anchors.fill: parent
            source: !raiz.animado ? raiz.recurso : ""
            visible: !raiz.animado && status === Image.Ready
            fillMode: Image.PreserveAspectFit
        }
    }
}
