"""Pruebas sintéticas de etapa 5; nunca cargan la reserva final."""

import unittest

from evaluar_desarrollo import calcular_modelo, comprobar_bc, proyectar_entrada, razon
from diagnostico_pc.hechos import EstadoHecho, normalizar_observaciones


def caso(ident, referencia, prioridad, a, b, c):
    return {
        "id": ident, "ruta": "general", "tipo_escenario": "ambigua",
        "referencia": referencia, "prioridad": prioridad,
        "modelos": {m: {"orden": orden, "hechos_derivados": {}}
                    for m, orden in (("A", a), ("B", b), ("C", c))},
    }


class EvaluacionDesarrolloTests(unittest.TestCase):
    def setUp(self):
        self.casos = [
            caso("D001", ["d1", "d2"], "d2", ["d1", "d2"], ["d2", "d1"], ["d1", "d2"]),
            caso("D002", [], None, [], ["d1"], ["d1"]),
            caso("D003", ["d2"], None, [], ["d2"], ["d2"]),
        ]

    def test_metricas_multietiqueta_y_matrices(self):
        met, matrices, errores = calcular_modelo(self.casos, "A", ["d1", "d2"])
        self.assertEqual(met["accuracy"], razon(2, 3))
        self.assertEqual((met["tp"], met["fp"], met["fn"]), (2, 0, 1))
        self.assertEqual(met["precision_micro"], razon(2, 2))
        self.assertEqual(met["recall_micro"], razon(2, 3))
        self.assertEqual(met["f1_micro"], razon(4, 5))
        self.assertEqual(met["principal"], razon(1, 2))
        self.assertEqual(met["accuracy_referencia_vacia"], razon(1, 1))
        self.assertEqual(met["abstenciones_incorrectas"], razon(1, 2))
        self.assertEqual(matrices["d1"], {"tn": 2, "fp": 0, "fn": 0, "tp": 1, "soporte": 1, "total": 3})
        self.assertEqual(matrices["d2"], {"tn": 1, "fp": 0, "fn": 1, "tp": 1, "soporte": 2, "total": 3})
        self.assertTrue(errores[2]["abstencion_incorrecta"])

    def test_prioridad_mismo_denominador_tres_modelos(self):
        resultados = {m: calcular_modelo(self.casos, m, ["d1", "d2"])[0] for m in "ABC"}
        self.assertEqual([resultados[m]["prioridad_principal"]["denominador"] for m in "ABC"], [1, 1, 1])
        self.assertEqual(resultados["A"]["prioridad_principal"], razon(0, 1))
        self.assertEqual(resultados["B"]["prioridad_principal"], razon(1, 1))
        self.assertEqual(resultados["A"]["prioridad_rango_reciproco_medio"], razon(0.5, 1))
        self.assertEqual(resultados["B"]["prioridad_rango_reciproco_medio"], razon(1.0, 1))

    def test_denominadores_nulos_son_indefinidos(self):
        unico = [caso("D001", [], None, [], [], [])]
        met, _, _ = calcular_modelo(unico, "A", ["d1"])
        self.assertIsNone(met["precision_micro"]["valor"])
        self.assertIsNone(met["recall_micro"]["valor"])
        self.assertIsNone(met["f1_micro"]["valor"])
        self.assertIsNone(met["principal"]["valor"])
        self.assertIsNone(met["prioridad_principal"]["valor"])

    def test_detecta_diferencia_de_conjunto_b_c(self):
        pred = {"casos": [{"id": "D001", "modelos": {
            "B": {"orden": ["d1", "d2"]}, "C": {"orden": ["d2", "d1"]}}}]}
        self.assertEqual(comprobar_bc(pred), [])
        pred["casos"][0]["modelos"]["C"]["orden"] = ["d2"]
        self.assertEqual(comprobar_bc(pred), ["D001"])

    def test_captura_proyecta_solo_campos_de_entrada(self):
        registro = {"id": "D001", "ruta": "general", "tipo_escenario": "ambigua",
                    "trayecto_preguntas": ["p01"], "observaciones": {"s1": "desconocido"},
                    "hipotesis_defendibles": ["d1"], "prioridad_revision": {"diagnostico": "d1"},
                    "relato": "No es entrada"}
        entrada = proyectar_entrada(registro)
        self.assertEqual(set(entrada), {"id", "ruta", "tipo_escenario", "trayecto_preguntas", "observaciones"})
        normalizadas = normalizar_observaciones({"s1", "s2"}, entrada["observaciones"])
        self.assertEqual(normalizadas["s1"], EstadoHecho.DESCONOCIDO)
        self.assertEqual(normalizadas["s2"], EstadoHecho.DESCONOCIDO)
        self.assertNotEqual(normalizadas["s1"], EstadoHecho.FALSO)


if __name__ == "__main__":
    unittest.main()
