"""Pruebas de carga Qt y PDF, sin casos reservados."""

import importlib.util
import os
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

QT_DISPONIBLE = importlib.util.find_spec("PySide6") is not None

PRUEBA_PDF = r'''
import json
import sys
from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication
from PySide6.QtPdf import QPdfDocument

app = QGuiApplication([])
resultados = []
for ruta in sys.argv[1:]:
    lector = QPdfDocument()
    lector.load(ruta)
    imagenes = [lector.render(i, QSize(595, 842)) for i in range(lector.pageCount())]
    resultados.append({
        "error": str(lector.error()),
        "paginas": lector.pageCount(),
        "textos": [lector.getAllText(i).text() for i in range(lector.pageCount())],
        "renderCorrecto": all(not imagen.isNull() for imagen in imagenes),
        "colores": [imagenes[0].pixelColor(530, y).name() for y in range(200, 420)],
        "mascota": any(imagenes[0].pixelColor(x, y).name() not in ("#ffffff", "#211d41")
                       for x in range(470, 530, 10) for y in range(60, 125, 10)),
        "franjaLibre": [all(imagen.pixelColor(x, y).name() == "#ffffff"
                             for x in range(50, 550, 25) for y in range(768, 781, 3))
                        for imagen in imagenes],
    })
    lector.close()
print(json.dumps(resultados))
'''

GENERAR_PDF_PRUEBAS = r'''
import json
import sys
from pathlib import Path
from PySide6.QtGui import QGuiApplication

raiz = Path(sys.argv[1])
salida = Path(sys.argv[2])
sys.path.insert(0, str(raiz / "src"))
from diagnostico_pc.gui.pdf_export import exportar_reporte
from diagnostico_pc.gui.serialization import serializar_resultado
from diagnostico_pc.gui.session import SesionGrafica
from diagnostico_pc.selector import seleccionar_modelo

app = QGuiApplication([])
sesion = SesionGrafica(raiz)
sesion.elegir_categoria("temperatura")
sesion.responder(sesion.estado()["preguntaActual"]["id"], "no_estoy_seguro")
registradas = {sesion.gestor.preguntas[r.pregunta_id].hecho for r in sesion.gestor.historial}
exportar_reporte(salida / "reporte.pdf", sesion.ver_resultado(), sesion.gestor.observaciones,
                 sesion.modelo_c.hechos, registradas)
for nombre, destino in (("arranque_multinivel_b", "reporte_cadena.pdf"),
                        ("hipotesis_termicas_c", "reporte_alternativas.pdf")):
    observaciones = json.loads((raiz / "ejemplos" / (nombre + ".json")).read_text(encoding="utf-8"))
    resultado = serializar_resultado(seleccionar_modelo("C", raiz / "data/conocimiento").evaluar(observaciones))
    exportar_reporte(salida / destino, resultado, observaciones, sesion.modelo_c.hechos)
    if nombre == "hipotesis_termicas_c":
        # Fixture de paginación: repite datos reales solo para forzar un reporte largo.
        largo = dict(resultado)
        largo["trazas"] = resultado["trazas"] * 12
        extensas = {hecho: "desconocido" for hecho in sesion.modelo_c.sintomas}
        extensas.update(observaciones)
        exportar_reporte(salida / "reporte_largo.pdf", largo, extensas, sesion.modelo_c.hechos)
'''

PRUEBA_INTERACTIVIDAD = r'''
import json
import sys
from pathlib import Path

import shiboken6
from PySide6.QtCore import QPoint, QPointF, Qt, QTimer, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest

raiz = Path(sys.argv[1])
sys.path.insert(0, str(raiz / "src"))
from diagnostico_pc.gui.bridge import PuenteDiagnostico

mensajes = []
qInstallMessageHandler(lambda tipo, contexto, mensaje: mensajes.append(mensaje))
app = QGuiApplication([])
motor = QQmlApplicationEngine()
puente = PuenteDiagnostico()
motor.rootContext().setContextProperty("diagnostico", puente)
motor.load(QUrl.fromLocalFile(str(raiz / "src/diagnostico_pc/gui/qml/Main.qml")))
ventana = shiboken6.wrapInstance(shiboken6.getCppPointer(motor.rootObjects()[0])[0], QQuickWindow)
pulsos = []
errores = []

def recorrer(item):
    yield item
    for hijo in item.childItems():
        yield from recorrer(hijo)

def pulsar(texto):
    for item in recorrer(ventana.contentItem()):
        if item.property("text") == texto and item.isVisible() and item.width() > 0 and item.height() > 0:
            centro = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
            QTest.mouseClick(ventana, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
                             QPoint(round(centro.x()), round(centro.y())))
            return
    errores.append("Control no visible: " + texto)

def comprobar_inicio():
    if puente.pantalla != "bienvenida":
        errores.append("La bienvenida avanzó sola")
    pulsar("Empezar diagnóstico")
    if puente.pantalla != "seleccion":
        errores.append("El botón de bienvenida no respondió")

def comprobar_categoria():
    if len(puente.categorias) != 7:
        errores.append("No aparecieron siete categorías")
    nombres = {item.property("text") for item in recorrer(ventana.contentItem())}
    if any(categoria["nombre"] not in nombres for categoria in puente.categorias):
        errores.append("Faltan tarjetas de categoría en QML")
    pulsar(puente.categorias[0]["nombre"])
    if puente.pantalla != "preguntas" or not puente.preguntaActual.get("id"):
        errores.append("La tarjeta de categoría no respondió")

def comprobar_respuesta():
    pulsar("Sí")
    if len(puente.historial) != 1:
        errores.append("El botón de respuesta no respondió")

def terminar():
    resultado = {"pulsos": len(pulsos), "pantalla": puente.pantalla,
                 "respuestas": len(puente.historial), "errores": errores,
                 "polishLoops": sum("polish() loop" in m for m in mensajes)}
    print(json.dumps(resultado), flush=True)
    ventana.close()
    app.quit()

reloj = QTimer()
reloj.timeout.connect(lambda: pulsos.append(1))
reloj.start(500)
QTimer.singleShot(1900, comprobar_inicio)
QTimer.singleShot(2900, comprobar_categoria)
QTimer.singleShot(3900, comprobar_respuesta)
QTimer.singleShot(6800, terminar)
app.exec()
'''

