"""Pruebas de integridad y semántica trivalente de la fase 2."""

import copy
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.hechos import (  # noqa: E402
    EstadoHecho,
    condicion_satisfecha,
    normalizar_observaciones,
)
from diagnostico_pc.validacion import (  # noqa: E402
    ErrorConocimiento,
    validar_directorio,
    validar_documentos,
)


def documentos_reales():
    carpeta = RAIZ / "data" / "conocimiento"
    return [
        json.loads((carpeta / nombre).read_text(encoding="utf-8"))
        for nombre in ("hechos.json", "diagnosticos.json", "reglas.json")
    ]


class PruebasConocimiento(unittest.TestCase):
    def test_base_real_valida_y_cubre_todas_las_categorias(self):
        hechos, diagnosticos, reglas = documentos_reales()
        resumen = validar_directorio(RAIZ / "data" / "conocimiento")
        self.assertEqual((resumen.hechos, resumen.diagnosticos, resumen.reglas), (36, 18, 42))
        self.assertEqual(len({d["categoria"] for d in diagnosticos["diagnosticos"]}), 7)
        usados = {
            condicion["hecho"]
            for regla in reglas["reglas"]
            for condicion in regla["condiciones"]
        }
        # Un mensaje de error inespecífico se registra para orientar el cierre,
        # pero no debe activar una hipótesis causal sin más evidencia.
        self.assertEqual(
            {hecho["id"] for hecho in hechos["hechos"]} - usados,
            {"s_error_durante_uso"},
        )
        rutas = json.loads((RAIZ / "data" / "interfaz" / "rutas.json").read_text(encoding="utf-8"))
        sistema = next(c for c in rutas["categorias"] if c["id"] == "sistema")
        self.assertEqual(sistema["nodos"]["p35"]["si"], "@error_uso_sin_causa")
        concluidos = {regla["conclusion"]["id"] for regla in reglas["reglas"]}
        self.assertEqual(concluidos, {d["id"] for d in diagnosticos["diagnosticos"]})

    def test_desconocido_no_equivale_a_falso(self):
        estados = normalizar_observaciones(
            {"a", "b", "c"}, {"a": "verdadero", "b": "falso"}
        )
        self.assertEqual(estados["c"], EstadoHecho.DESCONOCIDO)
        self.assertFalse(condicion_satisfecha(estados["c"], EstadoHecho.FALSO))
        self.assertFalse(condicion_satisfecha(estados["c"], EstadoHecho.VERDADERO))
        self.assertTrue(condicion_satisfecha(estados["b"], EstadoHecho.FALSO))
        self.assertTrue(condicion_satisfecha(estados["a"], EstadoHecho.VERDADERO))

    def test_observaciones_invalidas_se_rechazan(self):
        for respuestas in ({"no_existe": "verdadero"}, {"a": "tal_vez"}, {"a": False}):
            with self.subTest(respuestas=respuestas), self.assertRaises(ValueError):
                normalizar_observaciones({"a"}, respuestas)
        with self.assertRaises(ValueError):
            condicion_satisfecha(EstadoHecho.DESCONOCIDO, EstadoHecho.DESCONOCIDO)

    def test_hechos_compuestos_retirados_no_se_convierten_en_evidencia_inventada(self):
        sintomas = {hecho["id"] for hecho in documentos_reales()[0]["hechos"]}
        with self.assertRaisesRegex(ValueError, "s_lentitud_programas y s_congelamientos"):
            normalizar_observaciones(sintomas, {"s_lentitud_o_congelamientos": "verdadero"})

    def test_errores_de_estructura_y_referencia(self):
        alteraciones = [
            ("hecho duplicado", lambda h, d, r: h["hechos"].append(copy.deepcopy(h["hechos"][0])), "duplicado"),
            ("diagnóstico duplicado", lambda h, d, r: d["diagnosticos"].append(copy.deepcopy(d["diagnosticos"][0])), "duplicado"),
            ("regla duplicada", lambda h, d, r: r["reglas"].append(copy.deepcopy(r["reglas"][0])), "duplicado"),
            ("hecho ausente", lambda h, d, r: r["reglas"][0]["condiciones"][0].update(hecho="s_fantasma"), "referencia inexistente"),
            ("diagnóstico ausente", lambda h, d, r: r["reglas"][0]["conclusion"].update(id="d_fantasma"), "diagnóstico inexistente"),
            ("condición desconocida", lambda h, d, r: r["reglas"][0]["condiciones"][0].update(estado="desconocido"), "solo 'verdadero' o 'falso'"),
            ("condiciones contradictorias", lambda h, d, r: r["reglas"][0]["condiciones"].append({"hecho": r["reglas"][0]["condiciones"][0]["hecho"], "estado": "falso" if r["reglas"][0]["condiciones"][0]["estado"] == "verdadero" else "verdadero"}), "contradictorias"),
            ("condición repetida", lambda h, d, r: r["reglas"][0]["condiciones"].append(copy.deepcopy(r["reglas"][0]["condiciones"][0])), "condición duplicada"),
            ("campo faltante", lambda h, d, r: d["diagnosticos"][0].pop("recomendaciones"), "falta 'recomendaciones'"),
            ("categoría inválida", lambda h, d, r: d["diagnosticos"][0].update(categoria=[]), "categoría no admitida"),
            ("conclusión a síntoma", lambda h, d, r: r["reglas"][0].update(conclusion={"tipo": "hecho", "id": "s_led_encendido", "estado": "verdadero"}), "solo puede concluirse un hecho derivado"),
            ("versión inválida", lambda h, d, r: h.update(version=True), "debe ser el entero 1"),
        ]
        for nombre, alterar, mensaje in alteraciones:
            with self.subTest(nombre=nombre):
                documentos = documentos_reales()
                alterar(*documentos)
                with self.assertRaises(ErrorConocimiento) as contexto:
                    validar_documentos(*documentos)
                self.assertIn(mensaje, str(contexto.exception))

    def test_conclusion_de_hecho_derivado_y_autorreferencia(self):
        documentos = documentos_reales()
        documentos[0]["hechos"].append(
            {"id": "h_arranque_interrumpido", "nombre": "Arranque interrumpido", "descripcion": "Hecho de ejemplo para compatibilidad futura.", "tipo": "derivado"}
        )
        documentos[2]["reglas"].append(
            {"id": "r_derivada_ejemplo", "condiciones": [{"hecho": "s_so_no_inicia", "estado": "verdadero"}], "conclusion": {"tipo": "hecho", "id": "h_arranque_interrumpido", "estado": "verdadero"}, "explicacion": "Ejemplo de hecho intermedio."}
        )
        self.assertEqual(validar_documentos(*documentos).hechos, 37)
        documentos[2]["reglas"][-1]["condiciones"].append(
            {"hecho": "h_arranque_interrumpido", "estado": "verdadero"}
        )
        with self.assertRaisesRegex(ErrorConocimiento, "propia conclusión"):
            validar_documentos(*documentos)

    def test_json_ilegible_se_informa_como_error_de_conocimiento(self):
        with patch.object(Path, "open", return_value=io.StringIO("{malformado")):
            with self.assertRaisesRegex(ErrorConocimiento, "no se pudo cargar JSON"):
                validar_directorio(Path("datos_simulados"))


if __name__ == "__main__":
    unittest.main()
