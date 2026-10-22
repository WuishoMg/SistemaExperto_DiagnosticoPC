"""Pruebas funcionales del encadenamiento multinivel del Modelo B."""

import copy
import io
import os
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.conocimiento_b import leer_ampliacion  # noqa: E402
from diagnostico_pc.consola import mostrar_resultado_b  # noqa: E402
from diagnostico_pc.contratos import ModeloInferencia, ResultadoInferencia  # noqa: E402
from diagnostico_pc.gestor_preguntas import GestorPreguntas  # noqa: E402
from diagnostico_pc.hechos import EstadoHecho  # noqa: E402
from diagnostico_pc.modelo_b import ConflictoInferencia, ModeloB  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import cargar_rutas  # noqa: E402
from diagnostico_pc.selector import seleccionar_modelo  # noqa: E402
from diagnostico_pc.validacion import ErrorConocimiento, leer_documentos  # noqa: E402


class PruebasModeloB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = leer_documentos(RAIZ / "data" / "conocimiento")
        cls.ampliacion = leer_ampliacion(RAIZ / "data" / "conocimiento_avance2")
        cls.modelo = ModeloB(*cls.base, *cls.ampliacion)

    def test_contrato_selector_y_cadena_de_tres_niveles(self):
        modelo = seleccionar_modelo("B")
        self.assertIsInstance(modelo, ModeloInferencia)
        resultado = modelo.evaluar({
            "s_so_no_inicia": "verdadero",
            "s_post_completado": "verdadero",
            "s_unidad_no_detectada": "falso",
        })
        self.assertIsInstance(resultado, ResultadoInferencia)
        self.assertEqual(resultado.principal.id, "d_arranque_so")
        self.assertEqual(resultado.memoria.hechos["h_fallo_etapa_arranque"], EstadoHecho.VERDADERO)
        self.assertEqual(resultado.memoria.hechos["h_fallo_arranque_unidad_visible"], EstadoHecho.VERDADERO)
        self.assertEqual(
            [(traza.regla_id, traza.nivel) for traza in resultado.trazas if traza.regla_id.startswith("r_b_")],
            [("r_b_arranque_tras_post", 1), ("r_b_arranque_unidad_visible", 2), ("r_b_revision_arranque", 3)],
        )
        self.assertEqual(resultado.rondas, 3)
        self.assertEqual(len(resultado.memoria.reglas_activadas), len(set(resultado.memoria.reglas_activadas)))
        self.assertEqual(resultado, modelo.evaluar({
            "s_so_no_inicia": "verdadero",
            "s_post_completado": "verdadero",
            "s_unidad_no_detectada": "falso",
        }))

    def test_soportes_alternativos_y_explicacion_observada(self):
        resultado = self.modelo.evaluar({
            "s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
            "s_sin_dispositivo_arranque": "verdadero", "s_unidad_no_detectada": "falso",
        })
        soportes = [
            traza for traza in resultado.trazas
            if traza.conclusion_id == "h_fallo_etapa_arranque"
        ]
        self.assertEqual({t.regla_id for t in soportes}, {
            "r_b_arranque_tras_post", "r_b_mensaje_arranque",
        })
        salida = io.StringIO()
        mostrar_resultado_b(resultado, salida)
        texto = salida.getvalue()
        for fragmento in (
            "Nivel 1", "Nivel 2", "Nivel 3", "Soporte alternativo 1",
            "r_b_arranque_tras_post", "r_b_mensaje_arranque",
            "r_b_arranque_unidad_visible", "r_b_revision_arranque",
            "[observado]: falso", "[derivado]: verdadero",
            "Recomendaciones:",
        ):
            self.assertIn(fragmento, texto)
        self.assertNotIn("probabilidad", texto)

    def test_desconocido_no_activa_condicion_falsa_ni_cadena(self):
        incompleto = self.modelo.evaluar({
            "s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
        })
        self.assertEqual(incompleto.memoria.hechos["s_unidad_no_detectada"], EstadoHecho.DESCONOCIDO)
        self.assertEqual(incompleto.memoria.hechos["h_fallo_etapa_arranque"], EstadoHecho.VERDADERO)
        self.assertEqual(incompleto.memoria.hechos["h_fallo_arranque_unidad_visible"], EstadoHecho.DESCONOCIDO)
        self.assertIsNone(incompleto.principal)
        self.assertEqual(incompleto.rondas, 1)
        sin_post = self.modelo.evaluar({
            "s_so_no_inicia": "verdadero", "s_unidad_no_detectada": "falso",
        })
        self.assertEqual(sin_post.memoria.hechos["h_fallo_etapa_arranque"], EstadoHecho.DESCONOCIDO)
        self.assertFalse(any(traza.regla_id.startswith("r_b_") for traza in sin_post.trazas))

    def test_ciclo_entre_hechos_derivados_se_rechaza(self):
        reglas = copy.deepcopy(self.ampliacion[1])
        reglas["reglas"].append({
            "id": "r_b_ciclo", "condiciones": [
                {"hecho": "h_fallo_arranque_unidad_visible", "estado": "verdadero"}
            ],
            "conclusion": {"tipo": "hecho", "id": "h_fallo_etapa_arranque", "estado": "verdadero"},
            "explicacion": "Regla sintética de prueba para detectar un ciclo.",
        })
        with self.assertRaisesRegex(ErrorConocimiento, "Ciclo entre hechos derivados"):
            ModeloB(*self.base, self.ampliacion[0], reglas)

    def test_conclusiones_contradictorias_se_detectan(self):
        reglas = copy.deepcopy(self.ampliacion[1])
        reglas["reglas"].append({
            "id": "r_b_conflicto", "condiciones": [
                {"hecho": "s_pantalla_azul", "estado": "verdadero"}
            ],
            "conclusion": {"tipo": "hecho", "id": "h_fallo_etapa_arranque", "estado": "falso"},
            "explicacion": "Regla sintética de prueba para detectar oposición.",
        })
        modelo = ModeloB(*self.base, self.ampliacion[0], reglas)
        with self.assertRaisesRegex(ConflictoInferencia, "Conclusiones contradictorias"):
            modelo.evaluar({
                "s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
                "s_pantalla_azul": "verdadero",
            })

    def test_siete_rutas_entregan_hechos_sin_inferir_en_cuestionario(self):
        preguntas = cargar_preguntas(RAIZ / "data" / "interfaz" / "preguntas.json", self.modelo.sintomas)
        rutas = cargar_rutas(RAIZ / "data" / "interfaz" / "rutas.json", preguntas)
        self.assertEqual(len(rutas.categorias), 7)
        for categoria in rutas.categorias:
            with self.subTest(categoria=categoria.id):
                gestor = GestorPreguntas(preguntas, rutas, categoria.id)
                pasos = 0
                while (pregunta := gestor.siguiente()) is not None:
                    gestor.responder(pregunta.id, RespuestaVisible.NO_ESTOY_SEGURO)
                    pasos += 1
                    self.assertLessEqual(pasos, len(preguntas))
                resultado = self.modelo.evaluar(gestor.observaciones)
                self.assertIsNone(resultado.principal)
                self.assertEqual(resultado.rondas, 0)
                self.assertTrue(all(
                    estado == EstadoHecho.DESCONOCIDO
                    for estado in resultado.memoria.hechos.values()
                ))

    def test_siete_rutas_con_respuestas_reales_llegan_a_b(self):
        preguntas = cargar_preguntas(RAIZ / "data" / "interfaz" / "preguntas.json", self.modelo.sintomas)
        rutas = cargar_rutas(RAIZ / "data" / "interfaz" / "rutas.json", preguntas)
        S, N, D = RespuestaVisible.SI, RespuestaVisible.NO, RespuestaVisible.NO_ESTOY_SEGURO
        casos = (
            ("alimentacion", {"p02": N, "p03": N}, "d_ruta_alimentacion"),
            ("lentitud", {"p21": S, "p27": N, "p22": S, "p23": N, "p24": N, "p28": N}, "d_espacio_insuficiente"),
            ("video", {"p07": N, "p02": S, "p03": S, "p08": S}, "d_pantalla_principal"),
            ("sistema", {"p16": N, "p06": N, "p26": S, "p12": S, "p10": N, "p17": N, "p11": D}, "d_deteccion_almacenamiento"),
            ("temperatura", {"p30": S, "p14": S, "p15": S, "p13": S}, "d_sobrecalentamiento"),
            ("conectividad", {"p18": N, "p25": S, "p20": N, "p19": S}, "d_wifi_inhabilitado"),
            ("general", {"p02": N, "p03": N}, "d_ruta_alimentacion"),
        )
        for categoria, respuestas, esperado in casos:
            with self.subTest(categoria=categoria):
                gestor = GestorPreguntas(preguntas, rutas, categoria)
                pasos = 0
                while (pregunta := gestor.siguiente()) is not None:
                    gestor.responder(pregunta.id, respuestas.get(pregunta.id, D))
                    pasos += 1
                    self.assertLessEqual(pasos, len(preguntas))
                resultado = self.modelo.evaluar(gestor.observaciones)
                ids = {d.id for d in (resultado.principal, *resultado.alternativos) if d is not None}
                self.assertIn(esperado, ids)

    def test_cli_b_acepta_ejemplos(self):
        entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        for archivo, esperado in (
            ("ram.json", "Posible problema de memoria RAM"),
            ("sin_conclusion.json", "Sin diagnóstico concluyente"),
        ):
            with self.subTest(archivo=archivo):
                proceso = subprocess.run(
                    [sys.executable, str(RAIZ / "diagnosticar.py"), "--modelo", "B",
                     "--respuestas", str(RAIZ / "ejemplos" / archivo)],
                    cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=False,
                    env=entorno,
                )
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertIn("Resultado del Modelo B", proceso.stdout)
                self.assertIn(esperado, proceso.stdout)

        cadena = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py"), "--modelo", "B",
             "--respuestas", str(RAIZ / "ejemplos" / "arranque_multinivel_b.json")],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=False,
            env=entorno,
        )
        self.assertEqual(cadena.returncode, 0, cadena.stderr)
        self.assertIn("Posible problema de configuración o archivos de arranque", cadena.stdout)
        self.assertIn("r_b_revision_arranque", cadena.stdout)
        self.assertIn("Soporte alternativo 2", cadena.stdout)

    def test_cli_b_usa_cuestionario_condicional(self):
        proceso = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py"), "--modelo", "B"],
            cwd=RAIZ, input="1\n2\n2\n3\n\n", capture_output=True, text=True,
            encoding="utf-8", check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("¿Qué problema presenta tu computadora?", proceso.stdout)
        self.assertIn("Resultado del Modelo B", proceso.stdout)
        self.assertIn("Posible problema en la ruta de alimentación", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
