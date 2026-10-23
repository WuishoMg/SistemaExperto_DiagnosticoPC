import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: ventana
    width: 1080
    height: 760
    minimumWidth: 760
    minimumHeight: 600
    visible: true
    title: "Diagnóstico de PC"
    color: "#FBFAFF"
    property color violeta: "#6355FF"
    property color tinta: "#292544"
    property color tenue: "#6F6B83"
    property string categoriaPendiente: ""
    property bool secuenciaActiva: false
    property string faseVisual: ""
    readonly property bool movimientoReducido: Qt.styleHints && Qt.styleHints.reducedMotion === true

    function reproducirSonidoBoton() {
        audio.reproducirBoton()
    }

    AppAudio {
        id: audio
        pantalla: diagnostico.pantalla
        faseVisual: ventana.faseVisual
    }

    function cancelarSecuencia() {
        temporizadorAnalisis.stop()
        temporizadorIdea.stop()
        secuenciaActiva = false
        faseVisual = ""
    }

    function iniciarSecuenciaResultado() {
        if (secuenciaActiva)
            return
        if (diagnostico.contradicciones.length > 0 || diagnostico.terminal === "@bloqueo_energia") {
            diagnostico.verResultado()
            return
        }
        faseVisual = "analizando"
        secuenciaActiva = true
        temporizadorAnalisis.start()
    }

    Timer {
        id: temporizadorAnalisis
        interval: 2500
        onTriggered: {
            if (ventana.secuenciaActiva) {
                ventana.faseVisual = "idea"
                temporizadorIdea.start()
            }
        }
    }
    Timer {
        id: temporizadorIdea
        interval: 800
        onTriggered: {
            if (ventana.secuenciaActiva) {
                diagnostico.verResultado()
                if (diagnostico.pantalla === "preguntas" && diagnostico.error.length > 0)
                    ventana.cancelarSecuencia()
            }
        }
    }
    Connections {
        target: diagnostico
        function onEstadoCambiado() {
            if (ventana.secuenciaActiva
                    && diagnostico.pantalla !== "preguntas"
                    && diagnostico.pantalla !== "analisis")
                ventana.cancelarSecuencia()
        }
    }

    function iconoCategoria(id) {
        return ({alimentacion:"power-off", lentitud:"gauge-high", video:"display",
                 sistema:"gears", temperatura:"temperature-half", conectividad:"wifi",
                 general:"circle-question"})[id] || "laptop"
    }

    function elegir(id) {
        if (diagnostico.historial.length > 0) {
            categoriaPendiente = id
            confirmarCambio.open()
        } else {
            diagnostico.elegirCategoria(id)
        }
    }

    Dialog {
        id: confirmarCambio
        title: "Iniciar otra consulta"
        modal: true
        anchors.centerIn: parent
        standardButtons: Dialog.Yes | Dialog.No
        contentItem: Label {
            text: "Se descartarán las respuestas actuales. ¿Continuar?"
            wrapMode: Text.WordWrap
            padding: 16
        }
        onAccepted: {
            ventana.reproducirSonidoBoton()
            diagnostico.iniciarNuevaConsulta(categoriaPendiente)
        }
        onRejected: ventana.reproducirSonidoBoton()
    }

    FileDialog {
        id: guardarPdf
        title: "Guardar informe PDF"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PDF (*.pdf)"]
        defaultSuffix: "pdf"
        onAccepted: diagnostico.exportarPdf(selectedFile.toString())
    }

    WelcomeBackground {
        anchors.fill: parent
        visible: diagnostico.pantalla === "bienvenida"
        animando: visible && !ventana.movimientoReducido
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: ventana.width < 900 ? 20 : 30
        spacing: 0

        RowLayout {
            objectName: "encabezadoPrincipal"
            visible: diagnostico.pantalla !== "bienvenida"
            Layout.fillWidth: true
            Layout.bottomMargin: 18
            spacing: 12
            Rectangle {
                width: 34; height: 34; radius: 10; color: "#EEEAFE"
                FaIcon { anchors.centerIn: parent; nombre: "microchip"; width: 19; height: 19 }
            }
            Label {
                text: "PC / DIAGNÓSTICO"
                color: violeta
                font.pixelSize: 15
                font.bold: true
                font.family: "Segoe UI"
            }
            Item { Layout.fillWidth: true }
            ActionButton {
                text: "Categorías"
                icono: "list-check"
                secundario: true
                visible: diagnostico.pantalla !== "bienvenida" && diagnostico.pantalla !== "seleccion"
                onClicked: {
                    ventana.cancelarSecuencia()
                    diagnostico.irASeleccion()
                }
            }
        }

        Rectangle {
            objectName: "divisorEncabezado"
            visible: diagnostico.pantalla !== "bienvenida"
            Layout.fillWidth: true
            height: 1
            color: "#EAE7F5"
        }

        Rectangle {
            Layout.fillWidth: true
            visible: diagnostico.error.length > 0
            Layout.topMargin: 12
            Layout.bottomMargin: 12
            implicitHeight: errorTexto.implicitHeight + 24
            radius: 12
            color: "#FFF1F1"
            Label {
                id: errorTexto
                anchors.fill: parent
                anchors.margins: 12
                text: diagnostico.error
                color: "#8C2741"
                wrapMode: Text.WordWrap
            }
        }

        ScrollView {
            id: areaDesplazamiento
            objectName: "areaDesplazamiento"
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                x: areaDesplazamiento.width - width
                width: 7
                background: Rectangle { color: "transparent" }
                contentItem: Rectangle { radius: 4; color: "#C9C3E5" }
            }

            Item {
                width: Math.min(parent.width, 1080)
                x: Math.max(0, (parent.width - width) / 2)
                implicitHeight: contenido.implicitHeight + 28

                ColumnLayout {
                    id: contenido
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 14
                    spacing: 22

                    Item {
                        id: bienvenida
                        objectName: "bienvenida"
                        visible: diagnostico.pantalla === "bienvenida"
                        Layout.fillWidth: true
                        Layout.topMargin: Math.min(105, Math.max(70, ventana.height * 0.12))
                        implicitHeight: tarjetaBienvenida.height + 54
                        property real progreso: 0
                        property real entradaY: 20
                        opacity: 1
                        scale: 1
                        transformOrigin: Item.Center
                        NumberAnimation on opacity { from: 0; to: 1; duration: 390; easing.type: Easing.OutCubic; running: bienvenida.visible && !ventana.movimientoReducido }
                        NumberAnimation on scale { from: 0.97; to: 1; duration: 390; easing.type: Easing.OutCubic; running: bienvenida.visible && !ventana.movimientoReducido }
                        NumberAnimation on entradaY { from: 16; to: 0; duration: 390; easing.type: Easing.OutCubic; running: bienvenida.visible && !ventana.movimientoReducido }
                        NumberAnimation on progreso { from: 0; to: 1; duration: 1750; easing.type: Easing.OutCubic; running: bienvenida.visible }
                        Rectangle {
                            anchors.fill: tarjetaBienvenida
                            anchors.topMargin: 10; anchors.leftMargin: 3; anchors.rightMargin: -3
                            radius: 29; color: "#342073"; opacity: 0.09
                        }
                        Rectangle {
                            id: tarjetaBienvenida
                            objectName: "tarjetaBienvenida"
                            y: 30 + bienvenida.entradaY
                            width: Math.min(parent.width, 980)
                            anchors.horizontalCenter: parent.horizontalCenter
                            height: Math.max(270, contenidoBienvenida.implicitHeight + 58)
                            radius: 29; border.color: "#E5DFFF"
                            gradient: Gradient {
                                GradientStop { position: 0; color: "#FFFFFF" }
                                GradientStop { position: 0.72; color: "#FBFAFF" }
                                GradientStop { position: 1; color: "#F5F3FF" }
                            }
                            HeroBackdrop {
                                anchors.fill: parent; anchors.margins: 10
                                animar: bienvenida.visible && !ventana.movimientoReducido
                            }
                            Column {
                                id: contenidoBienvenida
                                anchors.left: parent.left
                                anchors.leftMargin: tarjetaBienvenida.width < 700 ? 27 : 42
                                anchors.verticalCenter: parent.verticalCenter
                                width: tarjetaBienvenida.width - mascotaBienvenida.width - (tarjetaBienvenida.width < 700 ? 42 : 75)
                                spacing: tarjetaBienvenida.width < 700 ? 10 : 13
                                Label {
                                    text: "UNA REVISIÓN PASO A PASO"
                                    color: violeta; font.pixelSize: 12; font.bold: true; font.letterSpacing: 1.6
                                }
                                Text {
                                    width: parent.width
                                    text: "Comprende lo que ocurre con <font color='#6355FF'>tu computadora</font>"
                                    textFormat: Text.RichText
                                    font.family: "Segoe UI"
                                    font.pixelSize: tarjetaBienvenida.width < 700 ? 27 : 35
                                    font.bold: true
                                    color: "#242044"
                                    wrapMode: Text.WordWrap
                                }
                                Label {
                                    width: parent.width
                                    text: "Responde unas preguntas y revisa las hipótesis y sus razones para orientar una revisión técnica."
                                    color: tenue
                                    font.pixelSize: tarjetaBienvenida.width < 700 ? 14 : 16
                                    wrapMode: Text.WordWrap
                                }
                                Rectangle {
                                    width: 150; height: 5; radius: 3; color: "#E1DCF6"
                                    Rectangle { width: parent.width * bienvenida.progreso; height: parent.height; radius: 3; color: violeta }
                                }
                                ActionButton { text: "Empezar diagnóstico"; icono: "arrow-right"; onClicked: diagnostico.irASeleccion() }
                            }
                        }
                        Mascota {
                            id: mascotaBienvenida
                            objectName: "mascotaBienvenida"
                            recurso: diagnostico.pantalla === "bienvenida" ? diagnostico.recursoMascota : ""
                            width: tarjetaBienvenida.width < 700 ? 215 : 290
                            height: width
                            x: tarjetaBienvenida.x + tarjetaBienvenida.width - width - (tarjetaBienvenida.width < 700 ? 5 : 15)
                            y: tarjetaBienvenida.y - (tarjetaBienvenida.width < 700 ? 22 : 34)
                            animarEntrada: bienvenida.visible && !ventana.movimientoReducido
                            retrasoEntrada: 90
                            flotar: bienvenida.visible && !ventana.movimientoReducido
                            sombraVioleta: true
                            onVisibleChanged: {
                                if (visible && diagnostico.pantalla === "bienvenida")
                                    audio.reproducirBienvenida()
                            }
                            Component.onCompleted: {
                                if (visible)
                                    audio.reproducirBienvenida()
                                else if (recurso.toString().length === 0)
                                    audio.reproducirBienvenida()
                            }
                        }
                    }

                    ColumnLayout {
                        visible: diagnostico.pantalla === "seleccion"
                        opacity: visible ? 1 : 0
                        Behavior on opacity { NumberAnimation { duration: 230 } }
                        Layout.fillWidth: true
                        spacing: 18
                        HeroCard {
                            Layout.fillWidth: true
                            Layout.topMargin: 18
                            icono: "list-check"; etiqueta: "SIETE RUTAS"
                            titulo: "¿Qué problema presenta tu computadora?"
                            tituloFormateado: "¿Qué problema presenta <font color='#6355FF'>tu computadora</font>?"
                            descripcion: "Elige la situación que mejor describe lo que observas."
                            mascotaRecurso: diagnostico.pantalla === "seleccion" ? diagnostico.recursoMascota : ""
                            activo: diagnostico.pantalla === "seleccion"
                        }
                        GridLayout {
                            Layout.fillWidth: true
                            columns: ventana.width < 900 ? 1 : 2
                            columnSpacing: 18
                            rowSpacing: 18
                            Repeater {
                                model: diagnostico.categorias
                                delegate: Item {
                                    required property var modelData
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 110
                                    Rectangle { anchors.fill: tarjeta; anchors.topMargin: 6; anchors.leftMargin: 2; anchors.rightMargin: -2; radius: 18; color: "#19104E"; opacity: 0.06 }
                                    Rectangle {
                                        id: tarjeta; anchors.fill: parent; radius: 18
                                        color: area.containsMouse ? "#F1EDFF" : "#FFFFFF"
                                        border.color: area.containsMouse ? "#CFC7FF" : "#EAE6F5"
                                        Behavior on color { ColorAnimation { duration: 150 } }
                                        RowLayout {
                                            anchors.fill: parent; anchors.margins: 18; spacing: 14
                                            Rectangle {
                                                Layout.preferredWidth: 50; Layout.preferredHeight: 50; radius: 14; color: "#EFEBFF"
                                                FaIcon { anchors.centerIn: parent; nombre: ventana.iconoCategoria(modelData.id); width: 24; height: 24 }
                                            }
                                            Label { text: modelData.nombre; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: tinta; font.pixelSize: 17; font.bold: true }
                                            FaIcon { nombre: "arrow-right"; Layout.preferredWidth: 17; Layout.preferredHeight: 17; opacity: 0.65 }
                                        }
                                    }
                                    MouseArea {
                                        id: area
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            ventana.reproducirSonidoBoton()
                                            ventana.elegir(modelData.id)
                                        }
                                    }
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        visible: diagnostico.pantalla === "preguntas" && !ventana.secuenciaActiva
                        opacity: visible ? 1 : 0
                        Behavior on opacity { NumberAnimation { duration: 230 } }
                        Layout.fillWidth: true
                        spacing: 18
                        HeroCard {
                            Layout.fillWidth: true; Layout.topMargin: 18
                            icono: "circle-question"; etiqueta: "CONSULTA EN CURSO"
                            titulo: "Cuestionario"
                            descripcion: "Puedes volver o corregir una respuesta. Las posteriores se preguntarán de nuevo."
                            mascotaRecurso: diagnostico.pantalla === "preguntas" && !ventana.secuenciaActiva ? diagnostico.recursoMascota : ""
                            mascotaFlotar: true
                            activo: diagnostico.pantalla === "preguntas" && !ventana.secuenciaActiva
                        }
                        Rectangle {
                            visible: diagnostico.contradicciones.length > 0
                            Layout.fillWidth: true
                            implicitHeight: contradiccionesTexto.implicitHeight + 32
                            radius: 14
                            color: "#FFF1F1"
                            Label {
                                id: contradiccionesTexto
                                anchors.fill: parent
                                anchors.margins: 16
                                text: diagnostico.contradicciones.map(c => c.explicacion).join("\n")
                                color: "#8C2741"
                                wrapMode: Text.WordWrap
                            }
                        }
                        SurfaceCard {
                            visible: !!diagnostico.preguntaActual.id
                            Layout.fillWidth: true
                            implicitHeight: preguntaCol.implicitHeight + 44
                            fondo: "#F7F5FF"
                            borde: "#E7E1FF"
                            ColumnLayout {
                                id: preguntaCol
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 22
                                spacing: 14
                                RowLayout {
                                    FaIcon { nombre: "circle-question"; Layout.preferredWidth: 18; Layout.preferredHeight: 18 }
                                    Label { text: "PREGUNTA ACTUAL"; color: violeta; font.pixelSize: 12; font.bold: true; font.letterSpacing: 1 }
                                }
                                Label {
                                    text: diagnostico.preguntaActual.texto || ""
                                    color: tinta
                                    font.pixelSize: 22
                                    font.bold: true
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }
                                Label {
                                    text: diagnostico.preguntaActual.ayuda || ""
                                    color: tenue
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }
                                Flow {
                                    Layout.fillWidth: true
                                    spacing: 12
                                    ActionButton { text: "Sí"; icono: "circle-check"; onClicked: diagnostico.responder(diagnostico.preguntaActual.id, "si") }
                                    ActionButton { text: "No"; icono: "circle-xmark"; secundario: true; onClicked: diagnostico.responder(diagnostico.preguntaActual.id, "no") }
                                    ActionButton { text: "No estoy seguro"; icono: "circle-question"; secundario: true; onClicked: diagnostico.responder(diagnostico.preguntaActual.id, "no_estoy_seguro") }
                                }
                            }
                        }
                        Label {
                            visible: diagnostico.terminal.length > 0
                            text: diagnostico.mensajeTerminal
                            color: tinta
                            font.pixelSize: 17
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                        Flow {
                            Layout.fillWidth: true; spacing: 10
                            ActionButton {
                                text: "Volver"
                                icono: "arrow-left"; secundario: true
                                enabled: diagnostico.historial.length > 0
                                onClicked: diagnostico.volver()
                            }
                            ActionButton {
                                text: "Ver resultado disponible"
                                icono: "magnifying-glass"
                                enabled: diagnostico.contradicciones.length === 0 && diagnostico.terminal !== "@bloqueo_energia"
                                onClicked: ventana.iniciarSecuenciaResultado()
                            }
                        }
                        Label {
                            visible: diagnostico.historial.length > 0
                            text: "Respuestas de esta consulta"
                            font.pixelSize: 19
                            font.bold: true
                            color: tinta
                        }
                        Repeater {
                            model: diagnostico.historial
                            delegate: SurfaceCard {
                                required property var modelData
                                Layout.fillWidth: true
                                implicitHeight: historialFila.implicitHeight + 22
                                RowLayout {
                                    id: historialFila
                                    anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 11; spacing: 10
                                    Label { Layout.fillWidth: true; text: modelData.texto; color: tinta; wrapMode: Text.WordWrap }
                                    StatusTag { estado: modelData.respuesta === "si" ? "verdadero" : modelData.respuesta === "no" ? "falso" : "desconocido"; texto: modelData.respuesta === "si" ? "Sí" : modelData.respuesta === "no" ? "No" : "No estoy seguro" }
                                    ActionButton { text: "Editar"; icono: "pen"; secundario: true; onClicked: diagnostico.editar(modelData.indice) }
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        visible: ventana.secuenciaActiva || diagnostico.pantalla === "analisis"
                        opacity: visible ? 1 : 0
                        Behavior on opacity { NumberAnimation { duration: 230 } }
                        Layout.fillWidth: true
                        Layout.preferredWidth: contenido.width
                        Layout.topMargin: 80
                        Item {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.preferredWidth: 220
                            Layout.preferredHeight: 220
                            Mascota {
                                objectName: "mascotaAnalisis"
                                anchors.centerIn: parent
                                width: ventana.faseVisual === "idea" ? 214 : 190
                                height: width
                                recurso: ventana.faseVisual === "idea"
                                    ? Qt.resolvedUrl("../assets/mascota/mascota-idea1.png")
                                    : ventana.secuenciaActiva
                                        ? Qt.resolvedUrl("../assets/mascota/mascota-analizando1.png")
                                        : diagnostico.pantalla === "analisis" ? diagnostico.recursoMascota : ""
                                animarEntrada: true
                                flotar: true
                            }
                        }
                        BusyIndicator {
                            Layout.alignment: Qt.AlignHCenter
                            running: parent.visible && ventana.faseVisual !== "idea"
                            visible: running
                        }
                        Label {
                            objectName: "textoAnalisis"
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            text: ventana.faseVisual === "idea" ? "Una idea para revisar…" : "Revisando las reglas y las observaciones…"
                            color: tinta
                            font.pixelSize: 20
                        }
                    }

                    ColumnLayout {
                        visible: diagnostico.pantalla === "resultados"
                        opacity: visible ? 1 : 0
                        Behavior on opacity { NumberAnimation { duration: 230 } }
                        Layout.fillWidth: true
                        spacing: 18
                        HeroCard {
                            Layout.fillWidth: true; Layout.topMargin: 18
                            icono: "lightbulb"; etiqueta: "REVISIÓN TÉCNICA"
                            titulo: "Resultado de la consulta"
                            tituloFormateado: "Resultado de la <font color='#6355FF'>consulta</font>"
                            descripcion: "Hipótesis para orientar una revisión técnica."
                            mascotaRecurso: diagnostico.pantalla === "resultados" ? diagnostico.recursoMascota : ""
                            activo: diagnostico.pantalla === "resultados"
                        }
                        SurfaceCard {
                            visible: !diagnostico.resultado.principal
                            Layout.fillWidth: true; fondo: "#F6F3FF"
                            implicitHeight: sinConclusion.implicitHeight + 36
                            Label {
                                id: sinConclusion; anchors.fill: parent; anchors.margins: 18
                                text: diagnostico.resultado.explicacionSinConclusion || ""
                                color: tinta; wrapMode: Text.WordWrap
                            }
                        }
                        HypothesisCard {
                            visible: !!diagnostico.resultado.principal
                            Layout.fillWidth: true; principal: true
                            hipotesis: diagnostico.resultado.principal || ({})
                        }
                        Label {
                            visible: !!diagnostico.resultado.alternativas && diagnostico.resultado.alternativas.length > 0
                            text: "Otras hipótesis compatibles"
                            font.pixelSize: 21; font.bold: true; color: tinta
                        }
                        Repeater {
                            model: diagnostico.resultado.alternativas || []
                            delegate: HypothesisCard {
                                required property var modelData
                                Layout.fillWidth: true
                                hipotesis: modelData
                            }
                        }
                        Label {
                            text: diagnostico.resultado.explicacionPrioridad || ""
                            color: tenue; wrapMode: Text.WordWrap; Layout.fillWidth: true
                        }
                        Label {
                            text: diagnostico.resultado.aviso || ""
                            color: tinta; font.bold: true; wrapMode: Text.WordWrap; Layout.fillWidth: true
                        }
                        Flow {
                            Layout.fillWidth: true; spacing: 10
                            ActionButton { text: "Revisar respuesta"; icono: "rotate-left"; secundario: true; onClicked: diagnostico.volver() }
                            ActionButton { text: "Exportar PDF"; icono: "file-pdf"; onClicked: guardarPdf.open() }
                        }
                        SurfaceCard {
                            Layout.fillWidth: true
                            implicitHeight: razonamientoCol.implicitHeight + 36
                            ColumnLayout {
                                id: razonamientoCol
                                anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 18
                                spacing: 12
                                Label { text: "Cómo se obtuvo el resultado"; color: tinta; font.bold: true; font.pixelSize: 21 }
                                Label { text: "Observaciones confirmadas"; color: violeta; font.bold: true }
                                Repeater {
                                    model: Object.keys(diagnostico.resultado.observacionesConfirmadas || {}).sort()
                                    delegate: RowLayout {
                                        required property string modelData
                                        Layout.fillWidth: true
                                        Label { text: modelData; color: tenue; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                        StatusTag { estado: diagnostico.resultado.observacionesConfirmadas[modelData] }
                                    }
                                }
                                Label { text: "Criterios ordinales"; color: violeta; font.bold: true }
                                Repeater {
                                    model: diagnostico.resultado.criterios || []
                                    delegate: Label {
                                        required property var modelData
                                        Layout.fillWidth: true
                                        text: modelData.diagnosticoId + ": " + modelData.calidadTexto + ", " + modelData.especificidad + " observaciones, " + modelData.prioridadTexto
                                        color: tenue; wrapMode: Text.WordWrap
                                    }
                                }
                                Label { text: "Hechos derivados"; color: violeta; font.bold: true }
                                Repeater {
                                    model: diagnostico.resultado.hechosDerivados || []
                                    delegate: RowLayout {
                                        required property var modelData
                                        Layout.fillWidth: true
                                        Label { text: modelData.hechoId + " (" + modelData.reglas.join(", ") + ")"; color: tenue; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                        StatusTag { estado: modelData.estado }
                                    }
                                }
                            }
                        }
                        Label { text: "Reglas activadas"; color: tinta; font.bold: true; font.pixelSize: 21 }
                        Repeater {
                            model: diagnostico.resultado.trazas || []
                            delegate: TraceCard { required property var modelData; Layout.fillWidth: true; traza: modelData }
                        }
                    }
                }
            }
        }
    }
}

