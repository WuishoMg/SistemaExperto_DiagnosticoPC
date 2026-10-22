"""Punto de entrada simple para validar la base desde la raíz del proyecto."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.preguntas import ErrorPreguntas, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import ErrorRutas, cargar_rutas  # noqa: E402
from diagnostico_pc.validacion import ErrorConocimiento, leer_documentos, validar_documentos  # noqa: E402
from diagnostico_pc.conocimiento_b import leer_ampliacion, validar_ampliacion  # noqa: E402
from diagnostico_pc.conocimiento_c import leer_criterios, validar_criterios  # noqa: E402


def main() -> int:
    try:
        documentos = leer_documentos(RAIZ / "data" / "conocimiento")
        resumen = validar_documentos(*documentos)
        ampliacion = leer_ampliacion(RAIZ / "data" / "conocimiento_avance2")
        validar_ampliacion(*documentos, *ampliacion)
        criterios = leer_criterios(RAIZ / "data" / "conocimiento_avance2" / "criterios_c.json")
        hechos_doc = documentos[0]
        sintomas = {hecho["id"] for hecho in hechos_doc["hechos"] if hecho["tipo"] == "sintoma"}
        validar_criterios(criterios, sintomas, {d["id"] for d in documentos[1]["diagnosticos"]})
        preguntas = cargar_preguntas(RAIZ / "data" / "interfaz" / "preguntas.json", sintomas)
        rutas = cargar_rutas(RAIZ / "data" / "interfaz" / "rutas.json", preguntas)
    except (ErrorConocimiento, ErrorPreguntas, ErrorRutas) as error:
        print("Catálogo inválido:", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1
    print(
        "Base de conocimientos válida: "
        f"{resumen.hechos} hechos, {resumen.diagnosticos} diagnósticos, "
        f"{resumen.reglas} reglas."
    )
    print(f"Cuestionario válido: {len(preguntas)} preguntas con mapeo Sí/No/No estoy seguro.")
    print(f"Rutas válidas: {len(rutas.categorias)} categorías con aplicabilidad comprobada.")
    print(
        f"Ampliación B válida: {len(ampliacion[0]['hechos'])} hechos derivados y "
        f"{len(ampliacion[1]['reglas'])} reglas nuevas."
    )
    print(f"Criterios C válidos: {len(criterios['evidencia'])} observaciones y {len(criterios['prioridades'])} diagnósticos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
