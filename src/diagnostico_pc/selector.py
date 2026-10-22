"""Selección de motores disponibles, independiente del cuestionario."""

from pathlib import Path

from .contratos import ModeloInferencia
from .modelo_a import ModeloA
from .modelo_b import ModeloB
from .modelo_c import ModeloC


MODELOS = ("A", "B", "C")
MODELO_PREDETERMINADO = "A"


class ModeloNoDisponibleError(ValueError):
    """El identificador existe, pero su motor aún no está implementado."""


def seleccionar_modelo(
    nombre: str = MODELO_PREDETERMINADO, directorio_conocimiento: Path | None = None
) -> ModeloInferencia:
    """Carga el motor solicitado sobre el conocimiento correspondiente."""
    clave = nombre.strip().upper()
    if clave not in MODELOS:
        raise ValueError(f"Modelo desconocido: {nombre}. Elige A, B o C.")
    if directorio_conocimiento is None:
        directorio_conocimiento = Path(__file__).resolve().parents[2] / "data" / "conocimiento"
    if clave == "A":
        return ModeloA.desde_directorio(directorio_conocimiento)
    ampliacion = Path(__file__).resolve().parents[2] / "data" / "conocimiento_avance2"
    if clave == "B":
        return ModeloB.desde_directorios(directorio_conocimiento, ampliacion)
    return ModeloC.desde_directorios(directorio_conocimiento, ampliacion)
