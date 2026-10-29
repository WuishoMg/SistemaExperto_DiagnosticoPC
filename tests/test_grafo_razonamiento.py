"""Grafo visual de C con ejemplos de desarrollo; nunca abre la reserva final."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.gestor_preguntas import RespuestaRegistrada  # noqa: E402
from diagnostico_pc.gui.reasoning_graph import construir_grafo  # noqa: E402
from diagnostico_pc.gui.serialization import serializar_resultado  # noqa: E402
from diagnostico_pc.gui.session import SesionGrafica  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible  # noqa: E402


class PruebasGrafo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sesion = SesionGrafica(RAIZ)
        cls.modelo = cls.sesion.modelo_c
        cls.preguntas = {p.hecho: p for p in cls.sesion.preguntas}
        cls.por_id = {p.id: p for p in cls.sesion.preguntas}

    def grafo(self, respuestas):
        resultado = serializar_resultado(self.modelo.evaluar(respuestas))
        historial = []
        for hecho, estado in respuestas.items():
            pregunta = self.preguntas[hecho]
            if estado == "desconocido":
                visible = RespuestaVisible.NO_ESTOY_SEGURO
            elif pregunta.estado_si.value == estado:
                visible = RespuestaVisible.SI
            else:
                visible = RespuestaVisible.NO
            historial.append(RespuestaRegistrada(pregunta.id, visible))
        return resultado, construir_grafo(resultado, historial, self.por_id,
                                          self.modelo.hechos, self.modelo.reglas)

    def test_cadena_y_orden_c_proceden_de_trazas(self):
        respuestas = json.loads((RAIZ / "ejemplos/arranque_multinivel_b.json").read_text(encoding="utf-8"))
        resultado, grafo = self.grafo(respuestas)
        nodos = {n["id"]: n for n in grafo["nodos"]}
        aristas = {(a["origen"], a["destino"]) for a in grafo["conexiones"]}
        self.assertEqual(grafo["hipotesis"], ["d:" + resultado["principal"]["id"]])
        self.assertEqual({n["referencia"] for n in grafo["nodos"] if n["tipo"] == "regla"},
                         {t["reglaId"] for t in resultado["trazas"]})
        for traza in resultado["trazas"]:
            regla = "r:" + traza["reglaId"]
            destino = ("h:" if traza["conclusionTipo"] == "hecho" else "d:") + traza["conclusionId"]
            self.assertIn((regla, destino), aristas)
            for condicion in traza["condiciones"]:
                origen = ("o:" if condicion["hechoId"] in self.modelo.sintomas else "h:") + condicion["hechoId"]
                self.assertIn((origen, regla), aristas)
        self.assertTrue(any(n["tipo"] == "derivado" for n in grafo["nodos"]))
        self.assertTrue(all(a["origen"] in nodos and a["destino"] in nodos for a in grafo["conexiones"]))
        self.assertTrue(any(s["tipo"] == "derivado" for s in grafo["secciones"]))
        self.assertTrue(all(nodos[a["origen"]]["y"] + nodos[a["origen"]]["alto"]
                            < nodos[a["destino"]]["y"] for a in grafo["conexiones"]))
        for traza in resultado["trazas"]:
            regla = nodos["r:" + traza["reglaId"]]
            self.assertEqual(regla["conclusion"]["id"], traza["conclusionId"])
            self.assertEqual(regla["conclusion"]["tipo"], traza["conclusionTipo"])
        for nodo in nodos.values():
            if nodo["tipo"] == "derivado":
                self.assertEqual(set(nodo["generadoras"]),
                                 {a["origen"].removeprefix("r:") for a in grafo["conexiones"]
                                  if a["destino"] == nodo["id"]})

    def test_alternativas_comparten_soportes_y_prioridad_c(self):
        respuestas = json.loads((RAIZ / "ejemplos/hipotesis_termicas_c.json").read_text(encoding="utf-8"))
        resultado, grafo = self.grafo(respuestas)
        esperadas = [resultado["principal"], *resultado["alternativas"]]
        self.assertEqual(grafo["hipotesis"], ["d:" + h["id"] for h in esperadas])
        self.assertGreater(len(set(grafo["soportes"][grafo["hipotesis"][0]]) &
                               set(grafo["soportes"][grafo["hipotesis"][1]])), 0)
        self.assertEqual(grafo["explicacionPrioridad"], resultado["explicacionPrioridad"])
        self.assertEqual([s["tipo"] for s in grafo["secciones"][-2:]],
                         ["principal", "alternativas"])

    def test_desconocido_y_sin_hipotesis_no_inventan_conexion(self):
        resultado, grafo = self.grafo({"s_temperatura_alta": "desconocido"})
        self.assertIsNone(resultado["principal"])
        self.assertEqual(grafo["hipotesis"], [])
        self.assertEqual(grafo["conexiones"], [])
        nodo = next(n for n in grafo["nodos"] if n["id"] == "o:s_temperatura_alta")
        self.assertEqual(nodo["estado"], "desconocido")
        self.assertEqual(len(grafo["sinPreguntar"]), len(self.modelo.sintomas) - 1)

    def test_falso_es_soporte_solo_si_consta_en_condicion(self):
        respuestas = {"s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
                      "s_sin_dispositivo_arranque": "verdadero", "s_unidad_no_detectada": "falso"}
        resultado, grafo = self.grafo(respuestas)
        aristas = [a for a in grafo["conexiones"] if a["origen"] == "o:s_unidad_no_detectada"]
        esperadas = {"r:" + t["reglaId"] for t in resultado["trazas"]
                     if any(c["hechoId"] == "s_unidad_no_detectada" and c["estado"] == "falso"
                            for c in t["condiciones"])}
        self.assertEqual({a["destino"] for a in aristas}, esperadas)
        self.assertTrue(all(a["estado"] == "falso" for a in aristas))

    def test_traza_incompleta_omite_relacion_y_da_aviso(self):
        resultado, _ = self.grafo({"s_temperatura_alta": "verdadero", "s_calor_percibido": "verdadero"})
        alterado = json.loads(json.dumps(resultado))
        alterado["trazas"][0]["condiciones"].append({"hechoId": "s_ausente", "estado": "verdadero"})
        grafo = construir_grafo(alterado, [], self.por_id, self.modelo.hechos, self.modelo.reglas)
        self.assertTrue(grafo["avisos"])
        self.assertFalse(any(a["origen"] == "h:s_ausente" for a in grafo["conexiones"]))

    def test_abrir_y_cerrar_no_vuelve_a_inferir(self):
        sesion = SesionGrafica(RAIZ)
        sesion.elegir_categoria("temperatura")
        sesion.responder(sesion.estado()["preguntaActual"]["id"], "no_estoy_seguro")
        sesion.ver_resultado()
        resultado = sesion.resultado
        historial = list(sesion.gestor.historial)
        with patch.object(sesion.modelo_c, "evaluar", side_effect=AssertionError("inferencia repetida")):
            sesion.ver_razonamiento()
            self.assertEqual(sesion.pantalla, "razonamiento")
            self.assertTrue(sesion.grafo["nodos"])
            sesion.volver_a_resultados()
        self.assertIs(sesion.resultado, resultado)
        self.assertEqual(sesion.gestor.historial, historial)


if __name__ == "__main__":
    unittest.main()