PRUEBA_BOTONES = r'''
import json
import sys
from pathlib import Path

import shiboken6
from PySide6.QtCore import QObject, QPoint, QPointF, Qt, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QSignalSpy, QTest

raiz = Path(sys.argv[1])
sys.path.insert(0, str(raiz / "src"))
from diagnostico_pc.gui.bridge import PuenteDiagnostico

mensajes = []
qInstallMessageHandler(lambda tipo, contexto, mensaje: mensajes.append(mensaje))
app = QGuiApplication([])
motor = QQmlApplicationEngine()
puente = PuenteDiagnostico()
motor.rootContext().setContextProperty("diagnostico", puente)
motor.load(QUrl.fromLocalFile(str(raiz / "src/diagnostico_pc/gui/qml/Main.qml")))
ventana = shiboken6.wrapInstance(shiboken6.getCppPointer(motor.rootObjects()[0])[0], QQuickWindow)
errores = []

def recorrer(item):
    yield item
    for hijo in item.childItems():
        yield from recorrer(hijo)

def boton(texto):
    return next(item for item in recorrer(ventana.contentItem())
                if item.property("text") == texto and item.isVisible()
                and "AbstractButton" in item.metaObject().superClass().className())

def alineado(control):
    contenido = control.property("contentItem")
    fila = contenido.childItems()[0]
    return (abs(fila.x() + fila.width() / 2 - contenido.width() / 2) < 1
            and abs(fila.y() + fila.height() / 2 - contenido.height() / 2) < 1
            and contenido.width() >= fila.width())

QTest.qWait(300)
audio = next(item for item in recorrer(ventana.contentItem()) if item.objectName() == "audioAplicacion")
if not audio.property("bienvenidaReproducida"):
    errores.append("La bienvenida no solicitó su sonido al aparecer la mascota")
for nombre, volumen in (("salidaBienvenida", 0.15), ("salidaAnalizando", 0.15),
                        ("salidaIdea", 0.18), ("audioBoton", 0.15)):
    salida = audio.findChild(QObject, nombre)
    if salida is None or abs(float(salida.property("volume")) - volumen) > 0.001:
        errores.append("Volumen incorrecto: " + nombre)
for nombre in ("audioBienvenida", "audioAnalizando", "audioIdea", "audioBoton"):
    reproductor = audio.findChild(QObject, nombre)
    if reproductor is None or reproductor.property("loops") != 1:
        errores.append("El audio no está configurado para una sola reproducción: " + nombre)
sonidos = QSignalSpy(audio.sonidoSolicitado)
audio.reproducirBienvenida()
if sonidos.count() != 0:
    errores.append("El sonido de bienvenida se solicitó más de una vez")
inicio = boton("Empezar diagnóstico")
QTest.keyClick(ventana, Qt.Key.Key_Tab)
QTest.qWait(80)
if not inicio.property("visualFocus"):
    errores.append("Tab no mostró el foco violeta")
clic_inicio = QSignalSpy(inicio.clicked)
QTest.keyClick(ventana, Qt.Key.Key_Return)
if puente.pantalla != "seleccion" or clic_inicio.count() != 1:
    errores.append("Enter no activó una sola vez el botón")
if sonidos.count() != 1 or sonidos.at(0)[0] != "boton":
    errores.append("El clic de bienvenida no emitió un solo pop")

puente.elegirCategoria("temperatura")
QTest.qWait(250)
respuesta = boton("No estoy seguro")
if not alineado(respuesta):
    errores.append("El contenido del botón largo no está centrado")
ancho, alto = respuesta.width(), respuesta.height()
centro = respuesta.mapToScene(QPointF(ancho / 2, alto / 2))
punto = QPoint(round(centro.x()), round(centro.y()))
QTest.mouseMove(ventana, punto)
QTest.qWait(240)
if sonidos.count() != 1:
    errores.append("El hover reprodujo el pop")
if abs(respuesta.scale() - 1.03) > 0.005 or respuesta.property("visualFocus"):
    errores.append("El hover no llegó a 103 % o conservó el foco de teclado")
QTest.mousePress(ventana, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, punto)
QTest.qWait(240)
if abs(respuesta.scale() - 0.97) > 0.005:
    errores.append("La pulsación no llegó a 97 %")
if respuesta.width() != ancho or respuesta.height() != alto:
    errores.append("La animación cambió la geometría del layout")
clic_respuesta = QSignalSpy(respuesta.clicked)
QTest.mouseRelease(ventana, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, punto)
if clic_respuesta.count() != 1 or len(puente.historial) != 1:
    errores.append("La respuesta no se ejecutó exactamente una vez")
if sonidos.count() != 2 or sonidos.at(1)[0] != "boton":
    errores.append("La respuesta no emitió un solo pop")

puente.verResultado()
QTest.qWait(250)
for texto in ("Revisar respuesta", "Exportar PDF"):
    if not alineado(boton(texto)):
        errores.append("Contenido desalineado: " + texto)
resultado = {"errores": errores,
             "polishLoops": sum("polish() loop" in mensaje for mensaje in mensajes)}
print(json.dumps(resultado), flush=True)
ventana.close()
'''

