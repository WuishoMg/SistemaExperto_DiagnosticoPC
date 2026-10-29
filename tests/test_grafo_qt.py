"""Carga y tamaños del visualizador, sin casos finales."""

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
QT_DISPONIBLE = importlib.util.find_spec("PySide6") is not None

PRUEBA = r'''
import json, sys
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QPoint, QPointF, Qt, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow
from PySide6.QtTest import QTest

raiz = Path(sys.argv[1])
sys.path.insert(0, str(raiz / "src"))
from diagnostico_pc.gui.bridge import PuenteDiagnostico
from diagnostico_pc.gui.reasoning_graph import construir_grafo
from diagnostico_pc.gui.serialization import serializar_resultado
from diagnostico_pc.gestor_preguntas import RespuestaRegistrada
from diagnostico_pc.preguntas import RespuestaVisible

mensajes = []
qInstallMessageHandler(lambda tipo, contexto, mensaje: mensajes.append(mensaje))
app = QGuiApplication([])
puente = PuenteDiagnostico()
motor = QQmlApplicationEngine()
motor.rootContext().setContextProperty("diagnostico", puente)
motor.load(QUrl.fromLocalFile(str(raiz / "src/diagnostico_pc/gui/qml/Main.qml")))
assert motor.rootObjects(), mensajes
ventana = motor.rootObjects()[0]
def recorrer(item):
    yield item
    for hijo in item.childItems():
        yield from recorrer(hijo)
puente.elegirCategoria("temperatura")
respuestas = {"p30": "si", "p14": "si", "p15": "no_estoy_seguro", "p13": "no_estoy_seguro"}
for _ in range(5):
    actual = puente.preguntaActual.get("id")
    if not actual:
        break
    puente.responder(actual, respuestas[actual])
puente.verResultado()
app.processEvents()
assert puente.pantalla == "resultados", (puente.error, mensajes)
resultado = puente.resultado
assert resultado["principal"], resultado
ejemplo = json.loads((raiz / "ejemplos/arranque_multinivel_b.json").read_text(encoding="utf-8"))
por_hecho = {p.hecho: p for p in puente.sesion.preguntas}
por_id = {p.id: p for p in puente.sesion.preguntas}
historial_ejemplo = []
for hecho, estado in ejemplo.items():
    p = por_hecho[hecho]
    visible = RespuestaVisible.NO_ESTOY_SEGURO if estado == "desconocido" else (
        RespuestaVisible.SI if p.estado_si.value == estado else RespuestaVisible.NO)
    historial_ejemplo.append(RespuestaRegistrada(p.id, visible))
grafo_ejemplo = construir_grafo(serializar_resultado(puente.sesion.modelo_c.evaluar(ejemplo)),
                                historial_ejemplo, por_id, puente.sesion.modelo_c.hechos,
                                puente.sesion.modelo_c.reglas)
with patch.object(puente.sesion.modelo_c, "evaluar", side_effect=AssertionError("inferencia repetida")):
    puente.verRazonamiento()
    assert puente.pantalla == "razonamiento", (puente.error, mensajes)
    for ancho, alto in ((760, 600), (1080, 760), (1440, 900)):
        ventana.setWidth(ancho)
        ventana.setHeight(alto)
        app.processEvents()
        pantalla = ventana.findChild(QQuickItem, "pantallaRazonamiento")
        assert pantalla and pantalla.isVisible(), (ancho, alto, mensajes)
        assert pantalla.width() > 0 and pantalla.height() > 0, (ancho, alto)
        imagen = QQuickWindow.grabWindow(ventana)
        assert not imagen.isNull(), (ancho, alto, mensajes)
    ventana.setWidth(760)
    ventana.setHeight(600)
    app.processEvents()
    pantalla.setProperty("detallesMovil", False)
    nodos_visuales = [n for n in recorrer(pantalla) if n.objectName() == "nodoRazonamiento"]
    assert nodos_visuales
    primer_nodo = nodos_visuales[0]
    pos = primer_nodo.mapToScene(QPointF(24, 24))
    QTest.mouseClick(ventana, Qt.LeftButton, pos=QPoint(round(pos.x()), round(pos.y())))
    app.processEvents()
    assert pantalla.property("detallesMovil") is True
    hipotesis = puente.grafo["hipotesis"][0]
    pantalla.setProperty("seleccionado", hipotesis)
    app.processEvents()
    assert hipotesis in pantalla.property("nodosResaltados")
    pantalla.setProperty("zoom", 1.3)
    app.processEvents()
    assert pantalla.property("zoom") == 1.3
    pantalla.setProperty("grafo", grafo_ejemplo)
    app.processEvents()
    ventana.setWidth(1080)
    ventana.setHeight(760)
    pantalla.setProperty("detallesMovil", False)
    app.processEvents()
    detalles = [n for n in recorrer(pantalla)
                if n.objectName() == "detalleRazonamiento" and n.isVisible()]
    assert len(detalles) == 1, (len(detalles), mensajes)
    panel = detalles[0]
    esperados = {
        "observacion": ("Descripción", "Pregunta asociada"),
        "regla": ("Descripción", "Condiciones verificadas", "Conclusión"),
        "derivado": ("Explicación", "Reglas que lo generaron"),
        "hipotesis": ("Explicación", "Soportes registrados"),
    }
    exclusivos = {"Pregunta asociada", "Condiciones verificadas", "Conclusión",
                  "Reglas que lo generaron", "Soportes registrados"}
    tipos = {n["tipo"] for n in grafo_ejemplo["nodos"]}
    assert tipos == set(esperados), tipos
    for tipo, titulos in esperados.items():
        nodo_dato = next(n for n in grafo_ejemplo["nodos"] if n["tipo"] == tipo)
        pantalla.setProperty("seleccionado", nodo_dato["id"])
        app.processEvents()
        textos = [item.property("text") for item in recorrer(panel)
                  if item.isVisible() and isinstance(item.property("text"), str)]
        assert nodo_dato["etiqueta"] in textos, (tipo, textos)
        if tipo == "observacion":
            assert nodo_dato["estado"] in textos, (tipo, textos)
            assert nodo_dato["descripcion"] in textos, (tipo, textos)
            assert nodo_dato["pregunta"] in textos, (tipo, textos)
        elif tipo == "regla":
            assert nodo_dato["referencia"] in textos, (tipo, textos)
        else:
            assert nodo_dato["detalle"] in textos, (tipo, textos)
        for titulo in titulos:
            assert titulo in textos, (tipo, titulo, textos)
        assert not ((exclusivos - set(titulos)) & set(textos)), (tipo, textos)
        assert not any("Reglas no activadas:" in t or "Preguntas no formuladas:" in t
                       or t in ("Leyenda de nodos", "Mostrar lista", "Ocultar lista")
                       for t in textos), (tipo, textos)
    nombres = {n["etiqueta"] for n in grafo_ejemplo["nodos"]}
    nodos_visuales = [n for n in recorrer(pantalla) if n.objectName() == "nodoRazonamiento"]
    assert len(nodos_visuales) == len(grafo_ejemplo["nodos"])
    for nodo in nodos_visuales:
        pendientes = list(nodo.childItems())
        while pendientes:
            item = pendientes.pop()
            pendientes.extend(item.childItems())
            texto = item.property("text")
            if not item.isVisible() or not isinstance(texto, str) or not texto:
                continue
            pos = item.mapToItem(nodo, QPointF(0, 0))
            assert pos.x() >= -1 and pos.y() >= -1, (texto, pos)
            assert pos.x() + item.width() <= nodo.width() + 1, (texto, pos.x(), item.width(), nodo.width())
            assert pos.y() + item.height() <= nodo.height() + 1, (texto, pos.y(), item.height(), nodo.height())
            if texto in nombres:
                assert item.property("truncated") is not True, (
                    texto, item.width(), item.height(), item.implicitHeight(),
                    item.property("lineCount"), item.property("maximumLineCount"), nodo.height())
    puente.volverAResultados()
assert puente.pantalla == "resultados" and puente.resultado == resultado
print(json.dumps({"errores": [m for m in mensajes if "Error" in m or "ReferenceError" in m],
                  "polishLoops": sum("polish() loop" in m for m in mensajes),
                  "nodos": len(puente.grafo["nodos"])}))
ventana.close()
'''


@unittest.skipUnless(QT_DISPONIBLE, "PySide6 no está instalado")
class PruebasGrafoQt(unittest.TestCase):
    def test_pantalla_en_tres_tamanos_sin_bucle(self):
        plataformas = ("offscreen", "windows") if sys.platform == "win32" else ("offscreen",)
        for plataforma in plataformas:
            with self.subTest(plataforma=plataforma):
                entorno = os.environ.copy()
                entorno["QT_QPA_PLATFORM"] = plataforma
                proceso = subprocess.run(
                    [sys.executable, "-c", PRUEBA, str(RAIZ)], cwd=RAIZ, env=entorno,
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=25,
                )
                self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
                datos = json.loads(proceso.stdout.strip().splitlines()[-1])
                self.assertEqual(datos["errores"], [], datos)
                self.assertEqual(datos["polishLoops"], 0, datos)
                self.assertGreater(datos["nodos"], 0)
