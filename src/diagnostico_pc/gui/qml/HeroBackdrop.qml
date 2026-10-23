import QtQuick

Item {
    id: fondo
    objectName: "heroBackdrop"
    property bool animar: false
    clip: true

    Canvas {
        id: manchaAlta
        property real derivaX: 0
        property real derivaY: 0
        property real respiracion: 0
        width: Math.max(330, fondo.width * 0.58)
        height: Math.max(200, fondo.height * 1.25)
        x: fondo.width * 0.57 + derivaX
        y: -height * 0.48 + derivaY
        scale: 1 + respiracion
        onPaint: {
            const ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            const brillo = ctx.createRadialGradient(width * 0.48, height * 0.52, 8,
                                                   width * 0.48, height * 0.52, width * 0.55)
            brillo.addColorStop(0, "rgba(124, 98, 255, 0.24)")
            brillo.addColorStop(0.62, "rgba(169, 155, 255, 0.15)")
            brillo.addColorStop(1, "rgba(169, 155, 255, 0)")
            ctx.fillStyle = brillo
            ctx.beginPath()
            ctx.moveTo(width * 0.05, height * 0.44)
            ctx.bezierCurveTo(width * 0.1, height * 0.08, width * 0.67, -height * 0.08, width * 0.91, height * 0.18)
            ctx.bezierCurveTo(width * 1.13, height * 0.47, width * 0.79, height * 0.89, width * 0.4, height * 0.91)
            ctx.bezierCurveTo(width * 0.03, height * 0.91, -width * 0.1, height * 0.66, width * 0.05, height * 0.44)
            ctx.closePath()
            ctx.fill()
        }
        SequentialAnimation on derivaX {
            loops: Animation.Infinite; running: fondo.animar
            NumberAnimation { from: 0; to: -22; duration: 7600; easing.type: Easing.InOutSine }
            NumberAnimation { from: -22; to: 0; duration: 7600; easing.type: Easing.InOutSine }
        }
        SequentialAnimation on derivaY {
            loops: Animation.Infinite; running: fondo.animar
            NumberAnimation { from: 0; to: 13; duration: 8300; easing.type: Easing.InOutSine }
            NumberAnimation { from: 13; to: 0; duration: 8300; easing.type: Easing.InOutSine }
        }
        SequentialAnimation on respiracion {
            loops: Animation.Infinite; running: fondo.animar
            NumberAnimation { from: 0; to: 0.035; duration: 7500; easing.type: Easing.InOutSine }
            NumberAnimation { from: 0.035; to: 0; duration: 7500; easing.type: Easing.InOutSine }
        }
    }

    Canvas {
        id: manchaBaja
        property real derivaX: 0
        property real derivaY: 0
        width: Math.max(300, fondo.width * 0.52)
        height: Math.max(200, fondo.height * 1.05)
        x: fondo.width * 0.34 + derivaX
        y: fondo.height * 0.38 + derivaY
        onPaint: {
            const ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            const luz = ctx.createRadialGradient(width * 0.5, height * 0.42, 4,
                                                width * 0.5, height * 0.42, width * 0.53)
            luz.addColorStop(0, "rgba(169, 155, 255, 0.19)")
            luz.addColorStop(0.72, "rgba(169, 155, 255, 0.10)")
            luz.addColorStop(1, "rgba(169, 155, 255, 0)")
            ctx.fillStyle = luz
            ctx.beginPath()
            ctx.moveTo(width * 0.04, height * 0.53)
            ctx.bezierCurveTo(width * 0.18, height * 0.09, width * 0.55, -height * 0.13, width * 0.84, height * 0.2)
            ctx.bezierCurveTo(width * 1.09, height * 0.49, width * 0.85, height * 0.96, width * 0.39, height * 0.91)
            ctx.bezierCurveTo(width * 0.05, height * 0.87, -width * 0.07, height * 0.68, width * 0.04, height * 0.53)
            ctx.closePath()
            ctx.fill()
        }
        SequentialAnimation on derivaX {
            loops: Animation.Infinite; running: fondo.animar
            NumberAnimation { from: 0; to: 18; duration: 6900; easing.type: Easing.InOutSine }
            NumberAnimation { from: 18; to: 0; duration: 6900; easing.type: Easing.InOutSine }
        }
        SequentialAnimation on derivaY {
            loops: Animation.Infinite; running: fondo.animar
            NumberAnimation { from: 0; to: -12; duration: 8500; easing.type: Easing.InOutSine }
            NumberAnimation { from: -12; to: 0; duration: 8500; easing.type: Easing.InOutSine }
        }
    }

    Canvas {
        anchors.fill: parent
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            const ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.strokeStyle = "rgba(169, 155, 255, 0.20)"
            ctx.lineWidth = 1.4
            ctx.beginPath()
            ctx.moveTo(width * 0.38, height * 1.03)
            ctx.bezierCurveTo(width * 0.52, height * 0.42, width * 0.75, height * 0.54, width * 0.94, -height * 0.08)
            ctx.stroke()
            ctx.beginPath()
            ctx.moveTo(width * 0.57, -height * 0.05)
            ctx.bezierCurveTo(width * 0.68, height * 0.34, width * 0.88, height * 0.16, width * 1.03, height * 0.51)
            ctx.stroke()
            ctx.fillStyle = "rgba(169, 155, 255, 0.28)"
            for (const punto of [[0.53, 0.74, 3], [0.72, 0.18, 4], [0.91, 0.7, 3]]) {
                ctx.beginPath()
                ctx.arc(width * punto[0], height * punto[1], punto[2], 0, Math.PI * 2)
                ctx.fill()
            }
        }
    }

    Repeater {
        model: [
            { nombre: "microchip", x: 0.52, y: 0.12, tamano: 31, dx: 11, dy: 7, tiempo: 14000 },
            { nombre: "wifi", x: 0.68, y: 0.35, tamano: 42, dx: -13, dy: 9, tiempo: 16000 },
            { nombre: "display", x: 0.77, y: 0.7, tamano: 49, dx: 15, dy: -8, tiempo: 17500 },
            { nombre: "gears", x: 0.47, y: 0.67, tamano: 34, dx: -10, dy: -6, tiempo: 15000 },
            { nombre: "laptop", x: 0.9, y: 0.18, tamano: 32, dx: 8, dy: 7, tiempo: 16500 }
        ]
        delegate: FaIcon {
            id: glifo
            required property var modelData
            property real derivaX: 0
            property real derivaY: 0
            nombre: modelData.nombre
            lavanda: true
            width: modelData.tamano
            height: width
            x: fondo.width * modelData.x + derivaX
            y: fondo.height * modelData.y + derivaY
            opacity: 0.10
            SequentialAnimation on derivaX {
                loops: Animation.Infinite; running: fondo.animar
                NumberAnimation { from: 0; to: glifo.modelData.dx; duration: glifo.modelData.tiempo / 2; easing.type: Easing.InOutSine }
                NumberAnimation { from: glifo.modelData.dx; to: 0; duration: glifo.modelData.tiempo / 2; easing.type: Easing.InOutSine }
            }
            SequentialAnimation on derivaY {
                loops: Animation.Infinite; running: fondo.animar
                NumberAnimation { from: 0; to: glifo.modelData.dy; duration: glifo.modelData.tiempo / 2; easing.type: Easing.InOutSine }
                NumberAnimation { from: glifo.modelData.dy; to: 0; duration: glifo.modelData.tiempo / 2; easing.type: Easing.InOutSine }
            }
        }
    }
}
