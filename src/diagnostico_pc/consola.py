"""Interfaz de texto para consultar el Modelo A."""

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from .hechos import EstadoHecho
from .modelo_a import DiagnosticoInferido, ModeloA, ResultadoModeloA
from .validacion import ErrorConocimiento


RESPUESTAS = {
    "s": EstadoHecho.VERDADERO.value,
    "si": EstadoHecho.VERDADERO.value,
    "sí": EstadoHecho.VERDADERO.value,
    "verdadero": EstadoHecho.VERDADERO.value,
    "n": EstadoHecho.FALSO.value,
    "no": EstadoHecho.FALSO.value,
    "falso": EstadoHecho.FALSO.value,
    "": EstadoHecho.DESCONOCIDO.value,
    "?": EstadoHecho.DESCONOCIDO.value,
    "desconocido": EstadoHecho.DESCONOCIDO.value,
}


def preguntar_sintomas(modelo: ModeloA, entrada: TextIO, salida: TextIO) -> dict[str, str]:
    """Pregunta por todos los síntomas; Enter conserva el estado desconocido."""
    respuestas: dict[str, str] = {}
    sintomas = [hecho for hecho in modelo.hechos.values() if hecho["tipo"] == "sintoma"]
    print("Responda s (sí), n (no) o Enter/? (desconocido).", file=salida)
    for numero, hecho in enumerate(sintomas, start=1):
        while True:
            print(f"{numero:02d}/{len(sintomas)} {hecho['nombre']} [s/n/?]: ", end="", file=salida, flush=True)
            respuesta = entrada.readline()
            if respuesta == "":
                raise EOFError("La consulta terminó antes de responder todos los síntomas")
            normalizada = RESPUESTAS.get(respuesta.strip().lower())
            if normalizada is not None:
                respuestas[hecho["id"]] = normalizada
                break
            print("Respuesta inválida; escriba s, n o ?.", file=salida)
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
    directorio = Path(__file__).resolve().parents[2] / "data" / "conocimiento"
    try:
        modelo = ModeloA.desde_directorio(directorio)
        if opciones.respuestas is None:
            respuestas = preguntar_sintomas(modelo, sys.stdin, sys.stdout)
        else:
            with opciones.respuestas.open(encoding="utf-8") as archivo:
                respuestas = json.load(archivo)
            if not isinstance(respuestas, dict):
                raise ValueError("El archivo de respuestas debe contener un objeto JSON")
        mostrar_resultado(modelo.evaluar(respuestas), sys.stdout)
    except (ErrorConocimiento, ValueError, OSError, UnicodeError, json.JSONDecodeError, EOFError) as error:
        print(f"No se pudo completar la consulta: {error}", file=sys.stderr)
        return 2
    return 0