PRUEBA_SECUENCIA_MASCOTA = r'''
import json
import sys
from pathlib import Path

import shiboken6
from PySide6.QtCore import QObject, QPoint, QPointF, Qt, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QSignalSpy, QTest

raiz = Path(sys.argv[1])
sys.path.insert(0, str(raiz / "src"))
from diagnostico_pc.gui.bridge import PuenteDiagnostico

mensajes = []
qInstallMessageHandler(lambda tipo, contexto, mensaje: mensajes.append(mensaje))
app = QGuiApplication([])
motor = QQmlApplicationEngine()
puente = PuenteDiagnostico()
motor.rootContext().setContextProperty("diagnostico", puente)
motor.load(QUrl.fromLocalFile(str(raiz / "src/diagnostico_pc/gui/qml/Main.qml")))
ventana = shiboken6.wrapInstance(shiboken6.getCppPointer(motor.rootObjects()[0])[0], QQuickWindow)
errores = []

def recorrer(item):
    yield item
    for hijo in item.childItems():
        yield from recorrer(hijo)

def pulsar(texto):
    for item in recorrer(ventana.contentItem()):
        if item.property("text") == texto and item.isVisible():
            centro = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
            QTest.mouseClick(ventana, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
                             QPoint(round(centro.x()), round(centro.y())))
            return
    errores.append("Control no encontrado: " + texto)

def pose_visible(objeto, archivo):
    for item in recorrer(ventana.contentItem()):
        if item.objectName() == objeto and item.isVisible():
            recurso = item.property("recurso")
            url = recurso.toString() if hasattr(recurso, "toString") else str(recurso)
            if url.endswith(archivo):
                return True
    return False

audio = next(item for item in recorrer(ventana.contentItem()) if item.objectName() == "audioAplicacion")
sonidos = QSignalSpy(audio.sonidoSolicitado)
def nombres_sonidos():
    return [sonidos.at(indice)[0] for indice in range(sonidos.count())]

def comprobar_centro(fase, ancho):
    mascota = next(item for item in recorrer(ventana.contentItem())
                   if item.objectName() == "mascotaAnalisis")
    etiqueta = next(item for item in recorrer(ventana.contentItem())
                    if item.objectName() == "textoAnalisis")
    centro_mascota = mascota.mapToScene(QPointF(mascota.width() / 2, mascota.height() / 2)).x()
    centro_etiqueta = etiqueta.mapToScene(QPointF(etiqueta.width() / 2, etiqueta.height() / 2)).x()
    if abs(centro_mascota - centro_etiqueta) > 2 or abs(centro_mascota - ventana.width() / 2) > 6:
        errores.append("Mascota y texto descentrados: " + fase)
    if abs(mascota.width() - ancho) > 1 or abs(mascota.height() - ancho) > 1:
        errores.append("Tamaño incorrecto de la pose: " + fase)

transiciones_analisis = []
def comprobar_pose_intermedia():
    if puente.pantalla == "analisis" and ventana.property("secuenciaActiva"):
        transiciones_analisis.append(ventana.property("faseVisual"))
        if ventana.property("faseVisual") != "idea" or not pose_visible("mascotaAnalisis", "mascota-idea1.png"):
            errores.append("La pose analizando reapareció antes del resultado")

puente.estadoCambiado.connect(comprobar_pose_intermedia)

QTest.qWait(250)
if not puente.recursoMascota.endswith("mascota-saludando.png"):
    errores.append("Falta la pose de bienvenida")
if not pose_visible("mascotaBienvenida", "mascota-saludando.png"):
    errores.append("La mascota de bienvenida no se dibujó")
QTest.qWait(1850)
if puente.pantalla != "bienvenida":
    errores.append("La bienvenida avanzó automáticamente")
puente.irASeleccion()
QTest.qWait(250)
if not puente.recursoMascota.endswith("mascota-default1.png"):
    errores.append("Falta la pose de categorías")
if not pose_visible("mascotaHero", "mascota-default1.png"):
    errores.append("La mascota de categorías no se dibujó")
puente.elegirCategoria("temperatura")
QTest.qWait(250)
if not puente.recursoMascota.endswith("mascota-escribiendo1.png"):
    errores.append("Falta la pose del cuestionario")
if not pose_visible("mascotaHero", "mascota-escribiendo1.png"):
    errores.append("La mascota del cuestionario no se dibujó")
pulsar("Ver resultado disponible")
if ventana.property("faseVisual") != "analizando" or puente.pantalla != "preguntas":
    errores.append("No comenzó la fase de análisis")
if sorted(nombres_sonidos()) != ["analizando", "boton"]:
    errores.append("El clic y la fase de análisis no solicitaron sus sonidos una vez")
if not pose_visible("mascotaAnalisis", "mascota-analizando1.png"):
    errores.append("La pose de análisis no se dibujó")
comprobar_centro("analizando", 190)
QTest.qWait(2250)
if ventana.property("faseVisual") != "analizando":
    errores.append("La fase de análisis duró menos de 2,5 segundos")
QTest.qWait(400)
if ventana.property("faseVisual") != "idea" or puente.pantalla != "preguntas":
    errores.append("No apareció la pose de idea antes del resultado")
if nombres_sonidos().count("idea") != 1 or nombres_sonidos().count("analizando") != 1:
    errores.append("La transición duplicó o perdió un sonido de mascota")
if not pose_visible("mascotaAnalisis", "mascota-idea1.png"):
    errores.append("La pose de idea no se dibujó")
comprobar_centro("idea", 214)
QTest.qWait(900)
if puente.pantalla != "resultados" or ventana.property("secuenciaActiva"):
    errores.append("La secuencia no terminó en resultados")
if nombres_sonidos().count("idea") != 1:
    errores.append("El resultado volvió a reproducir el sonido de idea")
if not transiciones_analisis:
    errores.append("No se observó el paso intermedio del puente")
if puente.resultado.get("modelo") != "C":
    errores.append("El resultado final no procede de C")
if not pose_visible("mascotaHero", "mascota-idea1.png"):
    errores.append("La pose de resultados no se dibujó")

puente.elegirCategoria("temperatura")
QTest.qWait(200)
pulsar("Ver resultado disponible")
QTest.qWait(200)
pulsar("Categorías")
QTest.qWait(100)
reproductor_analisis = audio.findChild(QObject, "audioAnalizando")
reproductor_analisis = shiboken6.wrapInstance(
    shiboken6.getCppPointer(reproductor_analisis)[0], QMediaPlayer
)
if reproductor_analisis.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
    errores.append("El sonido de análisis continuó tras abandonar la pantalla")
QTest.qWait(3450)
if puente.pantalla != "seleccion" or ventana.property("secuenciaActiva"):
    errores.append("La navegación no canceló la secuencia")

print(json.dumps({"errores": errores,
                  "polishLoops": sum("polish() loop" in mensaje for mensaje in mensajes)}), flush=True)
ventana.close()
'''

