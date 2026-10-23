import QtQuick
import QtMultimedia

Item {
    id: audio
    objectName: "audioAplicacion"
    property string pantalla: ""
    property string faseVisual: ""
    property bool bienvenidaReproducida: false
    signal sonidoSolicitado(string nombre)

    MediaPlayer {
        id: bienvenida
        objectName: "audioBienvenida"
        source: Qt.resolvedUrl("../assets/sounds/bienvenida.mp3")
        audioOutput: AudioOutput { objectName: "salidaBienvenida"; volume: 0.15 }
        loops: 1
    }
    MediaPlayer {
        id: analizando
        objectName: "audioAnalizando"
        source: Qt.resolvedUrl("../assets/sounds/analizando.mp3")
        audioOutput: AudioOutput { objectName: "salidaAnalizando"; volume: 0.15 }
        loops: 1
    }
    MediaPlayer {
        id: idea
        objectName: "audioIdea"
        source: Qt.resolvedUrl("../assets/sounds/idea-sound.mp3")
        audioOutput: AudioOutput { objectName: "salidaIdea"; volume: 0.18 }
        loops: 1
    }
    SoundEffect {
        id: boton
        objectName: "audioBoton"
        source: Qt.resolvedUrl("../assets/sounds/button-pop.wav")
        volume: 0.15
        loops: 1
    }

    function reproducirBienvenida() {
        if (bienvenidaReproducida || pantalla !== "bienvenida")
            return
        bienvenidaReproducida = true
        sonidoSolicitado("bienvenida")
        bienvenida.play()
    }

    function reproducirBoton() {
        sonidoSolicitado("boton")
        boton.stop()
        boton.play()
    }

    onPantallaChanged: {
        if (pantalla !== "bienvenida")
            bienvenida.stop()
        if (pantalla !== "preguntas" && pantalla !== "analisis") {
            analizando.stop()
            if (pantalla !== "resultados")
                idea.stop()
        }
    }

    onFaseVisualChanged: {
        if (faseVisual === "analizando") {
            bienvenida.stop()
            idea.stop()
            sonidoSolicitado("analizando")
            analizando.play()
        } else if (faseVisual === "idea") {
            analizando.stop()
            sonidoSolicitado("idea")
            idea.play()
        } else {
            analizando.stop()
            if (pantalla !== "resultados")
                idea.stop()
        }
    }
}
