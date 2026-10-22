"""Metadatos ordinales de C, separados de las reglas de inferencia."""

import json
from pathlib import Path

from .validacion import ErrorConocimiento


CALIDADES = {1: "indicio", 2: "observación directa", 3: "prueba técnica específica"}
PRIORIDADES = {1: "revisión habitual", 2: "revisión técnica temprana"}


def leer_criterios(ruta: Path) -> dict:
    try:
        with ruta.open(encoding="utf-8") as archivo:
            return json.load(archivo)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ErrorConocimiento([f"{ruta}: no se pudo cargar JSON: {error}"]) from error


def validar_criterios(documento: dict, sintomas: set[str], diagnosticos: set[str]) -> None:
    errores = []
    if not isinstance(documento, dict) or set(documento) != {"version", "evidencia", "prioridades"} or documento.get("version") != 1 or type(documento.get("version")) is not int:
        raise ErrorConocimiento(["Criterios C: se requieren version 1, evidencia y prioridades"])
    for clave, esperados, niveles in (
        ("evidencia", sintomas, CALIDADES),
        ("prioridades", diagnosticos, PRIORIDADES),
    ):
        entradas = documento[clave]
        if not isinstance(entradas, list):
            errores.append(f"Criterios C: {clave} debe ser una lista")
            continue
        ids = []
        for entrada in entradas:
            if not isinstance(entrada, dict) or set(entrada) != {"id", "nivel", "justificacion"}:
                errores.append(f"Criterios C: entrada de {clave} incompleta")
                continue
            identificador, nivel, justificacion = (
                entrada["id"], entrada["nivel"], entrada["justificacion"]
            )
            if not isinstance(identificador, str):
                errores.append(f"Criterios C: ID inválido en {clave}")
                continue
            ids.append(identificador)
            if type(nivel) is not int or nivel not in niveles:
                errores.append(f"Criterios C: nivel inválido para {identificador}")
            if not isinstance(justificacion, str) or not justificacion.strip():
                errores.append(f"Criterios C: falta justificación para {identificador}")
        if len(ids) != len(set(ids)):
            errores.append(f"Criterios C: IDs duplicados en {clave}")
        if set(ids) != esperados:
            errores.append(f"Criterios C: cobertura incorrecta en {clave}: faltan {sorted(esperados - set(ids))}; sobran {sorted(set(ids) - esperados)}")
    if errores:
        raise ErrorConocimiento(errores)
