"""Integridad del cuestionario visible, independiente de las reglas."""

import copy
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.modelo_a import ModeloA  # noqa: E402
from diagnostico_pc.preguntas import ErrorPreguntas, validar_preguntas  # noqa: E402


class PruebasPreguntas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sintomas = ModeloA.desde_directorio(RAIZ / "data" / "conocimiento").sintomas
        cls.documento = json.loads(
            (RAIZ / "data" / "interfaz" / "preguntas.json").read_text(encoding="utf-8")
        )

    def test_catalogo_visible_valido(self):
        preguntas = validar_preguntas(self.documento, self.sintomas)
        self.assertEqual(len(preguntas), 20)
        self.assertEqual(len({pregunta.id for pregunta in preguntas}), 20)

    def test_rechaza_duplicados_faltantes_y_polaridad_invalida(self):
        cambios = (
            (lambda doc: doc["preguntas"][1].update(id="p01"), "ID de pregunta duplicado"),
            (lambda doc: doc["preguntas"][1].update(hecho="s_no_enciende"), "pregunta duplicada"),
            (lambda doc: doc["preguntas"].pop(), "Faltan preguntas"),
            (lambda doc: doc["preguntas"][0].update(estado_no="falso"), "orden opuesto"),
            (lambda doc: doc["preguntas"][0].update(ayuda=""), "texto no vacío"),
        )
        for cambiar, mensaje in cambios:
            with self.subTest(mensaje=mensaje):
                documento = copy.deepcopy(self.documento)
                cambiar(documento)
                with self.assertRaises(ErrorPreguntas) as contexto:
                    validar_preguntas(documento, self.sintomas)
                self.assertIn(mensaje, str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
