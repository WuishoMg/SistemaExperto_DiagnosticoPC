import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: hero
    objectName: "heroCard"
    property string icono: "microchip"
    property string etiqueta: "DIAGNÓSTICO GUIADO"
    property string titulo: ""
    property string tituloFormateado: ""
    property string descripcion: ""
    property url mascotaRecurso: ""
    property bool mascotaFlotar: false
    property bool activo: false
    readonly property bool movimientoReducido: Qt.styleHints && Qt.styleHints.reducedMotion === true
    readonly property bool conMascota: mascotaRecurso.toString().length > 0
    readonly property real anchoMascota: width < 700 ? 220 : 280
    implicitHeight: cuerpo.height + 14
    opacity: 1
    scale: 1
    transformOrigin: Item.Center
    NumberAnimation on scale {
        from: 0.97; to: 1; duration: 390
        easing.type: Easing.OutCubic
        running: hero.activo && !hero.movimientoReducido
    }
    NumberAnimation on opacity {
        from: 0; to: 1; duration: 390
        easing.type: Easing.OutCubic
        running: hero.activo && !hero.movimientoReducido
    }

    Rectangle {
        anchors.fill: cuerpo
        anchors.topMargin: 8; anchors.leftMargin: 2; anchors.rightMargin: -2
        radius: 27; color: "#342073"; opacity: 0.085
    }
    Rectangle {
        id: cuerpo
        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
        height: Math.max(contenido.implicitHeight + 62, hero.conMascota ? (hero.width < 700 ? 218 : 250) : 180)
        radius: 27; border.color: "#E5DFFF"; border.width: 1
        gradient: Gradient {
            GradientStop { position: 0; color: "#FFFFFF" }
            GradientStop { position: 0.7; color: "#FBFAFF" }
            GradientStop { position: 1; color: "#F5F3FF" }
        }
        HeroBackdrop {
            anchors.fill: parent
            anchors.margins: 10
            animar: hero.activo && !hero.movimientoReducido
        }
        Rectangle {
            x: 24; y: 30; width: 43; height: 43; radius: 14
            color: "#FFFFFF"; border.color: "#EFEBFF"
            FaIcon { anchors.centerIn: parent; width: 21; height: 21; nombre: hero.icono }
        }
        Column {
            id: contenido
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 80
            anchors.rightMargin: hero.conMascota ? hero.anchoMascota + 22 : 34
            spacing: 10
            Label {
                text: hero.etiqueta
                font.pixelSize: 11; font.bold: true; font.letterSpacing: 1.4
                color: "#6355FF"
            }
            Text {
                width: parent.width
                text: hero.tituloFormateado || hero.titulo
                textFormat: Text.RichText
                wrapMode: Text.WordWrap
                font.family: "Segoe UI"
                font.pixelSize: hero.width < 700 ? 25 : 29
                font.bold: true
                color: "#242044"
            }
            Label {
                width: parent.width
                text: hero.descripcion
                wrapMode: Text.WordWrap
                font.pixelSize: 14
                color: "#6F6B83"
            }
        }
    }
    Mascota {
        id: mascotaHero
        objectName: "mascotaHero"
        recurso: hero.mascotaRecurso
        animarEntrada: hero.activo && !hero.movimientoReducido
        retrasoEntrada: 90
        flotar: hero.activo && hero.mascotaFlotar && !hero.movimientoReducido
        sombraVioleta: true
        width: hero.anchoMascota
        height: width
        x: hero.width - width - 7
        y: hero.width < 700 ? -28 : -36
    }
}
