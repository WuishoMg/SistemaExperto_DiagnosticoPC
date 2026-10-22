"""Regresiones del orden simbólico C; desempates sintéticos marcados como tales."""

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
from diagnostico_pc.conocimiento_c import leer_criterios, validar_criterios  # noqa: E402
from diagnostico_pc.consola import mostrar_resultado_c  # noqa: E402
from diagnostico_pc.hechos import EstadoHecho  # noqa: E402
from diagnostico_pc.modelo_b import ConflictoInferencia, ModeloB  # noqa: E402
from diagnostico_pc.modelo_c import CriterioHipotesis, ModeloC  # noqa: E402
from diagnostico_pc.validacion import ErrorConocimiento, leer_documentos  # noqa: E402


class PruebasModeloC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = leer_documentos(RAIZ / "data" / "conocimiento")
        cls.ampliacion = leer_ampliacion(RAIZ / "data" / "conocimiento_avance2")
        cls.criterios = leer_criterios(RAIZ / "data" / "conocimiento_avance2" / "criterios_c.json")
        cls.b = ModeloB(*cls.base, *cls.ampliacion)
        cls.c = ModeloC(*cls.base, *cls.ampliacion, cls.criterios)

    def test_c_reutiliza_conocimiento_cierre_y_hipotesis_de_b(self):
        self.assertEqual(self.b.reglas, self.c.reglas)
        self.assertEqual(self.b.hechos, self.c.hechos)
        self.assertEqual(self.b.diagnosticos, self.c.diagnosticos)
        for observaciones in (
            {},
            {"s_error_prueba_ram": "verdadero", "s_pitidos_ram_post": "verdadero"},
            {"s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
             "s_sin_dispositivo_arranque": "verdadero", "s_unidad_no_detectada": "falso"},
            {"s_temperatura_alta": "verdadero", "s_calor_percibido": "verdadero",
             "s_ventilador_ruidoso": "verdadero", "s_apagado_bajo_carga": "verdadero"},
        ):
            with self.subTest(observaciones=observaciones):
                b, c = self.b.evaluar(observaciones), self.c.evaluar(observaciones)
                self.assertEqual(b.memoria.hechos, c.memoria.hechos)
                self.assertEqual(b.memoria.reglas_activadas, c.memoria.reglas_activadas)
                self.assertEqual(b.memoria.conclusiones, c.memoria.conclusiones)
                self.assertEqual(b.trazas, c.trazas)
                self.assertEqual(b.rondas, c.rondas)
                self.assertEqual(
                    {d.id for d in (b.principal, *b.alternativos) if d},
                    {d.id for d in (c.principal, *c.alternativos) if d},
                )

    def test_ejemplo_termico_cambia_orden_por_calidad_y_conserva_alternativa(self):
        observaciones = {"s_temperatura_alta": "verdadero", "s_calor_percibido": "verdadero",
                         "s_ventilador_ruidoso": "verdadero", "s_apagado_bajo_carga": "verdadero"}
        b, c = self.b.evaluar(observaciones), self.c.evaluar(observaciones)
        self.assertEqual(b.principal.id, "d_indicios_termicos")
        self.assertEqual(c.principal.id, "d_sobrecalentamiento")
        self.assertEqual([d.id for d in c.alternativos], ["d_indicios_termicos"])
        self.assertEqual([(x.calidad, x.especificidad) for x in c.criterios], [(3, 3), (2, 3)])
        self.assertIn("calidad de evidencia", c.explicacion_prioridad)
        salida = io.StringIO()
        mostrar_resultado_c(c, salida)
        for texto in ("Observaciones originales", "Hipótesis alternativa", "Reglas activadas",
                      "prioridad técnica ordinal", "Orden:", "no son probabilidades"):
            self.assertIn(texto, salida.getvalue())

    def test_soportes_derivados_no_cuentan_como_observaciones_adicionales(self):
        c = self.c.evaluar({"s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
                           "s_sin_dispositivo_arranque": "verdadero", "s_unidad_no_detectada": "falso"})
        self.assertEqual(c.principal.id, "d_arranque_so")
        self.assertEqual(c.criterios[0].observaciones, (
            "s_post_completado", "s_sin_dispositivo_arranque", "s_so_no_inicia",
            "s_unidad_no_detectada",
        ))
        self.assertEqual(c.criterios[0].especificidad, 4)
        self.assertNotIn("h_fallo_etapa_arranque", c.criterios[0].observaciones)
        self.assertEqual(c.orden_b, ("d_arranque_so",))

    def test_orden_coincidente_y_prioridad_ordinal_sintetica(self):
        observaciones = {"s_lentitud_programas": "verdadero",
                         "s_espacio_sistema_bajo": "verdadero", "s_uso_memoria_alto": "verdadero"}
        real = self.c.evaluar(observaciones)
        self.assertEqual(real.orden_b, ("d_espacio_insuficiente", "d_presion_memoria"))
        self.assertEqual(real.principal.id, "d_espacio_insuficiente")
        self.assertIn("B y C conservan el mismo orden", real.explicacion_prioridad)
        # Metadatos sintéticos solo para probar el tercer criterio; no se guardan.
        documento = copy.deepcopy(self.criterios)
        next(x for x in documento["prioridades"] if x["id"] == "d_presion_memoria")["nivel"] = 2
        sintetico = ModeloC(*self.base, *self.ampliacion, documento).evaluar(observaciones)
        self.assertEqual(sintetico.principal.id, "d_presion_memoria")
        self.assertIn("prioridad técnica ordinal", sintetico.explicacion_prioridad)

    def test_desconocido_no_activa_regla_y_sin_hipotesis(self):
        c = self.c.evaluar({"s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
                           "s_unidad_no_detectada": "desconocido"})
        self.assertIsNone(c.principal)
        self.assertEqual(c.memoria.hechos["h_fallo_arranque_unidad_visible"], EstadoHecho.DESCONOCIDO)
        self.assertEqual(c.criterios, ())

    def test_metadatos_rechazan_omisiones_duplicados_y_niveles_invalidos(self):
        for cambio in ("omision", "duplicado", "nivel", "justificacion"):
            doc = copy.deepcopy(self.criterios)
            if cambio == "omision":
                doc["evidencia"].pop()
            elif cambio == "duplicado":
                doc["evidencia"].append(copy.deepcopy(doc["evidencia"][0]))
            elif cambio == "nivel":
                doc["prioridades"][0]["nivel"] = 90
            else:
                doc["evidencia"][0]["justificacion"] = ""
            with self.subTest(cambio=cambio), self.assertRaises(ErrorConocimiento):
                validar_criterios(doc, self.c.sintomas, set(self.c.diagnosticos))

    def test_desempates_sinteticos_ordinales_y_deterministas(self):
        # Solo puntuaciones sintéticas: no son casos de evaluación diagnóstica.
        criterios = [
            CriterioHipotesis("z", ("x",), 3, 1, 1),
            CriterioHipotesis("y", ("x", "y"), 2, 2, 2),
            CriterioHipotesis("b", ("x", "y"), 3, 2, 1),
            CriterioHipotesis("a", ("x", "y"), 3, 2, 1),
            CriterioHipotesis("c", ("x", "y"), 3, 2, 2),
        ]
        esperado = ["c", "a", "b", "z", "y"]
        for _ in range(3):
            self.assertEqual([c.diagnostico_id for c in sorted(criterios, key=lambda c: c.clave)], esperado)
            criterios.reverse()

    def test_c_hereda_rechazo_de_ciclos_y_contradicciones_de_b(self):
        reglas = copy.deepcopy(self.ampliacion[1])
        reglas["reglas"].append({
            "id": "r_c_ciclo_sintetico", "condiciones": [{"hecho": "h_fallo_arranque_unidad_visible", "estado": "verdadero"}],
            "conclusion": {"tipo": "hecho", "id": "h_fallo_etapa_arranque", "estado": "verdadero"},
            "explicacion": "Solo para probar ciclos.",
        })
        with self.assertRaisesRegex(ErrorConocimiento, "Ciclo"):
            ModeloC(*self.base, self.ampliacion[0], reglas, self.criterios)
        reglas = copy.deepcopy(self.ampliacion[1])
        reglas["reglas"].append({
            "id": "r_c_contradiccion_sintetica", "condiciones": [{"hecho": "s_pantalla_azul", "estado": "verdadero"}],
            "conclusion": {"tipo": "hecho", "id": "h_fallo_etapa_arranque", "estado": "falso"},
            "explicacion": "Solo para probar contradicciones.",
        })
        modelo = ModeloC(*self.base, self.ampliacion[0], reglas, self.criterios)
        with self.assertRaises(ConflictoInferencia):
            modelo.evaluar({"s_so_no_inicia": "verdadero", "s_post_completado": "verdadero",
                            "s_pantalla_azul": "verdadero"})

    def test_cli_c_ejemplo_reproducible(self):
        proceso = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py"), "--modelo", "C",
             "--respuestas", str(RAIZ / "ejemplos" / "hipotesis_termicas_c.json")],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("Hipótesis principal: Temperatura anormal medida", proceso.stdout)
        self.assertIn("Hipótesis alternativa 1: Indicios", proceso.stdout)
        self.assertIn("El orden difiere del de B", proceso.stdout)

    def test_cli_c_conserva_cuestionario_condicional(self):
        proceso = subprocess.run(
            [sys.executable, str(RAIZ / "diagnosticar.py"), "--modelo", "C"],
            cwd=RAIZ, input="1\n2\n2\n3\n\n", capture_output=True, text=True,
            encoding="utf-8", check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("¿Qué problema presenta tu computadora?", proceso.stdout)
        self.assertIn("Resultado del Modelo C", proceso.stdout)
        self.assertIn("Posible problema en la ruta de alimentación", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
