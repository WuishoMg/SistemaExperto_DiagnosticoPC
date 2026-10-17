"""Interfaz de texto para consultar el Modelo A."""

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from .modelo_a import DiagnosticoInferido, ModeloA, ResultadoModeloA
from .preguntas import ErrorPreguntas, Pregunta, RespuestaVisible, cargar_preguntas
from .validacion import ErrorConocimiento


RESPUESTAS = {
    "1": RespuestaVisible.SI,
    "s": RespuestaVisible.SI,
    "si": RespuestaVisible.SI,
    "sí": RespuestaVisible.SI,
    "2": RespuestaVisible.NO,
    "n": RespuestaVisible.NO,
    "no": RespuestaVisible.NO,
    "3": RespuestaVisible.NO_ESTOY_SEGURO,
    "": RespuestaVisible.NO_ESTOY_SEGURO,
    "?": RespuestaVisible.NO_ESTOY_SEGURO,
    "no estoy seguro": RespuestaVisible.NO_ESTOY_SEGURO,
}


def preguntar_sintomas(
    preguntas: tuple[Pregunta, ...], entrada: TextIO, salida: TextIO
) -> dict[str, str]:
    """Recoge respuestas visibles usando el mapeo propio de cada pregunta."""
    respuestas: dict[str, str] = {}
    print("Responde con 1/2/3 o con s/n/?.", file=salida)
    for numero, pregunta in enumerate(preguntas, start=1):
        while True:
            print(f"\n{numero:02d}/{len(preguntas)} {pregunta.texto}", file=salida)
            print(f"Ayuda: {pregunta.ayuda}", file=salida)
            print("1. Sí", file=salida)
            print("2. No", file=salida)
            print("3. No estoy seguro", file=salida)
            print("Respuesta: ", end="", file=salida, flush=True)
            respuesta = entrada.readline()
            if respuesta == "":
                raise EOFError("La consulta terminó antes de responder todos los síntomas")
            normalizada = RESPUESTAS.get(respuesta.strip().lower())
            if normalizada is not None:
                respuestas[pregunta.hecho] = pregunta.estado_para(normalizada).value
                break
            print("Respuesta inválida; elige Sí, No o No estoy seguro.", file=salida)
    return respuestas


def _mostrar_diagnostico(diagnostico: DiagnosticoInferido, salida: TextIO) -> None:
    print(f"- {diagnostico.nombre} [{diagnostico.categoria}]", file=salida)
    print(f"  {diagnostico.descripcion}", file=salida)
    print("  Reglas y hechos observados:", file=salida)
    for regla in diagnostico.reglas:
        print(f"  * {regla.id}: {regla.explicacion}", file=salida)
        for condicion in regla.condiciones:
            print(f"    - {condicion.nombre}: {condicion.estado.value}", file=salida)
    print("  Recomendaciones:", file=salida)
    for recomendacion in diagnostico.recomendaciones:
        print(f"  * {recomendacion}", file=salida)


def mostrar_resultado(resultado: ResultadoModeloA, salida: TextIO) -> None:
    print("\n=== Resultado del Modelo A ===", file=salida)
    if resultado.principal is None:
        print("Sin diagnóstico concluyente.", file=salida)
        print(resultado.explicacion_sin_conclusion, file=salida)
        return
    print("Hipótesis principal (ordenada por especificidad, no por probabilidad):", file=salida)
    _mostrar_diagnostico(resultado.principal, salida)
    if resultado.alternativos:
        print("\nOtras hipótesis compatibles:", file=salida)
        for diagnostico in resultado.alternativos:
            _mostrar_diagnostico(diagnostico, salida)
    print("\nEstas son hipótesis; confirme la causa con pruebas técnicas.", file=salida)


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnóstico simbólico básico de fallas en PC")
    parser.add_argument(
        "--respuestas", type=Path,
        help="Archivo JSON opcional con estados por ID de síntoma; omisiones = desconocido",
    )
    opciones = parser.parse_args(argumentos)
    raiz = Path(__file__).resolve().parents[2]
    try:
        modelo = ModeloA.desde_directorio(raiz / "data" / "conocimiento")
        if opciones.respuestas is None:
            preguntas = cargar_preguntas(raiz / "data" / "interfaz" / "preguntas.json", modelo.sintomas)
            respuestas = preguntar_sintomas(preguntas, sys.stdin, sys.stdout)
        else:
            with opciones.respuestas.open(encoding="utf-8") as archivo:
                respuestas = json.load(archivo)
            if not isinstance(respuestas, dict):
                raise ValueError("El archivo de respuestas debe contener un objeto JSON")
        mostrar_resultado(modelo.evaluar(respuestas), sys.stdout)
    except (ErrorConocimiento, ErrorPreguntas, ValueError, OSError, UnicodeError, json.JSONDecodeError, EOFError) as error:
        print(f"No se pudo completar la consulta: {error}", file=sys.stderr)
        return 2
    return 0
