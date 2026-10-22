"""Contrato estructural de inferencia; no contiene reglas ni cuestionarios."""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .modelo_a import DiagnosticoInferido, MemoriaTrabajo


@runtime_checkable
class ResultadoInferencia(Protocol):
    """Campos que consume la presentación de un resultado diagnóstico."""

    memoria: MemoriaTrabajo
    principal: DiagnosticoInferido | None
    alternativos: tuple[DiagnosticoInferido, ...]
    explicacion_sin_conclusion: str | None


@runtime_checkable
class ModeloInferencia(Protocol):
    """Un modelo recibe hechos trivalentes y devuelve evidencia explicable."""

    sintomas: set[str]

    def evaluar(self, respuestas: Mapping[str, str]) -> ResultadoInferencia:
        ...
