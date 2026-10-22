"""Carga y valida la ampliación independiente de conocimiento del Modelo B."""

import json
from pathlib import Path

from .validacion import ErrorConocimiento, validar_documentos


def leer_ampliacion(directorio: Path) -> tuple[dict, dict]:
    documentos = []
    for nombre in ("hechos.json", "reglas.json"):
        ruta = directorio / nombre
        try:
            with ruta.open(encoding="utf-8") as archivo:
                documentos.append(json.load(archivo))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ErrorConocimiento([f"{ruta}: no se pudo cargar JSON: {error}"]) from error
    return tuple(documentos)


def validar_ampliacion(
    hechos_base: dict, diagnosticos_base: dict, reglas_base: dict,
    hechos_nuevos: dict, reglas_nuevas: dict,
) -> tuple[dict, dict, dict]:
    """Valida la unión sin alterar los documentos originales ni permitir ciclos."""
    errores = []
    for documento, clave, nombre in (
        (hechos_nuevos, "hechos", "hechos.json"),
        (reglas_nuevas, "reglas", "reglas.json"),
    ):
        if not isinstance(documento, dict) or set(documento) != {"version", clave}:
            errores.append(f"Ampliación {nombre}: se requieren solo version y {clave}")
        elif type(documento.get("version")) is not int or documento["version"] != 1 or not isinstance(documento.get(clave), list):
            errores.append(f"Ampliación {nombre}: versión 1 y lista {clave} obligatorias")
    if errores:
        raise ErrorConocimiento(errores)

    validar_documentos(hechos_base, diagnosticos_base, reglas_base)
    hechos = {"version": 1, "hechos": [*hechos_base["hechos"], *hechos_nuevos["hechos"]]}
    reglas = {"version": 1, "reglas": [*reglas_base["reglas"], *reglas_nuevas["reglas"]]}
    validar_documentos(hechos, diagnosticos_base, reglas)

    for hecho in hechos_nuevos["hechos"]:
        if isinstance(hecho, dict) and hecho.get("tipo") != "derivado":
            errores.append("La ampliación B solo puede añadir hechos derivados")
    ids_nuevos = {hecho.get("id") for hecho in hechos_nuevos["hechos"] if isinstance(hecho, dict)}
    for regla in reglas_nuevas["reglas"]:
        if not isinstance(regla, dict):
            continue
        conclusion = regla.get("conclusion")
        if isinstance(conclusion, dict) and conclusion.get("tipo") == "hecho":
            if conclusion.get("id") not in ids_nuevos:
                errores.append("Una regla B solo puede concluir hechos de la ampliación")
    if errores:
        raise ErrorConocimiento(errores)

    dependencias = {identificador: set() for identificador in ids_nuevos}
    for regla in reglas_nuevas["reglas"]:
        conclusion = regla["conclusion"]
        if conclusion["tipo"] == "hecho":
            dependencias[conclusion["id"]].update(
                condicion["hecho"] for condicion in regla["condiciones"]
                if condicion["hecho"] in ids_nuevos
            )
    visitando: set[str] = set()
    visitados: set[str] = set()

    def recorrer(hecho_id: str) -> None:
        if hecho_id in visitando:
            raise ErrorConocimiento([f"Ciclo entre hechos derivados: {hecho_id}"])
        if hecho_id in visitados:
            return
        visitando.add(hecho_id)
        for dependencia in sorted(dependencias[hecho_id]):
            recorrer(dependencia)
        visitando.remove(hecho_id)
        visitados.add(hecho_id)

    for identificador in sorted(ids_nuevos):
        recorrer(identificador)
    return hechos, diagnosticos_base, reglas
