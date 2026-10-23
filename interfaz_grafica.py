"""Inicia la aplicación de escritorio sin alterar la consola existente."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.gui.main import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
