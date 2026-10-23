import QtQuick

Item {
    id: fondo
    clip: true
    property real desplazamiento: 0
    property bool animando: true
    readonly property int paso: 360
    NumberAnimation on desplazamiento {
        from: 0; to: fondo.paso; duration: 46000
        loops: Animation.Infinite
        running: fondo.visible && fondo.animando
    }
    Repeater {
        model: (Math.ceil(fondo.width / fondo.paso) + 2) * (Math.ceil(fondo.height / fondo.paso) + 2)
        delegate: Item {
            readonly property int columnas: Math.ceil(fondo.width / fondo.paso) + 2
            x: (index % columnas - 1) * fondo.paso + fondo.desplazamiento
            y: (Math.floor(index / columnas) - 1) * fondo.paso + fondo.desplazamiento
            width: fondo.paso; height: fondo.paso
            opacity: 0.10
            FaIcon { nombre: "microchip"; x: 34; y: 40; width: 49; height: 49 }
            FaIcon { nombre: "wifi"; x: 234; y: 78; width: 40; height: 40 }
            FaIcon { nombre: "display"; x: 144; y: 237; width: 54; height: 54 }
            FaIcon { nombre: "gears"; x: 303; y: 300; width: 36; height: 36 }
        }
    }
}
