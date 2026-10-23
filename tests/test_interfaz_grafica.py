"""Integración del adaptador puro sin abrir la reserva final."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.gui.session import SesionGrafica  # noqa: E402
from diagnostico_pc.gui.serialization import serializar_resultado  # noqa: E402
from diagnostico_pc.selector import seleccionar_modelo  # noqa: E402
from diagnostico_pc.validacion import ErrorConocimiento  # noqa: E402
import json  # noqa: E402


class PruebasSesionGrafica(unittest.TestCase):
    def setUp(self):
        self.sesion = SesionGrafica(RAIZ)

    def test_categorias_y_modelo_c_conservan_estado_desconocido(self):
        self.assertEqual(len(self.sesion.estado()["categorias"]), 7)
        self.sesion.elegir_categoria("temperatura")
        pregunta = self.sesion.estado()["preguntaActual"]
        self.sesion.responder(pregunta["id"], "no_estoy_seguro")
        self.assertEqual(self.sesion.gestor.observaciones[self.sesion.gestor.preguntas[pregunta["id"]].hecho], "desconocido")
        resultado = self.sesion.ver_resultado()
        self.assertEqual(resultado["modelo"], "C")
        self.assertEqual(resultado["principal"], None)

    def test_falla_de_carga_de_conocimiento_se_informa(self):
        with self.assertRaises(ErrorConocimiento):
            SesionGrafica(RAIZ / "directorio_inexistente")

    def test_editar_elimina_hechos_dependientes_y_resultado(self):
        self.sesion.elegir_categoria("conectividad")
        self.sesion.responder("p18", "no")
        self.sesion.responder("p25", "no_estoy_seguro")
        self.sesion.responder("p29", "si")
        self.sesion.ver_resultado()
        self.sesion.editar(1)
        self.assertEqual(self.sesion.estado()["pantalla"], "preguntas")
        self.assertEqual(self.sesion.estado()["preguntaActual"]["id"], "p25")
        self.assertEqual(len(self.sesion.estado()["historial"]), 1)
        self.assertEqual(self.sesion.estado()["resultado"], {})
        self.assertEqual(self.sesion.gestor.hechos["s_wifi_deshabilitado"].value, "desconocido")

    def test_cambio_de_categoria_limpia_la_sesion(self):
        self.sesion.elegir_categoria("conectividad")
        self.sesion.responder("p18", "no")
        self.sesion.iniciar_nueva_consulta("video")
        self.assertEqual(self.sesion.estado()["preguntaActual"]["id"], "p07")
        self.assertEqual(self.sesion.estado()["historial"], [])
        self.assertEqual(self.sesion.gestor.hechos["s_sin_red"].value, "desconocido")

    def test_comparacion_no_modifica_resultado_principal_c(self):
        self.sesion.elegir_categoria("temperatura")
        self.sesion.responder(self.sesion.estado()["preguntaActual"]["id"], "no_estoy_seguro")
        resultado = self.sesion.ver_resultado()
        comparacion = self.sesion.comparar_modelos()
        self.assertEqual([r["modelo"] for r in comparacion], ["A", "B", "C"])
        self.assertEqual(resultado, comparacion[2])
        self.assertEqual(self.sesion.estado()["resultado"], resultado)

    def test_regresar_de_resultado_sin_respuestas_vuelve_a_pregunta(self):
        self.sesion.elegir_categoria("temperatura")
        self.sesion.ver_resultado()
        self.sesion.volver()
        self.assertEqual(self.sesion.estado()["pantalla"], "preguntas")
        self.assertEqual(self.sesion.estado()["resultado"], {})

    def test_trazas_y_criterios_son_copia_del_motor_c(self):
        respuestas = json.loads((RAIZ / "ejemplos" / "arranque_multinivel_b.json").read_text(encoding="utf-8"))
        motor = seleccionar_modelo("C")
        original = motor.evaluar(respuestas)
        simple = serializar_resultado(original)
        self.assertEqual(simple["principal"]["id"], original.principal.id)
        self.assertEqual([t["reglaId"] for t in simple["trazas"]], [t.regla_id for t in original.trazas])
        self.assertEqual([c["diagnosticoId"] for c in simple["criterios"]], [c.diagnostico_id for c in original.criterios])
        self.assertEqual(
            {h["hechoId"]: h["estado"] for h in simple["hechosDerivados"]},
            {t.conclusion_id: original.memoria.hechos[t.conclusion_id].value for t in original.trazas if t.conclusion_tipo == "hecho"},
        )


if __name__ == "__main__":
    unittest.main()
