"""Punto de entrada simple para validar la base desde la raíz del proyecto."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.preguntas import ErrorPreguntas, cargar_preguntas  # noqa: E402
from diagnostico_pc.validacion import ErrorConocimiento, leer_documentos, validar_documentos  # noqa: E402


def main() -> int:
    try:
        documentos = leer_documentos(RAIZ / "data" / "conocimiento")
        resumen = validar_documentos(*documentos)
        hechos_doc = documentos[0]
        sintomas = {hecho["id"] for hecho in hechos_doc["hechos"] if hecho["tipo"] == "sintoma"}
        preguntas = cargar_preguntas(RAIZ / "data" / "interfaz" / "preguntas.json", sintomas)
    except (ErrorConocimiento, ErrorPreguntas) as error:
        print("Catálogo inválido:", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1
    print(
        "Base de conocimientos válida: "
        f"{resumen.hechos} hechos, {resumen.diagnosticos} diagnósticos, "
        f"{resumen.reglas} reglas."
    )
    print(f"Cuestionario válido: {len(preguntas)} preguntas con mapeo Sí/No/No estoy seguro.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
