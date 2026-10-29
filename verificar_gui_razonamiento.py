"""Comprueba la instantánea SHA-256 de la GUI con visualizador."""

import hashlib
import json
from pathlib import Path


RAIZ = Path(__file__).resolve().parent
MANIFIESTO = RAIZ / "data" / "interfaz" / "MANIFIESTO_GUI_RAZONAMIENTO.json"


def main() -> int:
    documento = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    errores = []
    for nombre, esperado in documento["archivos"].items():
        ruta = RAIZ / nombre
        if not ruta.is_file():
            errores.append(f"Falta: {nombre}")
        elif hashlib.sha256(ruta.read_bytes()).hexdigest() != esperado:
            errores.append(f"Huella distinta: {nombre}")
    if errores:
        print("\n".join(errores))
        return 1
    print(f"GUI con razonamiento verificada: {len(documento['archivos'])} archivos coinciden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
