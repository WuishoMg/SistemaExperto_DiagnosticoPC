"""Regresión de la arquitectura de la etapa 1 del Avance 2."""

import io
import os
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.contratos import ModeloInferencia, ResultadoInferencia  # noqa: E402
from diagnostico_pc.consola import mostrar_resultado  # noqa: E402
from diagnostico_pc.gestor_preguntas import GestorPreguntas  # noqa: E402
from diagnostico_pc.hechos import EstadoHecho  # noqa: E402
from diagnostico_pc.modelo_a import ModeloA, ResultadoModeloA  # noqa: E402
from diagnostico_pc.modelo_b import ModeloB  # noqa: E402
from diagnostico_pc.modelo_c import ModeloC  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import cargar_rutas  # noqa: E402
from diagnostico_pc.selector import (  # noqa: E402
    MODELO_PREDETERMINADO, MODELOS, seleccionar_modelo,
)


class PruebasArquitecturaAvance2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directorio = RAIZ / "data" / "conocimiento"
        cls.directo = ModeloA.desde_directorio(cls.directorio)

    def test_contrato_comun_acepta_modelo_y_resultado_existentes(self):
        self.assertIsInstance(self.directo, ModeloInferencia)
        resultado = self.directo.evaluar({"s_error_prueba_ram": "verdadero"})
        self.assertIsInstance(resultado, ResultadoInferencia)
        self.assertIsInstance(resultado, ResultadoModeloA)
        self.assertEqual(resultado.principal.id, "d_memoria_ram")
        self.assertIn("r_ram_prueba", resultado.memoria.reglas_activadas)

    def test_selector_reconoce_tres_modelos_y_a_es_predeterminado(self):
        self.assertEqual(MODELOS, ("A", "B", "C"))
        self.assertEqual(MODELO_PREDETERMINADO, "A")
        self.assertIsInstance(seleccionar_modelo(directorio_conocimiento=self.directorio), ModeloA)
        self.assertIsInstance(seleccionar_modelo("a", self.directorio), ModeloA)
        self.assertIsInstance(seleccionar_modelo("B", self.directorio), ModeloB)
        self.assertIsInstance(seleccionar_modelo("C", self.directorio), ModeloC)
        with self.assertRaisesRegex(ValueError, "Modelo desconocido"):
            seleccionar_modelo("D", self.directorio)

    def test_selector_preserva_resultado_y_presentacion_de_a(self):
        seleccionado = seleccionar_modelo("A", self.directorio)
        for observaciones in (
            {},
            {"s_so_no_inicia": "verdadero"},
            {"s_error_prueba_ram": "verdadero", "s_pitidos_ram_post": "verdadero"},
            {"s_artefactos_video": "verdadero", "s_pantalla_azul": "verdadero"},
        ):
            with self.subTest(observaciones=observaciones):
                anterior = self.directo.evaluar(observaciones)
                actual = seleccionado.evaluar(observaciones)
                self.assertEqual(actual, anterior)
                salida_anterior, salida_actual = io.StringIO(), io.StringIO()
                mostrar_resultado(anterior, salida_anterior)
                mostrar_resultado(actual, salida_actual)
                self.assertEqual(salida_actual.getvalue(), salida_anterior.getvalue())

    def test_cuestionario_entrega_hechos_trivalentes_al_selector(self):
        preguntas = cargar_preguntas(RAIZ / "data" / "interfaz" / "preguntas.json", self.directo.sintomas)
        rutas = cargar_rutas(RAIZ / "data" / "interfaz" / "rutas.json", preguntas)
        self.assertEqual(len(rutas.categorias), 7)
        for categoria in rutas.categorias:
            with self.subTest(categoria=categoria.id):
                gestor = GestorPreguntas(preguntas, rutas, categoria.id)
                self.assertEqual(set(gestor.observaciones), self.directo.sintomas)
                self.assertTrue(all(estado == EstadoHecho.DESCONOCIDO for estado in gestor.hechos.values()))
                pregunta = gestor.siguiente()
                gestor.responder(pregunta.id, RespuestaVisible.NO_ESTOY_SEGURO)
                self.assertEqual(gestor.hechos[pregunta.hecho], EstadoHecho.DESCONOCIDO)
                self.assertEqual(
                    seleccionar_modelo("A", self.directorio).evaluar(gestor.observaciones),
                    self.directo.evaluar(gestor.observaciones),
                )

    def test_cli_predeterminado_y_a_explicito_conservan_salida(self):
        entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        for archivo in ("ram.json", "sin_conclusion.json"):
            with self.subTest(archivo=archivo):
                ruta = RAIZ / "ejemplos" / archivo
                base = [sys.executable, str(RAIZ / "diagnosticar.py"), "--respuestas", str(ruta)]
                predeterminado = subprocess.run(base, cwd=RAIZ, capture_output=True, env=entorno, check=False)
                explicito = subprocess.run(base + ["--modelo", "A"], cwd=RAIZ, capture_output=True, env=entorno, check=False)
                self.assertEqual(predeterminado.returncode, 0, predeterminado.stderr)
                self.assertEqual(explicito.returncode, 0, explicito.stderr)
                self.assertEqual(predeterminado.stdout, explicito.stdout)
                self.assertEqual(predeterminado.stderr, explicito.stderr)

    def test_cli_c_esta_disponible(self):
        proceso = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py"), "--modelo", "C",
             "--respuestas", str(RAIZ / "ejemplos" / "ram.json")],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("Resultado del Modelo C", proceso.stdout)
        self.assertIn("Posible problema de memoria RAM", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
