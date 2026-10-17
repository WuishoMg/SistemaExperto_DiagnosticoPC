"""Punto de entrada simple para validar la base desde la raíz del proyecto."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.validacion import ErrorConocimiento, validar_directorio  # noqa: E402


def main() -> int:
    try:
        resumen = validar_directorio(RAIZ / "data" / "conocimiento")
    except ErrorConocimiento as error:
        print("Base de conocimientos inválida:", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1
    print(
        "Base de conocimientos válida: "
        f"{resumen.hechos} hechos, {resumen.diagnosticos} diagnósticos, "
        f"{resumen.reglas} reglas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
