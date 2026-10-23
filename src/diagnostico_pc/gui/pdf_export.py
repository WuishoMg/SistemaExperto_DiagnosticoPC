"""Exporta una instantánea del resultado gráfico como reporte técnico."""

from pathlib import Path

from .pdf_layout import datos_reporte, dibujar_reporte


def exportar_reporte(
    ruta: Path, resultado: dict, observaciones: dict[str, str], hechos: dict | None = None,
    registradas: set[str] | None = None,
) -> None:
    if resultado.get("modelo") != "C":
        raise ValueError("El resultado de esta consulta no se puede exportar.")
    dibujar_reporte(ruta, datos_reporte(resultado, observaciones, hechos, registradas))
