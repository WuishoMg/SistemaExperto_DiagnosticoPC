"""Auditoría independiente de reglas y recorridos; no usa los casos finales."""

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.gestor_preguntas import GestorPreguntas  # noqa: E402
from diagnostico_pc.modelo_a import ModeloA  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible as Respuesta, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import cargar_rutas  # noqa: E402

S, N, D = Respuesta.SI, Respuesta.NO, Respuesta.NO_ESTOY_SEGURO


def contexto_regla(regla_id):
    if regla_id == "r_pantalla_externa_tras_imagen_transitoria":
        return "video", {"p07": S, "p32": S, "p08": S}
    if regla_id.startswith("r_red_intermitente_"):
        return "conectividad", {"p18": S, "p33": S, "p36": S}
    if regla_id == "r_red_pagina_fallida_local":
        return "conectividad", {"p18": S, "p33": N, "p34": S, "p37": S}
    if regla_id.startswith("r_alimentacion"):
        return "alimentacion", {"p02": N, "p03": N}
    if regla_id.startswith("r_inicio_"):
        return "alimentacion", {"p02": S, "p03": S, "p07": N}
    if regla_id.startswith("r_ram"):
        return "video", {"p07": N, "p02": S, "p03": S, "p08": N}
    if regla_id == "r_pantalla_externa":
        return "video", {"p07": N, "p02": S, "p03": S, "p08": S}
    if regla_id.startswith("r_video_artefactos"):
        return "sistema", {"p16": S, "p17": S, "p09": S}
    if regla_id == "r_video_sin_salida":
        return "video", {"p07": N, "p02": S, "p03": S, "p08": N}
    if regla_id.startswith("r_almacenamiento") or (
        regla_id.startswith("r_so_") and regla_id != "r_so_error_critico"
    ):
        return "sistema", {"p16": N, "p06": N, "p26": S, "p12": S,
                           "p10": S, "p17": N, "p11": S}
    if regla_id == "r_so_error_critico":
        return "sistema", {"p16": S, "p17": S, "p09": N, "p11": N}
    if regla_id.startswith(("r_temperatura", "r_indicios")):
        return "temperatura", {"p30": S, "p14": S, "p15": S, "p13": S}
    if regla_id == "r_red_cable_desconectado":
        return "conectividad", {"p18": N, "p25": N, "p29": S, "p31": S, "p19": S}
    if regla_id.startswith(("r_wifi", "r_red")):
        return "conectividad", {"p18": N, "p25": S, "p20": N, "p19": S}
    if regla_id.startswith(("r_lentitud", "r_congelamiento")):
        return "lentitud", {"p21": S, "p27": S, "p22": S, "p23": S, "p24": S, "p28": S}
    raise AssertionError(f"Falta contexto de auditoría para {regla_id}")


class AuditoriaAvance1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo = ModeloA.desde_directorio(RAIZ / "data" / "conocimiento")
        cls.preguntas = cargar_preguntas(
            RAIZ / "data" / "interfaz" / "preguntas.json", cls.modelo.sintomas
        )
        cls.rutas = cargar_rutas(RAIZ / "data" / "interfaz" / "rutas.json", cls.preguntas)
        cls.reglas = json.loads(
            (RAIZ / "data" / "conocimiento" / "reglas.json").read_text(encoding="utf-8")
        )["reglas"]
        cls.por_hecho = {pregunta.hecho: pregunta for pregunta in cls.preguntas}

    def test_cada_condicion_directa_exige_observacion_explicita(self):
        self.assertEqual(len(self.reglas), 42)
        for regla in self.reglas:
            condiciones = {c["hecho"]: c["estado"] for c in regla["condiciones"]}
            with self.subTest(regla=regla["id"], caso="positiva"):
                self.assertIn(regla["id"], self.modelo.evaluar(condiciones).memoria.reglas_activadas)
            for hecho, estado in condiciones.items():
                for sustituto in (None, "desconocido", "falso" if estado == "verdadero" else "verdadero"):
                    cambio = dict(condiciones)
                    if sustituto is None:
                        del cambio[hecho]
                    else:
                        cambio[hecho] = sustituto
                    with self.subTest(regla=regla["id"], hecho=hecho, sustituto=sustituto):
                        self.assertNotIn(regla["id"], self.modelo.evaluar(cambio).memoria.reglas_activadas)

    def test_todas_las_reglas_y_diagnosticos_son_alcanzables_por_cuestionario(self):
        alcanzadas = set()
        diagnosticos = set()
        for regla in self.reglas:
            categoria, respuestas = contexto_regla(regla["id"])
            for condicion in regla["condiciones"]:
                pregunta = self.por_hecho[condicion["hecho"]]
                respuestas[pregunta.id] = (
                    S if pregunta.estado_si.value == condicion["estado"] else N
                )
            gestor = GestorPreguntas(self.preguntas, self.rutas, categoria)
            visitadas = []
            while (pregunta := gestor.siguiente()) is not None:
                self.assertNotIn(pregunta.id, visitadas)
                visitadas.append(pregunta.id)
                gestor.responder(pregunta.id, respuestas.get(pregunta.id, D))
            resultado = self.modelo.evaluar(gestor.observaciones)
            with self.subTest(regla=regla["id"]):
                self.assertIn(regla["id"], resultado.memoria.reglas_activadas, visitadas)
                self.assertFalse(gestor.contradicciones)
            alcanzadas.update(resultado.memoria.reglas_activadas)
            diagnosticos.update(resultado.memoria.conclusiones)
        self.assertEqual(alcanzadas, {r["id"] for r in self.reglas})
        self.assertEqual(diagnosticos, set(self.modelo.diagnosticos))
        self.assertEqual(len(diagnosticos), 18)

    def test_exploracion_acotada_de_bifurcaciones_termina(self):
        bifurcaciones = {"p02", "p07", "p16", "p21", "p18", "p30", "p25"}
        for categoria in self.rutas.categorias:
            gestor = GestorPreguntas(self.preguntas, self.rutas, categoria.id)
            terminales = 0
            def explorar():
                nonlocal terminales
                pregunta = gestor.siguiente()
                if pregunta is None:
                    self.assertIsNotNone(gestor.estado_final)
                    self.assertFalse(gestor.contradicciones)
                    terminales += 1
                    return
                self.assertLess(len(gestor.historial), len(self.preguntas))
                opciones = tuple(Respuesta) if pregunta.id in bifurcaciones else (D,)
                for opcion in opciones:
                    gestor.responder(pregunta.id, opcion)
                    explorar()
                    gestor.volver()
            explorar()
            self.assertGreater(terminales, 0)


if __name__ == "__main__":
    unittest.main()
