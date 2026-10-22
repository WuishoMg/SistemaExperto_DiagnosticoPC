"""Regresiones del validador de viñetas; no importa motores A, B ni C."""

import copy
import json
import unittest
from pathlib import Path

from validar_casos import ErrorCasos, validar_documentos
from diagnostico_pc.preguntas import cargar_preguntas
from diagnostico_pc.rutas import cargar_rutas


ROOT = Path(__file__).resolve().parents[1]


class ValidacionCasosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / "data"
        cls.desarrollo = json.loads((base / "evaluacion/casos_desarrollo.json").read_text(encoding="utf-8"))
        cls.final = json.loads((base / "evaluacion/casos_finales_reservados.json").read_text(encoding="utf-8"))
        cls.fuentes = json.loads((base / "evaluacion/fuentes.json").read_text(encoding="utf-8"))
        hechos_doc = json.loads((base / "conocimiento/hechos.json").read_text(encoding="utf-8"))
        diag_doc = json.loads((base / "conocimiento/diagnosticos.json").read_text(encoding="utf-8"))
        cls.hechos = {x["id"] for x in hechos_doc["hechos"] if x["tipo"] == "sintoma"}
        cls.diagnosticos = {x["id"] for x in diag_doc["diagnosticos"]}
        cls.preguntas = cargar_preguntas(base / "interfaz/preguntas.json", cls.hechos)
        cls.rutas = cargar_rutas(base / "interfaz/rutas.json", cls.preguntas)

    def validar(self, desarrollo=None, final=None):
        return validar_documentos(
            desarrollo or self.desarrollo, final or self.final, self.fuentes,
            self.preguntas, self.rutas, self.hechos, self.diagnosticos,
        )

    def test_80_casos_y_siete_rutas(self):
        resumen = self.validar()
        self.assertEqual(sum(resumen["categoria"].values()), 80)
        self.assertEqual(len(resumen["categoria"]), 7)

    def test_rechaza_hecho_inexistente(self):
        doc = copy.deepcopy(self.desarrollo)
        doc["casos"][0]["observaciones"]["s_inventado"] = "verdadero"
        with self.assertRaisesRegex(ErrorCasos, "hecho fuera de catálogo"):
            self.validar(desarrollo=doc)

    def test_rechaza_estado_invertido_frente_al_trayecto(self):
        doc = copy.deepcopy(self.desarrollo)
        doc["casos"][26]["observaciones"]["s_unidad_no_detectada"] = "verdadero"
        with self.assertRaises(ErrorCasos):
            self.validar(desarrollo=doc)

    def test_rechaza_prioridad_ajena_al_conjunto(self):
        doc = copy.deepcopy(self.desarrollo)
        doc["casos"][9]["prioridad_revision"]["diagnostico"] = "d_memoria_ram"
        with self.assertRaisesRegex(ErrorCasos, "prioridad sin sustento"):
            self.validar(desarrollo=doc)

    def test_rechaza_reutilizacion_de_observaciones_finales(self):
        reservado = copy.deepcopy(self.final)
        reservado["casos"][0]["ruta"] = self.desarrollo["casos"][0]["ruta"]
        reservado["casos"][0]["trayecto_preguntas"] = self.desarrollo["casos"][0]["trayecto_preguntas"]
        reservado["casos"][0]["observaciones"] = self.desarrollo["casos"][0]["observaciones"]
        reservado["casos"][0]["evidencia_conocida"] = self.desarrollo["casos"][0]["evidencia_conocida"]
        reservado["casos"][0]["informacion_faltante"] = self.desarrollo["casos"][0]["informacion_faltante"]
        with self.assertRaisesRegex(ErrorCasos, "duplicadas entre grupos"):
            self.validar(final=reservado)


if __name__ == "__main__":
    unittest.main()
