"""Exploración independiente del cuestionario; no modifica el sistema."""

import collections
import io
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.gestor_preguntas import GestorPreguntas  # noqa: E402
from diagnostico_pc.consola import preguntar_condicional  # noqa: E402
from diagnostico_pc.hechos import EstadoHecho  # noqa: E402
from diagnostico_pc.modelo_a import ModeloA  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import cargar_rutas  # noqa: E402


class AuditoriaContextual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo = ModeloA.desde_directorio(RAIZ / "data" / "conocimiento")
        cls.preguntas = cargar_preguntas(
            RAIZ / "data" / "interfaz" / "preguntas.json", cls.modelo.sintomas
        )
        cls.rutas = cargar_rutas(
            RAIZ / "data" / "interfaz" / "rutas.json", cls.preguntas
        )

    def explorar(self, categoria, bifurcaciones=None):
        gestor = GestorPreguntas(self.preguntas, self.rutas, categoria)
        cuenta = collections.Counter()
        preguntas = set()
        reglas = set()
        diagnosticos = set()
        maximo = 0

        def avanzar():
            nonlocal maximo
            self.assertEqual(gestor.categoria_actual, categoria)
            self.assertFalse(gestor.contradicciones)
            siguiente = gestor.siguiente()
            if siguiente is None:
                terminal = gestor.estado_final
                self.assertIsNotNone(terminal)
                cuenta[terminal] += 1
                maximo = max(maximo, len(gestor.historial))
                inferencia = self.modelo.evaluar(gestor.observaciones)
                reglas.update(inferencia.memoria.reglas_activadas)
                diagnosticos.update(inferencia.memoria.conclusiones)
                if terminal == "@insuficiente":
                    self.assertFalse(inferencia.memoria.conclusiones)
                return
            self.assertNotIn(siguiente.id, (r.pregunta_id for r in gestor.historial))
            hechos = gestor.hechos
            if siguiente.id == "p32":
                self.assertEqual(categoria, "video")
                self.assertEqual(hechos["s_sin_imagen"], EstadoHecho.FALSO)
            elif siguiente.id == "p33":
                self.assertEqual(categoria, "conectividad")
                self.assertNotEqual(hechos["s_sin_red"], EstadoHecho.VERDADERO)
            elif siguiente.id == "p34":
                self.assertEqual(categoria, "conectividad")
                self.assertNotEqual(hechos["s_sin_red"], EstadoHecho.VERDADERO)
                self.assertNotEqual(hechos["s_red_intermitente"], EstadoHecho.VERDADERO)
            elif siguiente.id == "p35":
                self.assertEqual(categoria, "sistema")
                self.assertEqual(hechos["s_so_no_inicia"], EstadoHecho.FALSO)
                self.assertNotEqual(hechos["s_pantalla_azul"], EstadoHecho.VERDADERO)
                self.assertNotEqual(hechos["s_errores_entrada_salida"], EstadoHecho.VERDADERO)
            elif siguiente.id == "p36":
                self.assertEqual(categoria, "conectividad")
                self.assertEqual(hechos["s_red_intermitente"], EstadoHecho.VERDADERO)
            elif siguiente.id == "p37":
                self.assertEqual(categoria, "conectividad")
                self.assertEqual(hechos["s_pagina_especifica_falla"], EstadoHecho.VERDADERO)
            preguntas.add(siguiente.id)
            opciones = tuple(RespuestaVisible) if bifurcaciones is None or siguiente.id in bifurcaciones else (RespuestaVisible.NO_ESTOY_SEGURO,)
            for opcion in opciones:
                gestor.responder(siguiente.id, opcion)
                avanzar()
                gestor.volver()

        avanzar()
        return cuenta, preguntas, reglas, diagnosticos, maximo

    def recorrido(self, categoria, respuestas):
        gestor = GestorPreguntas(self.preguntas, self.rutas, categoria)
        visitadas = []
        while (pregunta := gestor.siguiente()) is not None:
            visitadas.append(pregunta.id)
            gestor.responder(
                pregunta.id,
                respuestas.get(pregunta.id, RespuestaVisible.NO_ESTOY_SEGURO),
            )
        resultado = self.modelo.evaluar(gestor.observaciones)
        return visitadas, gestor.estado_final, set(resultado.memoria.conclusiones)

    def test_rutas_especificas_todas_las_respuestas(self):
        for categoria in self.rutas.categorias:
            if categoria.id == "general":
                continue
            with self.subTest(categoria=categoria.id):
                cuenta, preguntas, reglas, diagnosticos, maximo = self.explorar(categoria.id)
                self.assertEqual(preguntas, set(categoria.nodos))
                print(
                    "COBERTURA", categoria.id, "trayectorias", sum(cuenta.values()),
                    "terminales", dict(cuenta), "preguntas", len(preguntas),
                    "reglas", len(reglas), "diagnosticos", len(diagnosticos),
                    "profundidad_maxima", maximo,
                )

    def test_ruta_general_muestra_acotada(self):
        pivotes = {"p02", "p03", "p07", "p16", "p21", "p27", "p18", "p25", "p30"}
        cuenta, preguntas, reglas, diagnosticos, maximo = self.explorar("general", pivotes)
        print(
            "COBERTURA general_muestra trayectorias", sum(cuenta.values()),
            "terminales", dict(cuenta), "preguntas", len(preguntas),
            "reglas", len(reglas), "diagnosticos", len(diagnosticos),
            "profundidad_maxima", maximo,
        )

    def test_cantidad_y_polaridades_observadas(self):
        conocimiento = RAIZ / "data" / "conocimiento"
        hechos = json.loads((conocimiento / "hechos.json").read_text(encoding="utf-8"))["hechos"]
        reglas = json.loads((conocimiento / "reglas.json").read_text(encoding="utf-8"))["reglas"]
        self.assertEqual((len(hechos), len(self.preguntas), len(reglas), len(self.modelo.diagnosticos)), (36, 36, 42, 18))
        preguntas = {p.id: p for p in self.preguntas}
        self.assertEqual(preguntas["p10"].estado_para(RespuestaVisible.SI).value, "falso")
        self.assertEqual(preguntas["p10"].estado_para(RespuestaVisible.NO).value, "verdadero")
        self.assertEqual(preguntas["p10"].estado_para(RespuestaVisible.NO_ESTOY_SEGURO).value, "desconocido")

    def test_cierres_corregidos_para_auditoria_semantica(self):
        si, no, duda = tuple(RespuestaVisible)
        casos = (
            ("video", {"p07": si, "p32": si, "p08": si},
             ["p07", "p32", "p08"], "@resultado", {"d_pantalla_principal"}),
            ("video", {"p07": si, "p32": duda, "p09": no},
             ["p07", "p32", "p09"], "@insuficiente", set()),
            ("conectividad", {"p18": si, "p33": si, "p36": no},
             ["p18", "p33", "p36"], "@resultado", {"d_conectividad_local"}),
            ("conectividad", {"p18": si, "p33": no, "p34": si, "p37": duda},
             ["p18", "p33", "p34", "p37"], "@patron_red_sin_causa", set()),
            ("sistema", {"p16": si, "p17": no, "p11": no, "p35": si},
             ["p16", "p17", "p11", "p35"], "@error_uso_sin_causa", set()),
        )
        for categoria, respuestas, preguntas, terminal, esperados in casos:
            with self.subTest(categoria=categoria):
                visitadas, observado, diagnosticos = self.recorrido(categoria, respuestas)
                self.assertEqual((visitadas, observado, diagnosticos),
                                 (preguntas, terminal, esperados))

    def test_perfiles_representativos(self):
        si, no, duda = tuple(RespuestaVisible)
        casos = (
            ("principiante", "video", {}, "@insuficiente", set()),
            ("sintomas_basicos", "video", {"p07": no, "p02": si, "p03": si, "p08": si},
             "@resultado", {"d_pantalla_principal"}),
            ("medicion_desconocida", "temperatura", {"p30": si, "p14": si, "p15": duda},
             "@resultado", {"d_indicios_termicos"}),
            ("categoria_correcta", "conectividad", {"p18": no, "p25": si, "p20": no, "p19": si},
             "@resultado", {"d_wifi_inhabilitado"}),
            ("categoria_equivocada", "video", {"p07": no, "p02": no, "p03": no},
             "@bloqueo_energia", {"d_ruta_alimentacion"}),
            ("sintomas_multiples", "lentitud", {"p21": si, "p27": si, "p22": si,
             "p23": si, "p24": si, "p28": si, "p11": si}, "@resultado",
             {"d_espacio_insuficiente", "d_presion_memoria", "d_proceso_exigente",
              "d_salud_almacenamiento"}),
        )
        for perfil, categoria, respuestas, terminal, esperados in casos:
            with self.subTest(perfil=perfil):
                visitadas, final, diagnosticos = self.recorrido(categoria, respuestas)
                self.assertEqual(final, terminal)
                self.assertTrue(esperados <= diagnosticos)
                print("PERFIL", perfil, categoria, visitadas, final, sorted(diagnosticos))

    def test_respuesta_parcial_finaliza_sin_inventar_negaciones(self):
        consulta = preguntar_condicional(
            self.preguntas, self.rutas, io.StringIO("4\n2\nf\n"), io.StringIO()
        )
        self.assertIsNone(consulta.terminal)
        self.assertEqual(consulta.observaciones["s_so_no_inicia"], "verdadero")
        self.assertEqual(consulta.observaciones["s_reinicios_post"], "desconocido")
        self.assertIsNone(self.modelo.evaluar(consulta.observaciones).principal)

    def test_mensajes_de_cierre_corregidos_en_consola(self):
        casos = (
            ("3\n1\n1\n1\n\n", "@resultado", "Se completaron las comprobaciones útiles"),
            ("6\n1\n1\n3\n\n", "@patron_red_sin_causa", "Se registró un problema de conexión"),
            ("4\n1\n2\n2\n1\n\n", "@error_uso_sin_causa", "Se registró un error durante el uso"),
        )
        for respuestas, terminal, mensaje in casos:
            with self.subTest(terminal=terminal):
                salida = io.StringIO()
                consulta = preguntar_condicional(
                    self.preguntas, self.rutas, io.StringIO(respuestas), salida
                )
                self.assertEqual(consulta.terminal, terminal)
                self.assertIn(mensaje, salida.getvalue())


if __name__ == "__main__":
    unittest.main()
