"""Pruebas del encadenamiento directo y de la interfaz del primer avance."""

import io
import os
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.consola import mostrar_resultado, preguntar_sintomas  # noqa: E402
from diagnostico_pc.hechos import EstadoHecho  # noqa: E402
from diagnostico_pc.modelo_a import ModeloA  # noqa: E402


class PruebasModeloA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo = ModeloA.desde_directorio(RAIZ / "data" / "conocimiento")

    def test_encadenamiento_directo_registra_dos_reglas_de_una_hipotesis(self):
        resultado = self.modelo.evaluar(
            {"s_temperatura_alta": "verdadero", "s_apagado_bajo_carga": "verdadero"}
        )
        self.assertEqual(resultado.principal.id, "d_sobrecalentamiento")
        self.assertEqual(resultado.principal.especificidad, 2)
        self.assertEqual(
            {regla.id for regla in resultado.principal.reglas},
            {"r_temperatura_medida", "r_temperatura_apagado"},
        )
        self.assertEqual(resultado.memoria.hechos["s_ventilador_ruidoso"], EstadoHecho.DESCONOCIDO)
        self.assertEqual(len(resultado.memoria.conclusiones), 1)

    def test_condicion_falsa_exige_observacion_explicita(self):
        incompleto = self.modelo.evaluar({"s_so_no_inicia": "verdadero"})
        self.assertIsNone(incompleto.principal)
        self.assertEqual(incompleto.memoria.hechos["s_unidad_no_detectada"], EstadoHecho.DESCONOCIDO)
        confirmado = self.modelo.evaluar(
            {"s_so_no_inicia": "verdadero", "s_unidad_no_detectada": "falso"}
        )
        self.assertEqual(confirmado.principal.id, "d_arranque_so")
        self.assertIn("r_so_no_inicia_unidad_presente", confirmado.memoria.reglas_activadas)

    def test_sin_diagnostico_con_datos_ausentes_o_no_concluyentes(self):
        vacio = self.modelo.evaluar({})
        self.assertIsNone(vacio.principal)
        self.assertIn("No se aportaron", vacio.explicacion_sin_conclusion)
        no_concluyente = self.modelo.evaluar({"s_apagado_bajo_carga": "verdadero"})
        self.assertIsNone(no_concluyente.principal)
        self.assertIn("Ninguna regla", no_concluyente.explicacion_sin_conclusion)

    def test_varias_hipotesis_y_explicacion_completa(self):
        resultado = self.modelo.evaluar(
            {"s_artefactos_video": "verdadero", "s_pantalla_azul": "verdadero"}
        )
        self.assertEqual(resultado.principal.id, "d_subsistema_video")
        self.assertEqual([d.id for d in resultado.alternativos], ["d_error_critico_so"])
        salida = io.StringIO()
        mostrar_resultado(resultado, salida)
        texto = salida.getvalue()
        self.assertIn("r_video_artefactos_error", texto)
        self.assertIn("r_so_error_critico", texto)
        self.assertIn("Artefactos de video: verdadero", texto)
        self.assertIn("Recomendaciones:", texto)
        self.assertIn("no por probabilidad", texto)

    def test_empate_se_resuelve_por_id_y_no_por_numero_de_reglas(self):
        resultado = self.modelo.evaluar(
            {"s_error_prueba_ram": "verdadero", "s_artefactos_video": "verdadero"}
        )
        self.assertEqual(resultado.principal.id, "d_memoria_ram")
        self.assertEqual([d.id for d in resultado.alternativos], ["d_subsistema_video"])

    def test_interaccion_pregunta_todos_los_sintomas_y_acepta_desconocido(self):
        sintomas = [h for h in self.modelo.hechos.values() if h["tipo"] == "sintoma"]
        entradas = ["s" if h["id"] == "s_pitidos_ram_post" else "" for h in sintomas]
        respuestas = preguntar_sintomas(
            self.modelo, io.StringIO("\n".join(entradas) + "\n"), io.StringIO()
        )
        self.assertEqual(len(respuestas), len(sintomas))
        self.assertEqual(respuestas["s_pitidos_ram_post"], "verdadero")
        self.assertEqual(self.modelo.evaluar(respuestas).principal.id, "d_memoria_ram")

    def test_consola_en_subproceso_con_ejemplos(self):
        for archivo, frase in (
            ("ram.json", "Posible problema de memoria RAM"),
            ("sin_conclusion.json", "Sin diagnóstico concluyente"),
        ):
            with self.subTest(archivo=archivo):
                proceso = subprocess.run(
                    [sys.executable, str(RAIZ / "diagnosticar.py"), "--respuestas", str(RAIZ / "ejemplos" / archivo)],
                    cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=False,
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                )
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertIn(frase, proceso.stdout)

    def test_consola_interactiva_completa(self):
        sintomas = [h for h in self.modelo.hechos.values() if h["tipo"] == "sintoma"]
        respuestas = "\n".join(
            "s" if hecho["id"] == "s_pitidos_ram_post" else "?" for hecho in sintomas
        ) + "\n"
        proceso = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py")],
            cwd=RAIZ, input=respuestas, capture_output=True, text=True,
            encoding="utf-8", check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("20/20", proceso.stdout)
        self.assertIn("Posible problema de memoria RAM", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
