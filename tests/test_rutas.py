"""Recorridos completos y decisiones de las siete rutas del Avance 1."""

import copy
import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.consola import mostrar_resultado, preguntar_condicional  # noqa: E402
from diagnostico_pc.gestor_preguntas import GestorPreguntas  # noqa: E402
from diagnostico_pc.hechos import EstadoHecho  # noqa: E402
from diagnostico_pc.modelo_a import ModeloA  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible as Respuesta, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import ErrorRutas, cargar_rutas, validar_rutas  # noqa: E402

S, N, D = Respuesta.SI, Respuesta.NO, Respuesta.NO_ESTOY_SEGURO


class PruebasRutas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo = ModeloA.desde_directorio(RAIZ / "data" / "conocimiento")
        cls.preguntas = cargar_preguntas(RAIZ / "data" / "interfaz" / "preguntas.json", cls.modelo.sintomas)
        cls.documento = json.loads((RAIZ / "data" / "interfaz" / "rutas.json").read_text(encoding="utf-8"))
        cls.rutas = cargar_rutas(RAIZ / "data" / "interfaz" / "rutas.json", cls.preguntas)

    def recorrer(self, categoria, respuestas):
        gestor = GestorPreguntas(self.preguntas, self.rutas, categoria)
        visitadas = []
        while (pregunta := gestor.siguiente()) is not None:
            self.assertNotIn(pregunta.id, visitadas)
            visitadas.append(pregunta.id)
            self.assertLessEqual(len(visitadas), len(self.preguntas))
            gestor.responder(pregunta.id, respuestas.get(pregunta.id, D))
            self.assertEqual(gestor.categoria_actual, categoria)
            self.assertFalse(gestor.contradicciones)
        self.assertIsNotNone(gestor.estado_final)
        resultado = self.modelo.evaluar(gestor.observaciones)
        diagnosticos = {d.id for d in (resultado.principal, *resultado.alternativos) if d is not None}
        return gestor, visitadas, diagnosticos

    def test_cada_categoria_empieza_con_su_problema(self):
        esperados = {
            "alimentacion": "p02", "lentitud": "p21", "video": "p07",
            "sistema": "p16", "temperatura": "p30", "conectividad": "p18",
            "general": "p02",
        }
        self.assertEqual({c.id: c.inicio for c in self.rutas.categorias}, esperados)
        self.assertEqual(len(self.preguntas), 36)

    def test_tres_recorridos_completos_por_ruta(self):
        casos = [
            ("A sin señales", "alimentacion", {"p02": N, "p03": N}, "d_ruta_alimentacion"),
            ("A energía sin imagen", "alimentacion", {"p02": S, "p03": S, "p07": N}, "d_revision_inicio_energia"),
            ("A incierto", "alimentacion", {"p02": D, "p03": D}, None),
            ("L espacio", "lentitud", {"p21": S, "p27": N, "p22": S, "p23": N, "p24": N, "p28": N}, "d_espacio_insuficiente"),
            ("L memoria", "lentitud", {"p21": N, "p27": S, "p22": N, "p23": S, "p24": N, "p28": N, "p11": N, "p05": D}, "d_presion_memoria"),
            ("L incierto", "lentitud", {"p21": D, "p27": D}, None),
            ("V pantalla externa", "video", {"p07": N, "p02": S, "p03": S, "p08": S}, "d_pantalla_principal"),
            ("V sin salida", "video", {"p07": N, "p02": S, "p03": S, "p08": N, "p04": N, "p06": N, "p05": D}, "d_subsistema_video"),
            ("V incierto", "video", {"p07": D, "p02": D, "p03": D}, None),
            ("S unidad ausente", "sistema", {"p16": N, "p06": N, "p26": S, "p12": S, "p10": N, "p17": N, "p11": D}, "d_deteccion_almacenamiento"),
            ("S error crítico", "sistema", {"p16": S, "p17": S, "p09": N, "p11": N}, "d_error_critico_so"),
            ("S incierto", "sistema", {"p16": N, "p06": D, "p26": D, "p12": D, "p04": D, "p05": D}, None),
            ("T medida", "temperatura", {"p30": S, "p14": S, "p15": S, "p13": S}, "d_sobrecalentamiento"),
            ("T indicios", "temperatura", {"p30": S, "p14": N, "p15": S, "p13": D}, "d_indicios_termicos"),
            ("T incierto", "temperatura", {"p30": D, "p14": D, "p15": D}, None),
            ("C wifi", "conectividad", {"p18": N, "p25": S, "p20": N, "p19": S}, "d_wifi_inhabilitado"),
            ("C cable", "conectividad", {"p18": N, "p25": N, "p29": S, "p31": S, "p19": S}, "d_enlace_cable"),
            ("C incierto", "conectividad", {"p18": N, "p25": D, "p29": D, "p19": D}, None),
            ("G alimentación", "general", {"p02": N, "p03": N}, "d_ruta_alimentacion"),
            ("G wifi", "general", {"p02": S, "p03": S, "p07": S, "p16": S, "p21": N, "p27": N, "p18": N, "p25": S, "p20": N, "p19": S}, "d_wifi_inhabilitado"),
            ("G incierto", "general", {"p02": D, "p03": D, "p07": D}, None),
        ]
        for nombre, categoria, respuestas, esperado in casos:
            with self.subTest(nombre=nombre):
                gestor, visitadas, diagnosticos = self.recorrer(categoria, respuestas)
                if esperado is None:
                    self.assertFalse(diagnosticos, (nombre, visitadas, diagnosticos))
                else:
                    self.assertIn(esperado, diagnosticos, (nombre, visitadas, diagnosticos))
                if nombre == "S unidad ausente":
                    self.assertEqual(gestor.hechos["s_unidad_no_detectada"], EstadoHecho.VERDADERO)
                if nombre == "C cable":
                    self.assertNotIn("p20", visitadas)
                    self.assertNotIn("d_wifi_inhabilitado", diagnosticos)

    def test_no_cambia_categoria_y_cambio_explicito_limpia_hechos(self):
        gestor = GestorPreguntas(self.preguntas, self.rutas, "conectividad")
        gestor.responder("p18", N)
        gestor.responder("p25", D)
        self.assertEqual(gestor.categoria_actual, "conectividad")
        self.assertEqual(gestor.siguiente().id, "p29")
        gestor.cambiar_categoria("video")
        self.assertEqual(gestor.categoria_actual, "video")
        self.assertEqual(gestor.siguiente().id, "p07")
        self.assertEqual(gestor.hechos["s_sin_red"], EstadoHecho.DESCONOCIDO)
        self.assertFalse(gestor.historial)

    def test_energia_no_equivale_a_funcionamiento_correcto(self):
        gestor, visitadas, diagnosticos = self.recorrer(
            "alimentacion", {"p02": S, "p03": S, "p07": S, "p16": N}
        )
        self.assertEqual(gestor.estado_final, "@bloqueo_sistema")
        self.assertEqual(visitadas, ["p02", "p03", "p07", "p16"])
        self.assertIn("d_revision_inicio_energia", diagnosticos)
        self.assertNotIn("d_ruta_alimentacion", diagnosticos)

    def test_editar_descarta_respuestas_dependientes(self):
        gestor = GestorPreguntas(self.preguntas, self.rutas, "conectividad")
        for pid, respuesta in (("p18", N), ("p25", S), ("p20", N)):
            gestor.responder(pid, respuesta)
        gestor.editar(1)
        self.assertEqual([r.pregunta_id for r in gestor.historial], ["p18"])
        self.assertEqual(gestor.siguiente().id, "p25")
        self.assertEqual(gestor.hechos["s_wifi_deshabilitado"], EstadoHecho.DESCONOCIDO)
        gestor.responder("p25", N)
        self.assertEqual(gestor.siguiente().id, "p29")

    def test_post_no_se_confunde_con_arranque_so(self):
        gestor, visitadas, diagnosticos = self.recorrer("sistema", {"p16": N, "p06": S, "p04": S})
        self.assertIn("d_memoria_ram", diagnosticos)
        self.assertNotIn("d_arranque_so", diagnosticos)
        self.assertNotIn("p10", visitadas)
        gestor, _, diagnosticos = self.recorrer("sistema", {"p16": N, "p06": N, "p26": S, "p12": S, "p10": S})
        self.assertEqual(gestor.hechos["s_unidad_no_detectada"], EstadoHecho.FALSO)
        self.assertIn("d_arranque_so", diagnosticos)

    def test_medida_y_solo_indicios_son_diagnosticos_distintos(self):
        _, _, medido = self.recorrer("temperatura", {"p30": N, "p14": N, "p15": N})
        self.assertFalse(medido)
        _, _, indicios = self.recorrer("temperatura", {"p30": S, "p14": N, "p15": S, "p13": D})
        self.assertEqual(indicios, {"d_indicios_termicos"})
        _, _, medido = self.recorrer("temperatura", {"p30": N, "p14": S, "p15": N, "p13": S})
        self.assertIn("d_sobrecalentamiento", medido)
        self.assertNotIn("d_indicios_termicos", medido)
        resultado = self.modelo.evaluar({
            "s_calor_percibido": "verdadero",
            "s_apagado_bajo_carga": "verdadero",
            "s_ventilador_ruidoso": "verdadero",
            "s_temperatura_alta": "verdadero",
        })
        salida = io.StringIO()
        mostrar_resultado(resultado, salida)
        self.assertLess(
            salida.getvalue().index("Temperatura anormal medida"),
            salida.getvalue().index("Indicios de posible problema térmico"),
        )

    def test_consola_confirma_cambio_y_permite_cancelarlo(self):
        salida = io.StringIO()
        respuestas = preguntar_condicional(self.preguntas, self.rutas, io.StringIO("6\nc\n3\nn\n2\nf\n"), salida).observaciones
        self.assertEqual(respuestas["s_sin_red"], "verdadero")
        self.assertEqual(respuestas["s_sin_imagen"], "desconocido")
        self.assertIn("Se conserva la consulta actual", salida.getvalue())
        salida = io.StringIO()
        respuestas = preguntar_condicional(self.preguntas, self.rutas, io.StringIO("6\n2\nc\n3\ns\n2\nf\n"), salida).observaciones
        self.assertEqual(respuestas["s_sin_red"], "desconocido")
        self.assertEqual(respuestas["s_sin_imagen"], "verdadero")
        self.assertIn("Consulta nueva iniciada", salida.getvalue())

    def test_bloqueo_de_video_no_muestra_diagnostico_de_alimentacion(self):
        proceso = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py")],
            cwd=RAIZ, input="3\n2\n2\n2\n\n",
            capture_output=True, text=True, encoding="utf-8", check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("No hay diagnóstico de video", proceso.stdout)
        self.assertNotIn("Posible problema en la ruta de alimentación", proceso.stdout)

    def test_i01_imagen_transitoria_no_bloquea_video(self):
        gestor, visitadas, diagnosticos = self.recorrer(
            "video", {"p07": S, "p32": S, "p08": S}
        )
        self.assertEqual(visitadas, ["p07", "p32", "p08"])
        self.assertEqual(gestor.estado_final, "@resultado")
        self.assertIn("d_pantalla_principal", diagnosticos)
        gestor, visitadas, diagnosticos = self.recorrer(
            "video", {"p07": S, "p32": N, "p09": N}
        )
        self.assertEqual(visitadas, ["p07", "p32", "p09"])
        self.assertEqual(gestor.estado_final, "@bloqueo_imagen")
        self.assertFalse(diagnosticos)

    def test_i02_web_actual_funciona_pero_red_intermitente_o_parcial(self):
        gestor, visitadas, diagnosticos = self.recorrer(
            "conectividad", {"p18": S, "p33": S, "p36": N}
        )
        self.assertEqual(visitadas, ["p18", "p33", "p36"])
        self.assertIn("d_conectividad_local", diagnosticos)
        gestor, visitadas, diagnosticos = self.recorrer(
            "conectividad", {"p18": S, "p33": N, "p34": S, "p37": D}
        )
        self.assertEqual(visitadas, ["p18", "p33", "p34", "p37"])
        self.assertEqual(gestor.estado_final, "@patron_red_sin_causa")
        self.assertFalse(diagnosticos)

    def test_i03_error_durante_uso_no_se_atribuye_a_causa_inventada(self):
        gestor, visitadas, diagnosticos = self.recorrer(
            "sistema", {"p16": S, "p17": N, "p11": N, "p35": S}
        )
        self.assertEqual(visitadas, ["p16", "p17", "p11", "p35"])
        self.assertEqual(gestor.estado_final, "@error_uso_sin_causa")
        self.assertEqual(gestor.hechos["s_error_durante_uso"], EstadoHecho.VERDADERO)
        self.assertFalse(diagnosticos)
        _, visitadas, _ = self.recorrer("sistema", {"p16": N, "p06": S, "p04": N, "p05": D})
        self.assertNotIn("p35", visitadas)

    def test_o01_resultado_integra_hipotesis_general_como_evidencia(self):
        gestor, _, _ = self.recorrer(
            "video", {"p07": N, "p02": S, "p03": S, "p08": S}
        )
        resultado = self.modelo.evaluar(gestor.observaciones)
        self.assertIn("d_revision_inicio_energia", resultado.memoria.conclusiones)
        salida = io.StringIO()
        mostrar_resultado(resultado, salida)
        texto = salida.getvalue()
        self.assertEqual(texto.count("Posible problema de inicio con energía presente"), 0)
        self.assertIn("Evidencia complementaria de energía presente", texto)
        self.assertIn("r_inicio_energia_luz", texto)
        self.assertIn("Posible problema de pantalla principal", texto)

    def test_validador_rechaza_grafo_invalido(self):
        mutaciones = (
            lambda doc: doc["categorias"][0]["nodos"]["p02"].pop("desconocido"),
            lambda doc: doc["categorias"][0]["nodos"]["p02"].update(si="p999"),
            lambda doc: doc["categorias"][0]["nodos"]["p02"].update(si="p02"),
        )
        for mutar in mutaciones:
            with self.subTest(mutacion=mutar):
                documento = copy.deepcopy(self.documento)
                mutar(documento)
                with self.assertRaises(ErrorRutas):
                    validar_rutas(documento, self.preguntas)


if __name__ == "__main__":
    unittest.main()
