"""Preguntas visibles y su mapeo explícito a hechos del sistema experto."""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .hechos import EstadoHecho


class RespuestaVisible(str, Enum):
    SI = "si"
    NO = "no"
    NO_ESTOY_SEGURO = "no_estoy_seguro"


@dataclass(frozen=True)
class Pregunta:
    id: str
    hecho: str
    texto: str
    ayuda: str
    estado_si: EstadoHecho
    estado_no: EstadoHecho

    def estado_para(self, respuesta: RespuestaVisible) -> EstadoHecho:
        """Traduce la respuesta visible sin asumir que Sí siempre es verdadero."""
        if respuesta == RespuestaVisible.SI:
            return self.estado_si
        if respuesta == RespuestaVisible.NO:
            return self.estado_no
        if respuesta == RespuestaVisible.NO_ESTOY_SEGURO:
            return EstadoHecho.DESCONOCIDO
        raise ValueError(f"Respuesta visible no admitida: {respuesta!r}")


class ErrorPreguntas(ValueError):
    def __init__(self, errores: list[str]):
        self.errores = errores
        super().__init__("\n".join(errores))


def validar_preguntas(documento: Any, sintomas: set[str]) -> tuple[Pregunta, ...]:
    """Exige una pregunta por síntoma y polaridades Sí/No opuestas."""
    errores: list[str] = []
    if not isinstance(documento, dict):
        raise ErrorPreguntas(["preguntas.json: se esperaba un objeto JSON"])
    if set(documento) != {"version", "preguntas"}:
        errores.append("preguntas.json: se requieren solo 'version' y 'preguntas'")
    if type(documento.get("version")) is not int or documento.get("version") != 1:
        errores.append("preguntas.json.version: debe ser el entero 1")
    registros = documento.get("preguntas")
    if not isinstance(registros, list):
        raise ErrorPreguntas(errores + ["preguntas.json.preguntas: se esperaba una lista"])

    ids: set[str] = set()
    hechos: set[str] = set()
    preguntas: list[Pregunta] = []
    campos = {"id", "hecho", "pregunta", "ayuda", "estado_si", "estado_no"}
    estados = {EstadoHecho.VERDADERO.value, EstadoHecho.FALSO.value}
    for indice, registro in enumerate(registros):
        ruta = f"preguntas[{indice}]"
        if not isinstance(registro, dict):
            errores.append(f"{ruta}: se esperaba un objeto")
            continue
        if set(registro) != campos:
            errores.append(f"{ruta}: campos requeridos: {', '.join(sorted(campos))}")
            continue
        if any(not isinstance(registro[campo], str) or not registro[campo].strip() for campo in campos):
            errores.append(f"{ruta}: todos los campos deben contener texto no vacío")
            continue
        identificador = registro["id"]
        hecho = registro["hecho"]
        if identificador in ids:
            errores.append(f"{ruta}: ID de pregunta duplicado '{identificador}'")
        ids.add(identificador)
        if hecho in hechos:
            errores.append(f"{ruta}: pregunta duplicada para '{hecho}'")
        hechos.add(hecho)
        if hecho not in sintomas:
            errores.append(f"{ruta}: síntoma inexistente '{hecho}'")
        texto = registro["pregunta"]
        if not texto.startswith("¿") or not texto.endswith("?") or hecho in texto:
            errores.append(f"{ruta}.pregunta: debe ser una pregunta visible sin ID interno")
        estado_si = registro["estado_si"]
        estado_no = registro["estado_no"]
        if {estado_si, estado_no} != estados:
            errores.append(f"{ruta}: Sí y No deben mapear a verdadero y falso en orden opuesto")
            continue
        preguntas.append(
            Pregunta(
                id=identificador,
                hecho=hecho,
                texto=texto,
                ayuda=registro["ayuda"],
                estado_si=EstadoHecho(estado_si),
                estado_no=EstadoHecho(estado_no),
            )
        )

    faltantes = sintomas - hechos
    if faltantes:
        errores.append(f"Faltan preguntas para: {', '.join(sorted(faltantes))}")
    if errores:
        raise ErrorPreguntas(errores)
    return tuple(preguntas)


def cargar_preguntas(ruta: Path, sintomas: set[str]) -> tuple[Pregunta, ...]:
    try:
        with ruta.open(encoding="utf-8") as archivo:
            documento = json.load(archivo)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ErrorPreguntas([f"{ruta}: no se pudo cargar JSON: {error}"]) from error
    return validar_preguntas(documento, sintomas)
