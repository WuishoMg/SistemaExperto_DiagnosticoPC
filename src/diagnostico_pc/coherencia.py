"""Incompatibilidades entre observaciones del mismo intento de uso."""

from dataclasses import dataclass
from typing import Mapping

from .hechos import EstadoHecho


@dataclass(frozen=True)
class Contradiccion:
    explicacion: str
    preguntas: tuple[str, ...]


RESTRICCIONES = (
    ("s_reinicios_post", EstadoHecho.VERDADERO, "s_post_completado", EstadoHecho.VERDADERO,
     "Indicaste que se reinicia antes de mostrar el sistema, pero también que llegó a mostrarlo.", ("p06", "p26")),
    ("s_reinicios_post", EstadoHecho.VERDADERO, "s_so_no_inicia", EstadoHecho.FALSO,
     "Indicaste reinicios antes de iniciar el sistema, pero también que pudiste usarlo en el mismo intento.", ("p06", "p16")),
)


def detectar_contradicciones(hechos: Mapping[str, EstadoHecho]) -> tuple[Contradiccion, ...]:
    """Nunca trata un hecho desconocido como falso ni compara intentos distintos."""
    return tuple(
        Contradiccion(mensaje, preguntas)
        for primero, estado_primero, segundo, estado_segundo, mensaje, preguntas in RESTRICCIONES
        if hechos.get(primero, EstadoHecho.DESCONOCIDO) == estado_primero
        and hechos.get(segundo, EstadoHecho.DESCONOCIDO) == estado_segundo
    )
