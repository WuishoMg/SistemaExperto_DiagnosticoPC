"""Representación de observaciones; no contiene un motor de inferencia."""

from enum import Enum
from typing import Mapping


class EstadoHecho(str, Enum):
    VERDADERO = "verdadero"
    FALSO = "falso"
    DESCONOCIDO = "desconocido"


def normalizar_observaciones(
    identificadores: set[str], respuestas: Mapping[str, str]
) -> dict[str, EstadoHecho]:
    """Completa respuestas ausentes como desconocidas, sin inferir negaciones."""
    desconocidos = set(respuestas) - identificadores
    if desconocidos:
        retirados = {
            "s_no_enciende": "s_led_encendido y s_ventiladores_giran",
            "s_lentitud_o_congelamientos": "s_lentitud_programas y s_congelamientos",
            "s_proceso_consumo_alto": "s_proceso_cpu_alto y s_proceso_disco_alto",
        }
        ambiguos = [hecho for hecho in sorted(desconocidos) if hecho in retirados]
        if ambiguos:
            detalle = "; ".join(f"{hecho} → {retirados[hecho]}" for hecho in ambiguos)
            raise ValueError(
                "Hechos compuestos retirados. Registra cada observación por separado: " + detalle
            )
        raise ValueError(f"Hechos no definidos: {', '.join(sorted(desconocidos))}")

    normalizadas = {identificador: EstadoHecho.DESCONOCIDO for identificador in identificadores}
    for identificador, valor in respuestas.items():
        if not isinstance(valor, str):
            raise ValueError(f"Estado inválido para {identificador}: {valor!r}")
        try:
            normalizadas[identificador] = EstadoHecho(valor)
        except ValueError as error:
            raise ValueError(f"Estado inválido para {identificador}: {valor!r}") from error
    return normalizadas


def condicion_satisfecha(estado_actual: EstadoHecho, estado_requerido: EstadoHecho) -> bool:
    """Solo una observación explícita satisface la condición exigida."""
    if estado_requerido == EstadoHecho.DESCONOCIDO:
        raise ValueError("Una regla diagnóstica no puede exigir 'desconocido'")
    return estado_actual == estado_requerido
