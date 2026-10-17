"""Ejecuta la consulta por consola desde la raíz del proyecto."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.consola import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