PRUEBA_HERO_CARDS = r'''
import json
import sys
from pathlib import Path

import shiboken6
from PySide6.QtCore import QPointF, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest

raiz = Path(sys.argv[1])
sys.path.insert(0, str(raiz / "src"))
from diagnostico_pc.gui.bridge import PuenteDiagnostico

mensajes = []
qInstallMessageHandler(lambda tipo, contexto, mensaje: mensajes.append(mensaje))
app = QGuiApplication([])
motor = QQmlApplicationEngine()
puente = PuenteDiagnostico()
motor.rootContext().setContextProperty("diagnostico", puente)
motor.load(QUrl.fromLocalFile(str(raiz / "src/diagnostico_pc/gui/qml/Main.qml")))
ventana = shiboken6.wrapInstance(shiboken6.getCppPointer(motor.rootObjects()[0])[0], QQuickWindow)
errores = []

def recorrer(item):
    yield item
    for hijo in item.childItems():
        yield from recorrer(hijo)

def visible(nombre):
    return next((item for item in recorrer(ventana.contentItem())
                 if item.objectName() == nombre and item.isVisible()), None)

def revisar(fase):
    card = visible("tarjetaBienvenida" if fase == "bienvenida" else "heroCard")
    mascota = visible("mascotaBienvenida" if fase == "bienvenida" else "mascotaHero")
    encabezado = visible("encabezadoPrincipal")
    divisor = visible("divisorEncabezado")
    if (encabezado is None) != (fase == "bienvenida") or (divisor is None) != (fase == "bienvenida"):
        errores.append(f"Encabezado incorrecto: {fase}, {ventana.width()}x{ventana.height()}")
    if card is None or mascota is None:
        errores.append(f"Falta hero card o mascota: {fase}, {ventana.width()}x{ventana.height()}")
        return
    arriba = card.mapToScene(QPointF(0, 0)).y()
    izquierda = card.mapToScene(QPointF(0, 0)).x()
    mascota_arriba = mascota.mapToScene(QPointF(0, 0)).y()
    derecha = card.mapToScene(QPointF(card.width(), 0)).x()
    mascota_derecha = mascota.mapToScene(QPointF(mascota.width(), 0)).x()
    if izquierda < -1 or derecha > ventana.width() + 1:
        errores.append(f"Hero card fuera de ventana: {fase}, {ventana.width()}x{ventana.height()}")
    if divisor is not None:
        separacion = arriba - divisor.mapToScene(QPointF(0, divisor.height())).y()
        if not 24 <= separacion <= 36:
            errores.append(f"Separación incorrecta ({separacion:.1f}): {fase}, {ventana.width()}x{ventana.height()}")
    if mascota_arriba >= arriba - 10 or mascota_derecha > derecha + 12:
        errores.append(f"Mascota mal situada: {fase}, {ventana.width()}x{ventana.height()}; "
                       f"arriba={arriba:.1f}, mascota={mascota_arriba:.1f}, "
                       f"derecha={derecha:.1f}, mascota_derecha={mascota_derecha:.1f}")
    if fase in ("preguntas", "resultados"):
        botones = [item for item in recorrer(ventana.contentItem())
                   if item.property("text") == "Categorías"
                   and item.property("icono") == "list-check" and item.isVisible()]
        if len(botones) != 1:
            errores.append(f"Botón Categorías ausente: {fase}")
        elif mascota_arriba <= botones[0].mapToScene(QPointF(0, botones[0].height())).y():
            errores.append(f"Mascota y botón Categorías se superponen: {fase}")
    area = visible("areaDesplazamiento")
    if area is not None and area.property("contentWidth") > area.width() + 1:
        errores.append(f"Scroll horizontal: {fase}, {ventana.width()}x{ventana.height()}")
    fondos = [item for item in recorrer(card) if item.objectName() == "heroBackdrop"]
    if len(fondos) != 1 or not fondos[0].property("animar"):
        errores.append(f"Fondo decorativo inactivo: {fase}")

for fase in ("bienvenida", "seleccion", "preguntas", "resultados"):
    if fase == "seleccion":
        puente.irASeleccion()
    elif fase == "preguntas":
        puente.elegirCategoria("temperatura")
    elif fase == "resultados":
        puente.verResultado()
    QTest.qWait(800)
    for ancho, alto in ((760, 600), (1080, 760), (1440, 900)):
        ventana.resize(ancho, alto)
        QTest.qWait(120)
        revisar(fase)

fondo = visible("heroBackdrop")
if fondo is not None:
    elementos = [item for item in recorrer(fondo) if item.property("derivaX") is not None]
    if elementos:
        antes = float(elementos[0].property("derivaX"))
        QTest.qWait(350)
        despues = float(elementos[0].property("derivaX"))
        if abs(despues - antes) < 0.01:
            errores.append("El fondo visible no se anima")
    else:
        errores.append("Falta la mancha animada")

print(json.dumps({"errores": errores,
                  "polishLoops": sum("polish() loop" in mensaje for mensaje in mensajes)}), flush=True)
ventana.close()
'''


