"""Pruebas del manifiesto de selección; no cargan la reserva final."""

import copy
import json
import unittest
from pathlib import Path

from verificar_seleccion import ARCHIVOS_CONGELADOS, ErrorSeleccion, MANIFIESTO, RAIZ, verificar


class SeleccionModeloTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifiesto = json.loads((RAIZ / MANIFIESTO).read_text(encoding="utf-8"))

    def test_manifiesto_coincide_con_archivos_congelados(self):
        self.assertEqual(verificar(), len(ARCHIVOS_CONGELADOS))
        self.assertNotIn("data/evaluacion/casos_finales_reservados.json", ARCHIVOS_CONGELADOS)

    def test_rechaza_huella_alterada(self):
        alterado = copy.deepcopy(self.manifiesto)
        alterado["archivos"]["src/diagnostico_pc/modelo_c.py"] = "0" * 64
        with self.assertRaisesRegex(ErrorSeleccion, "Huella distinta"):
            verificar(alterado)

    def test_rechaza_ruta_adicional(self):
        alterado = copy.deepcopy(self.manifiesto)
        alterado["archivos"]["data/evaluacion/casos_finales_reservados.json"] = "0" * 64
        with self.assertRaisesRegex(ErrorSeleccion, "lista de archivos"):
            verificar(alterado)


if __name__ == "__main__":
    unittest.main()
