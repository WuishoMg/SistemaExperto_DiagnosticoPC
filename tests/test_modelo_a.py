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
from diagnostico_pc.preguntas import RespuestaVisible, cargar_preguntas  # noqa: E402


class PruebasModeloA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo = ModeloA.desde_directorio(RAIZ / "data" / "conocimiento")
        cls.preguntas = cargar_preguntas(
            RAIZ / "data" / "interfaz" / "preguntas.json", cls.modelo.sintomas
        )

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
        entradas = ["s" if p.hecho == "s_pitidos_ram_post" else "" for p in self.preguntas]
        salida = io.StringIO()
        respuestas = preguntar_sintomas(
            self.preguntas, io.StringIO("\n".join(entradas) + "\n"), salida
        )
        self.assertEqual(len(respuestas), len(self.preguntas))
        self.assertEqual(respuestas["s_pitidos_ram_post"], "verdadero")
        self.assertEqual(respuestas["s_error_prueba_ram"], "desconocido")
        self.assertIn("Ayuda:", salida.getvalue())
        self.assertIn("No estoy seguro", salida.getvalue())
        self.assertNotIn("s_pitidos_ram_post", salida.getvalue())
        self.assertEqual(self.modelo.evaluar(respuestas).principal.id, "d_memoria_ram")

    def test_todas_las_preguntas_tienen_mapeo_explicito_y_ayuda(self):
        invertidas = {
            "s_no_enciende", "s_sin_imagen", "s_unidad_no_detectada",
            "s_so_no_inicia", "s_sin_red", "s_wifi_deshabilitado",
        }
        self.assertEqual(len(self.preguntas), 20)
        self.assertEqual({p.hecho for p in self.preguntas}, self.modelo.sintomas)
        for pregunta in self.preguntas:
            with self.subTest(hecho=pregunta.hecho):
                self.assertTrue(pregunta.texto.startswith("¿"))
                self.assertTrue(pregunta.ayuda.strip())
                self.assertNotIn(pregunta.hecho, pregunta.texto)
                self.assertEqual(
                    pregunta.estado_para(RespuestaVisible.SI),
                    EstadoHecho.FALSO if pregunta.hecho in invertidas else EstadoHecho.VERDADERO,
                )
                self.assertEqual(
                    pregunta.estado_para(RespuestaVisible.NO),
                    EstadoHecho.VERDADERO if pregunta.hecho in invertidas else EstadoHecho.FALSO,
                )
                self.assertEqual(
                    pregunta.estado_para(RespuestaVisible.NO_ESTOY_SEGURO),
                    EstadoHecho.DESCONOCIDO,
                )

    def test_respuestas_invertidas_activan_las_reglas_existentes(self):
        seleccion = {"s_unidad_no_detectada": "Sí", "s_so_no_inicia": "No"}
        entradas = [seleccion.get(p.hecho, "No estoy seguro") for p in self.preguntas]
        respuestas = preguntar_sintomas(
            self.preguntas, io.StringIO("\n".join(entradas) + "\n"), io.StringIO()
        )
        self.assertEqual(respuestas["s_unidad_no_detectada"], "falso")
        self.assertEqual(respuestas["s_so_no_inicia"], "verdadero")
        resultado = self.modelo.evaluar(respuestas)
        self.assertEqual(resultado.principal.id, "d_arranque_so")
        self.assertIn("r_so_no_inicia_unidad_presente", resultado.memoria.reglas_activadas)

    def test_no_en_preguntas_de_encendido_conserva_polaridad(self):
        seleccion = {"s_no_enciende": "No", "s_led_encendido": "No"}
        entradas = [seleccion.get(p.hecho, "3") for p in self.preguntas]
        respuestas = preguntar_sintomas(
            self.preguntas, io.StringIO("\n".join(entradas) + "\n"), io.StringIO()
        )
        self.assertEqual(respuestas["s_no_enciende"], "verdadero")
        self.assertEqual(respuestas["s_led_encendido"], "falso")
        self.assertEqual(self.modelo.evaluar(respuestas).principal.id, "d_ruta_alimentacion")

    def test_menu_numeros_y_letras_conservan_polaridad(self):
        ejemplos = {
            "s_led_encendido": {
                "1": "verdadero", "s": "verdadero",
                "2": "falso", "n": "falso",
                "3": "desconocido", "?": "desconocido",
            },
            "s_no_enciende": {
                "1": "falso", "s": "falso",
                "2": "verdadero", "n": "verdadero",
                "3": "desconocido", "?": "desconocido",
            },
        }
        for pregunta in self.preguntas:
            if pregunta.hecho not in ejemplos:
                continue
            for entrada, esperado in ejemplos[pregunta.hecho].items():
                with self.subTest(hecho=pregunta.hecho, entrada=entrada):
                    salida = io.StringIO()
                    respuestas = preguntar_sintomas(
                        (pregunta,), io.StringIO(entrada + "\n"), salida
                    )
                    self.assertEqual(respuestas[pregunta.hecho], esperado)
                    for opcion in ("1. Sí", "2. No", "3. No estoy seguro"):
                        self.assertIn(opcion, salida.getvalue())

    def test_consola_en_subproceso_con_ejemplos(self):
        for archivo, frases in (
            ("ram.json", ("Posible problema de memoria RAM", "r_ram_codigo_post", "r_ram_reinicio_post")),
            ("sin_conclusion.json", ("Sin diagnóstico concluyente", "Ninguna regla directa coincide")),
        ):
            with self.subTest(archivo=archivo):
                proceso = subprocess.run(
                    [sys.executable, str(RAIZ / "diagnosticar.py"), "--respuestas", str(RAIZ / "ejemplos" / archivo)],
                    cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=False,
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                )
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                for frase in frases:
                    self.assertIn(frase, proceso.stdout)

    def test_consola_interactiva_completa(self):
        respuestas = "\n".join(
            "1" if pregunta.hecho == "s_pitidos_ram_post" else "3" for pregunta in self.preguntas
        ) + "\n"
        proceso = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py")],
            cwd=RAIZ, input=respuestas, capture_output=True, text=True,
            encoding="utf-8", check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("20/20", proceso.stdout)
        self.assertIn("Ayuda:", proceso.stdout)
        self.assertNotIn("s_pitidos_ram_post", proceso.stdout)
        self.assertIn("Posible problema de memoria RAM", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
