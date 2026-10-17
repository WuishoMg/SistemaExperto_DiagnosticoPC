"""Validación estática de la base de conocimientos JSON (versión 1)."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .hechos import EstadoHecho


ID_VALIDO = re.compile(r"^[a-z][a-z0-9_]*$")
CATEGORIAS = {
    "alimentacion_electrica",
    "memoria_ram",
    "video",
    "almacenamiento",
    "temperatura",
    "sistema_operativo",
    "conectividad",
}


class ErrorConocimiento(ValueError):
    """La base tiene uno o más errores estructurales o de referencia."""

    def __init__(self, errores: list[str]):
        self.errores = errores
        super().__init__("\n".join(errores))


@dataclass(frozen=True)
class ResumenConocimiento:
    hechos: int
    diagnosticos: int
    reglas: int


def _objeto(valor: Any, ruta: str, errores: list[str]) -> bool:
    if not isinstance(valor, dict):
        errores.append(f"{ruta}: se esperaba un objeto")
        return False
    return True


def _campos(
    valor: dict, obligatorios: set[str], opcionales: set[str], ruta: str, errores: list[str]
) -> None:
    for campo in sorted(obligatorios - valor.keys()):
        errores.append(f"{ruta}: falta '{campo}'")
    for campo in sorted(valor.keys() - obligatorios - opcionales):
        errores.append(f"{ruta}: campo no permitido '{campo}'")


def _texto(valor: Any, ruta: str, errores: list[str]) -> bool:
    if not isinstance(valor, str) or not valor.strip():
        errores.append(f"{ruta}: se esperaba texto no vacío")
        return False
    return True


def _id(valor: Any, ruta: str, errores: list[str]) -> bool:
    if not _texto(valor, ruta, errores):
        return False
    if ID_VALIDO.fullmatch(valor) is None:
        errores.append(f"{ruta}: identificador inválido '{valor}'")
        return False
    return True


def _lista(valor: Any, ruta: str, errores: list[str]) -> list:
    if not isinstance(valor, list):
        errores.append(f"{ruta}: se esperaba una lista")
        return []
    return valor


def _documento(valor: Any, clave: str, ruta: str, errores: list[str]) -> list:
    if not _objeto(valor, ruta, errores):
        return []
    _campos(valor, {"version", clave}, set(), ruta, errores)
    if type(valor.get("version")) is not int or valor.get("version") != 1:
        errores.append(f"{ruta}.version: debe ser el entero 1")
    return _lista(valor.get(clave), f"{ruta}.{clave}", errores)


def validar_documentos(hechos_doc: Any, diagnosticos_doc: Any, reglas_doc: Any) -> ResumenConocimiento:
    """Valida estructura, relaciones y consistencia sin activar ninguna regla."""
    errores: list[str] = []
    hechos = _documento(hechos_doc, "hechos", "hechos.json", errores)
    diagnosticos = _documento(diagnosticos_doc, "diagnosticos", "diagnosticos.json", errores)
    reglas = _documento(reglas_doc, "reglas", "reglas.json", errores)

    hechos_por_id: dict[str, str] = {}
    diagnosticos_ids: set[str] = set()
    ids_globales: set[str] = set()

    for indice, hecho in enumerate(hechos):
        ruta = f"hechos[{indice}]"
        if not _objeto(hecho, ruta, errores):
            continue
        _campos(hecho, {"id", "nombre", "descripcion", "tipo"}, set(), ruta, errores)
        identificador = hecho.get("id")
        if _id(identificador, f"{ruta}.id", errores):
            if identificador in ids_globales:
                errores.append(f"{ruta}.id: identificador duplicado '{identificador}'")
            else:
                ids_globales.add(identificador)
                hechos_por_id[identificador] = hecho.get("tipo")
        _texto(hecho.get("nombre"), f"{ruta}.nombre", errores)
        _texto(hecho.get("descripcion"), f"{ruta}.descripcion", errores)
        if hecho.get("tipo") not in ("sintoma", "derivado"):
            errores.append(f"{ruta}.tipo: debe ser 'sintoma' o 'derivado'")

    for indice, diagnostico in enumerate(diagnosticos):
        ruta = f"diagnosticos[{indice}]"
        if not _objeto(diagnostico, ruta, errores):
            continue
        _campos(
            diagnostico,
            {"id", "nombre", "categoria", "descripcion", "recomendaciones"},
            set(), ruta, errores,
        )
        identificador = diagnostico.get("id")
        if _id(identificador, f"{ruta}.id", errores):
            if identificador in ids_globales:
                errores.append(f"{ruta}.id: identificador duplicado '{identificador}'")
            else:
                ids_globales.add(identificador)
                diagnosticos_ids.add(identificador)
        _texto(diagnostico.get("nombre"), f"{ruta}.nombre", errores)
        _texto(diagnostico.get("descripcion"), f"{ruta}.descripcion", errores)
        if not isinstance(diagnostico.get("categoria"), str) or diagnostico.get("categoria") not in CATEGORIAS:
            errores.append(f"{ruta}.categoria: categoría no admitida")
        recomendaciones = _lista(
            diagnostico.get("recomendaciones"), f"{ruta}.recomendaciones", errores
        )
        if not recomendaciones:
            errores.append(f"{ruta}.recomendaciones: se requiere al menos una recomendación")
        for j, recomendacion in enumerate(recomendaciones):
            _texto(recomendacion, f"{ruta}.recomendaciones[{j}]", errores)

    for indice, regla in enumerate(reglas):
        ruta = f"reglas[{indice}]"
        if not _objeto(regla, ruta, errores):
            continue
        _campos(regla, {"id", "condiciones", "conclusion", "explicacion"}, set(), ruta, errores)
        identificador = regla.get("id")
        if _id(identificador, f"{ruta}.id", errores):
            if identificador in ids_globales:
                errores.append(f"{ruta}.id: identificador duplicado '{identificador}'")
            else:
                ids_globales.add(identificador)
        _texto(regla.get("explicacion"), f"{ruta}.explicacion", errores)
        condiciones = _lista(regla.get("condiciones"), f"{ruta}.condiciones", errores)
        if not condiciones:
            errores.append(f"{ruta}.condiciones: se requiere al menos una condición")
        estados_por_hecho: dict[str, str] = {}
        for j, condicion in enumerate(condiciones):
            cruta = f"{ruta}.condiciones[{j}]"
            if not _objeto(condicion, cruta, errores):
                continue
            _campos(condicion, {"hecho", "estado"}, set(), cruta, errores)
            hecho_id = condicion.get("hecho")
            if _id(hecho_id, f"{cruta}.hecho", errores):
                if hecho_id not in hechos_por_id:
                    errores.append(f"{cruta}.hecho: referencia inexistente '{hecho_id}'")
                if hecho_id in estados_por_hecho:
                    if estados_por_hecho[hecho_id] == condicion.get("estado"):
                        errores.append(f"{cruta}: condición duplicada para '{hecho_id}'")
                    else:
                        errores.append(f"{cruta}: condiciones contradictorias para '{hecho_id}'")
                estados_por_hecho[hecho_id] = condicion.get("estado")
            if condicion.get("estado") not in (
                EstadoHecho.VERDADERO.value, EstadoHecho.FALSO.value
            ):
                errores.append(f"{cruta}.estado: solo 'verdadero' o 'falso' son condiciones válidas")

        conclusion = regla.get("conclusion")
        cruta = f"{ruta}.conclusion"
        if not _objeto(conclusion, cruta, errores):
            continue
        tipo = conclusion.get("tipo")
        _campos(
            conclusion,
            {"tipo", "id"} | ({"estado"} if tipo == "hecho" else set()),
            set(), cruta, errores,
        )
        conclusion_id = conclusion.get("id")
        if _id(conclusion_id, f"{cruta}.id", errores):
            if tipo == "diagnostico" and conclusion_id not in diagnosticos_ids:
                errores.append(f"{cruta}.id: diagnóstico inexistente '{conclusion_id}'")
            elif tipo == "hecho":
                if conclusion_id not in hechos_por_id:
                    errores.append(f"{cruta}.id: hecho inexistente '{conclusion_id}'")
                elif hechos_por_id[conclusion_id] != "derivado":
                    errores.append(f"{cruta}.id: solo puede concluirse un hecho derivado")
                if conclusion_id in estados_por_hecho:
                    errores.append(f"{cruta}.id: una regla no puede depender de su propia conclusión")
        if tipo not in ("diagnostico", "hecho"):
            errores.append(f"{cruta}.tipo: debe ser 'diagnostico' o 'hecho'")
        if tipo == "hecho" and conclusion.get("estado") not in (
            EstadoHecho.VERDADERO.value, EstadoHecho.FALSO.value
        ):
            errores.append(f"{cruta}.estado: un hecho derivado requiere 'verdadero' o 'falso'")

    if errores:
        raise ErrorConocimiento(errores)
    return ResumenConocimiento(len(hechos), len(diagnosticos), len(reglas))


def validar_directorio(directorio: Path) -> ResumenConocimiento:
    """Carga los tres JSON y devuelve sus cantidades si son válidos."""
    documentos = []
    for nombre in ("hechos.json", "diagnosticos.json", "reglas.json"):
        ruta = directorio / nombre
        try:
            with ruta.open(encoding="utf-8") as archivo:
                documentos.append(json.load(archivo))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ErrorConocimiento([f"{ruta}: no se pudo cargar JSON: {error}"]) from error
    return validar_documentos(*documentos)