@unittest.skipUnless(QT_DISPONIBLE, "PySide6 aún no está instalado en este Python")
class PruebasQt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault("QT_QUICK_BACKEND", "software")
        from PySide6.QtGui import QGuiApplication
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    @unittest.skipUnless(sys.platform == "win32", "Prueba de respuesta de la ventana Windows")
    def test_ventana_responde_con_ambos_backends(self):
        for backend in ("predeterminado", "software"):
            with self.subTest(backend=backend):
                entorno = os.environ.copy()
                entorno["QT_QPA_PLATFORM"] = "windows"
                entorno.pop("QT_QUICK_BACKEND", None)
                entorno.pop("QSG_RHI_BACKEND", None)
                if backend == "software":
                    entorno["QSG_RHI_BACKEND"] = "software"
                proceso = subprocess.run(
                    [sys.executable, "-c", PRUEBA_INTERACTIVIDAD, str(RAIZ)],
                    cwd=RAIZ, env=entorno, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=14, check=False,
                )
                self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
                resultado = json.loads(proceso.stdout.strip().splitlines()[-1])
                self.assertEqual(resultado["errores"], [], resultado)
                self.assertGreaterEqual(resultado["pulsos"], 12, resultado)
                self.assertEqual(resultado["pantalla"], "preguntas", resultado)
                self.assertEqual(resultado["respuestas"], 1, resultado)
                self.assertEqual(resultado["polishLoops"], 0, resultado)

    @unittest.skipUnless(sys.platform == "win32", "Prueba visual de botones Windows")
    def test_botones_alineados_animados_y_accesibles(self):
        entorno = os.environ.copy()
        entorno["QT_QPA_PLATFORM"] = "windows"
        entorno.pop("QT_QUICK_BACKEND", None)
        entorno.pop("QSG_RHI_BACKEND", None)
        proceso = subprocess.run(
            [sys.executable, "-c", PRUEBA_BOTONES, str(RAIZ)],
            cwd=RAIZ, env=entorno, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=12, check=False,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
        resultado = json.loads(proceso.stdout.strip().splitlines()[-1])
        self.assertEqual(resultado["errores"], [], resultado)
        self.assertEqual(resultado["polishLoops"], 0, resultado)

    def test_qml_carga_y_expone_siete_categorias(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtQml import QQmlApplicationEngine
        from diagnostico_pc.gui.bridge import PuenteDiagnostico

        motor = QQmlApplicationEngine()
        puente = PuenteDiagnostico()
        motor.rootContext().setContextProperty("diagnostico", puente)
        motor.load(QUrl.fromLocalFile(str(RAIZ / "src/diagnostico_pc/gui/qml/Main.qml")))
        self.assertEqual(len(motor.rootObjects()), 1)
        from PySide6.QtQuick import QQuickItem

        ventana = motor.rootObjects()[0]

        def textos_visibles(item):
            if isinstance(item, QQuickItem) and item.isVisible():
                texto = item.property("text")
                if isinstance(texto, str):
                    yield texto
                for hijo in item.childItems():
                    yield from textos_visibles(hijo)

        def comprobar_etiquetas():
            self.app.processEvents()
            textos = list(textos_visibles(ventana.contentItem()))
            self.assertFalse(
                any("modelo" in t.lower() or "compar" in t.lower() for t in textos), textos
            )
            return textos

        comprobar_etiquetas()  # Bienvenida
        puente.irASeleccion()
        self.assertEqual(len(puente.categorias), 7)
        comprobar_etiquetas()  # Categorías
        puente.elegirCategoria("temperatura")
        self.assertTrue(puente.preguntaActual["id"])
        self.assertEqual(puente.pantalla, "preguntas")
        comprobar_etiquetas()  # Cuestionario
        puente.verResultado()
        self.app.processEvents()
        self.assertEqual(puente.pantalla, "resultados")
        self.assertEqual(puente.resultado["modelo"], "C")
        textos = comprobar_etiquetas()  # Resultados
        self.assertTrue(any(t.startswith("Resultado de la ") for t in textos), textos)
        self.assertIn("Exportar PDF", textos)
        self.assertTrue(any(t.endswith("mo se obtuvo el resultado") for t in textos), textos)

    @unittest.skipUnless(sys.platform == "win32", "Prueba visual de hero cards Windows")
    def test_hero_cards_responden_en_tres_tamanos(self):
        entorno = os.environ.copy()
        entorno["QT_QPA_PLATFORM"] = "windows"
        entorno.pop("QT_QUICK_BACKEND", None)
        entorno.pop("QSG_RHI_BACKEND", None)
        proceso = subprocess.run(
            [sys.executable, "-c", PRUEBA_HERO_CARDS, str(RAIZ)],
            cwd=RAIZ, env=entorno, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=18, check=False,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
        resultado = json.loads(proceso.stdout.strip().splitlines()[-1])
        self.assertEqual(resultado["errores"], [], resultado)
        self.assertEqual(resultado["polishLoops"], 0, resultado)

    def test_bienvenida_permanece_hasta_iniciar(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtTest import QTest
        from diagnostico_pc.gui.bridge import PuenteDiagnostico

        motor = QQmlApplicationEngine()
        puente = PuenteDiagnostico()
        motor.rootContext().setContextProperty("diagnostico", puente)
        motor.load(QUrl.fromLocalFile(str(RAIZ / "src/diagnostico_pc/gui/qml/Main.qml")))
        self.assertEqual(len(motor.rootObjects()), 1)
        QTest.qWait(2000)
        self.assertEqual(puente.pantalla, "bienvenida")
        self.assertTrue(puente.recursoMascota.endswith("mascota-saludando.png"))
        puente.irASeleccion()
        self.assertEqual(puente.pantalla, "seleccion")

    def test_mascota_prefiere_png_y_admite_jpg(self):
        from diagnostico_pc.gui.bridge import PuenteDiagnostico

        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            recursos = raiz / "assets" / "mascota"
            recursos.mkdir(parents=True)
            puente = PuenteDiagnostico()
            with patch("diagnostico_pc.gui.bridge.__file__", str(raiz / "bridge.py")):
                self.assertEqual(puente.recursoMascota, "")
                jpg = recursos / "mascota-saludando.jpg"
                jpg.write_bytes(b"jpg")
                self.assertTrue(puente.recursoMascota.endswith("mascota-saludando.jpg"))
                png = recursos / "mascota-saludando.png"
                png.write_bytes(b"png")
                self.assertTrue(puente.recursoMascota.endswith("mascota-saludando.png"))

    def test_mascota_oculta_recurso_inexistente(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtQml import QQmlComponent, QQmlEngine
        from PySide6.QtTest import QTest

        motor = QQmlEngine()
        componente = QQmlComponent(
            motor, QUrl.fromLocalFile(str(RAIZ / "src/diagnostico_pc/gui/qml/Mascota.qml"))
        )
        mascota = componente.create()
        self.assertIsNotNone(mascota, componente.errors())
        mascota.setProperty("recurso", QUrl.fromLocalFile(str(RAIZ / "archivo-inexistente.png")))
        QTest.qWait(100)
        self.assertFalse(mascota.property("visible"))

    def test_audio_sin_archivos_no_detiene_qml(self):
        from PySide6.QtCore import QMetaObject, QUrl
        from PySide6.QtQml import QQmlComponent, QQmlEngine
        from PySide6.QtTest import QTest

        with tempfile.TemporaryDirectory() as carpeta:
            copia = Path(carpeta) / "AppAudio.qml"
            shutil.copyfile(RAIZ / "src/diagnostico_pc/gui/qml/AppAudio.qml", copia)
            motor = QQmlEngine()
            componente = QQmlComponent(motor, QUrl.fromLocalFile(str(copia)))
            audio = componente.create()
            self.assertIsNotNone(audio, componente.errors())
            audio.setProperty("pantalla", "bienvenida")
            self.assertTrue(QMetaObject.invokeMethod(audio, "reproducirBienvenida"))
            audio.setProperty("faseVisual", "analizando")
            QTest.qWait(50)
            audio.setProperty("faseVisual", "idea")
            self.assertTrue(QMetaObject.invokeMethod(audio, "reproducirBoton"))
            audio.setProperty("pantalla", "resultados")
            audio.setProperty("faseVisual", "")
            QTest.qWait(50)
            self.assertEqual(audio.property("pantalla"), "resultados")

    @unittest.skipUnless(sys.platform == "win32", "Prueba de secuencia visual Windows")
    def test_secuencia_visual_mascotas_y_cancelacion(self):
        entorno = os.environ.copy()
        entorno["QT_QPA_PLATFORM"] = "windows"
        entorno.pop("QT_QUICK_BACKEND", None)
        entorno.pop("QSG_RHI_BACKEND", None)
        proceso = subprocess.run(
            [sys.executable, "-c", PRUEBA_SECUENCIA_MASCOTA, str(RAIZ)],
            cwd=RAIZ, env=entorno, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=16, check=False,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
        resultado = json.loads(proceso.stdout.strip().splitlines()[-1])
        self.assertEqual(resultado["errores"], [], resultado)
        self.assertEqual(resultado["polishLoops"], 0, resultado)

    def test_traza_se_despliega_sin_cambiar_sus_datos(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtQml import QQmlComponent, QQmlEngine
        from PySide6.QtQuick import QQuickWindow

        motor = QQmlEngine()
        componente = QQmlComponent(
            motor, QUrl.fromLocalFile(str(RAIZ / "src/diagnostico_pc/gui/qml/TraceCard.qml"))
        )
        tarjeta = componente.create()
        self.assertIsNotNone(tarjeta, componente.errors())
        tarjeta.setProperty("width", 500)
        ventana = QQuickWindow()
        ventana.setWidth(600)
        ventana.setHeight(400)
        tarjeta.setParentItem(ventana.contentItem())
        ventana.show()
        traza = {
            "nivel": 2,
            "reglaId": "r_ejemplo",
            "explicacion": "La observación activa esta hipótesis.",
            "condiciones": [{"nombre": "Señal", "hechoId": "s_senal", "estado": "desconocido"}],
            "conclusionId": "d_ejemplo",
            "conclusionEstado": "",
        }
        tarjeta.setProperty("traza", traza)
        self.app.processEvents()
        QQuickWindow.grabWindow(ventana)
        altura_cerrada = tarjeta.property("implicitHeight")
        tarjeta.setProperty("abierto", True)
        self.app.processEvents()
        QQuickWindow.grabWindow(ventana)
        self.assertGreater(tarjeta.property("implicitHeight"), altura_cerrada)
        self.assertEqual(tarjeta.property("traza"), traza)
        ventana.close()

    def test_fondo_bienvenida_es_periodico(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtQml import QQmlComponent, QQmlEngine
        from PySide6.QtQuick import QQuickWindow
        from PySide6.QtTest import QTest

        motor = QQmlEngine()
        componente = QQmlComponent(
            motor, QUrl.fromLocalFile(str(RAIZ / "src/diagnostico_pc/gui/qml/WelcomeBackground.qml"))
        )
        fondo = componente.create()
        self.assertIsNotNone(fondo, componente.errors())
        fondo.setProperty("animando", False)
        fondo.setWidth(760)
        fondo.setHeight(600)
        ventana = QQuickWindow()
        ventana.setWidth(760)
        ventana.setHeight(600)
        fondo.setParentItem(ventana.contentItem())
        ventana.show()
        QTest.qWait(100)
        fondo.setProperty("desplazamiento", 0)
        primera = QQuickWindow.grabWindow(ventana)
        fondo.setProperty("desplazamiento", 360)
        segunda = QQuickWindow.grabWindow(ventana)
        self.assertEqual(primera, segunda)
        ventana.close()

    def test_pdf_es_legible_y_conserva_resultado(self):
        from diagnostico_pc.gui.pdf_layout import datos_reporte
        from diagnostico_pc.gui.session import SesionGrafica

        sesion = SesionGrafica(RAIZ)
        sesion.elegir_categoria("temperatura")
        sesion.responder(sesion.estado()["preguntaActual"]["id"], "no_estoy_seguro")
        resultado = sesion.ver_resultado()
        registradas = {sesion.gestor.preguntas[r.pregunta_id].hecho for r in sesion.gestor.historial}
        datos = datos_reporte(resultado, sesion.gestor.observaciones, sesion.modelo_c.hechos, registradas)
        self.assertEqual(len(datos["observaciones"]), 1)
        self.assertEqual(datos["observaciones"][0]["estado"], "desconocido")
        self.assertEqual(datos["hipotesis"], [])
        from diagnostico_pc.gui.serialization import serializar_resultado
        from diagnostico_pc.selector import seleccionar_modelo

        observaciones_con_cadena = json.loads(
            (RAIZ / "ejemplos/arranque_multinivel_b.json").read_text(encoding="utf-8")
        )
        resultado_con_cadena = serializar_resultado(
            seleccionar_modelo("C").evaluar(observaciones_con_cadena)
        )
        datos_con_cadena = datos_reporte(resultado_con_cadena, observaciones_con_cadena, sesion.modelo_c.hechos)
        self.assertTrue(datos_con_cadena["hipotesis"])
        self.assertTrue(datos_con_cadena["trazas"])
        self.assertEqual(
            [h["id"] for h in datos_con_cadena["hipotesis"]],
            [resultado_con_cadena["principal"]["id"], *[h["id"] for h in resultado_con_cadena["alternativas"]]],
        )
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "reporte.pdf"
            ruta_cadena = Path(carpeta) / "reporte_cadena.pdf"
            ruta_alternativas = Path(carpeta) / "reporte_alternativas.pdf"
            ruta_largo = Path(carpeta) / "reporte_largo.pdf"
            entorno = os.environ.copy()
            entorno["QT_QPA_PLATFORM"] = "windows" if sys.platform == "win32" else "offscreen"
            entorno.pop("QT_QUICK_BACKEND", None)
            generado = subprocess.run(
                [sys.executable, "-c", GENERAR_PDF_PRUEBAS, str(RAIZ), carpeta],
                cwd=RAIZ, env=entorno, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=20, check=False,
            )
            self.assertEqual(generado.returncode, 0, generado.stdout + generado.stderr)
            self.assertTrue(all(p.stat().st_size > 1000 for p in (ruta, ruta_cadena, ruta_alternativas, ruta_largo)))
            proceso = subprocess.run(
                [sys.executable, "-c", PRUEBA_PDF, str(ruta), str(ruta_cadena),
                 str(ruta_alternativas), str(ruta_largo)],
                cwd=RAIZ, env=entorno, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=20, check=False,
            )
            self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
            sin_hipotesis, cadena, alternativas, largo = json.loads(proceso.stdout.strip().splitlines()[-1])
            for reporte in (sin_hipotesis, cadena, alternativas, largo):
                self.assertEqual(reporte["error"], "Error.None_")
                self.assertTrue(reporte["renderCorrecto"])
                self.assertTrue(reporte["mascota"])
                self.assertTrue(all(reporte["franjaLibre"]), reporte["franjaLibre"])
                for numero, texto_pagina in enumerate(reporte["textos"], 1):
                    self.assertIn(f"Página {numero}", texto_pagina, reporte)
                    self.assertIn("Del síntoma a la solución.", texto_pagina)
                    self.assertNotIn("Modelo C", texto_pagina)
            texto_sin = "\n".join(sin_hipotesis["textos"])
            self.assertIn("Sin hipótesis concluyente", texto_sin)
            self.assertIn("Desconocido", texto_sin)
            self.assertIn("#f1f1f3", sin_hipotesis["colores"])
            self.assertGreaterEqual(cadena["paginas"], 2)
            texto_cadena = "\n".join(cadena["textos"])
            for esperado in ("Hipótesis principal", "Reglas y evidencias de soporte", "Hechos derivados",
                             "Trazas de razonamiento", "Guía de verificación técnica", "Observaciones del técnico:"):
                self.assertIn(esperado, texto_cadena)
            self.assertIn("#e8f6f0", cadena["colores"])
            self.assertIn("#fff1e5", cadena["colores"])
            texto_alternativas = "\n".join(alternativas["textos"])
            self.assertIn("Hipótesis alternativa 1", texto_alternativas)
            self.assertNotIn("El orden difiere del de B", texto_alternativas)
            self.assertGreater(largo["paginas"], alternativas["paginas"])
            self.assertIn("Hipótesis alternativa 1", "\n".join(largo["textos"]))
            from PySide6.QtCore import QUrl
            from diagnostico_pc.gui.bridge import PuenteDiagnostico

            ruta_puente = Path(carpeta) / "reporte_desde_gui.pdf"
            puente = PuenteDiagnostico(sesion)
            puente.exportarPdf(QUrl.fromLocalFile(str(ruta_puente)).toString())
            self.assertEqual(puente.error, "")
            self.assertTrue(ruta_puente.is_file())


if __name__ == "__main__":
    unittest.main()
