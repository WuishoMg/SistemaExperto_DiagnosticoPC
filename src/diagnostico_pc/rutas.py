"""Grafo declarativo de adquisición de hechos, separado del Modelo A."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .hechos import EstadoHecho
from .preguntas import Pregunta, RespuestaVisible


class ErrorRutas(ValueError):
    pass


CLAVES_RESPUESTA = ("si", "no", "desconocido")
RESPUESTA_A_CLAVE = {
    RespuestaVisible.SI: "si",
    RespuestaVisible.NO: "no",
    RespuestaVisible.NO_ESTOY_SEGURO: "desconocido",
}
TERMINALES = {
    "@resultado", "@insuficiente", "@bloqueo_energia", "@bloqueo_imagen",
    "@bloqueo_sistema", "@patron_red_sin_causa", "@error_uso_sin_causa",
}


@dataclass(frozen=True)
class CondicionRuta:
    hecho: str
    estado: EstadoHecho

    def coincide(self, hechos: dict[str, EstadoHecho]) -> bool:
        return hechos[self.hecho] == self.estado


@dataclass(frozen=True)
class OpcionDestino:
    ir: str
    cuando: tuple[CondicionRuta, ...] = ()

    def coincide(self, hechos: dict[str, EstadoHecho]) -> bool:
        return all(condicion.coincide(hechos) for condicion in self.cuando)


@dataclass(frozen=True)
class Nodo:
    pregunta_id: str
    transiciones: dict[str, tuple[OpcionDestino, ...]]

    def destino(self, respuesta: RespuestaVisible, hechos: dict[str, EstadoHecho]) -> str:
        for opcion in self.transiciones[RESPUESTA_A_CLAVE[respuesta]]:
            if opcion.coincide(hechos):
                return opcion.ir
        raise RuntimeError(f"Transición sin destino en {self.pregunta_id}")


@dataclass(frozen=True)
class Categoria:
    id: str
    nombre: str
    inicio: str
    nodos: dict[str, Nodo]


@dataclass(frozen=True)
class CatalogoRutas:
    categorias: tuple[Categoria, ...]

    @property
    def por_id(self) -> dict[str, Categoria]:
        return {categoria.id: categoria for categoria in self.categorias}


def _leer_opciones(valor: Any, pregunta_id: str, clave: str, hechos: set[str]) -> tuple[OpcionDestino, ...]:
    opciones = [dict(ir=valor)] if isinstance(valor, str) else valor
    if not isinstance(opciones, list) or not opciones:
        raise ErrorRutas(f"{pregunta_id}.{clave}: destino inválido")
    leidas: list[OpcionDestino] = []
    for indice, opcion in enumerate(opciones):
        if not isinstance(opcion, dict) or set(opcion) not in ({"ir"}, {"ir", "cuando"}):
            raise ErrorRutas(f"{pregunta_id}.{clave}: opción inválida")
        ir = opcion["ir"]
        if not isinstance(ir, str) or not ir:
            raise ErrorRutas(f"{pregunta_id}.{clave}: destino vacío")
        cuando = opcion.get("cuando", [])
        if not isinstance(cuando, list) or ("cuando" in opcion and not cuando):
            raise ErrorRutas(f"{pregunta_id}.{clave}: condición inválida")
        condiciones: list[CondicionRuta] = []
        for condicion in cuando:
            if (not isinstance(condicion, dict) or set(condicion) != {"hecho", "estado"}
                    or not isinstance(condicion["hecho"], str)
                    or condicion["hecho"] not in hechos
                    or not isinstance(condicion["estado"], str)
                    or condicion["estado"] not in {estado.value for estado in EstadoHecho}):
                raise ErrorRutas(f"{pregunta_id}.{clave}: hecho o estado inválido")
            condiciones.append(CondicionRuta(condicion["hecho"], EstadoHecho(condicion["estado"])))
        if len({c.hecho for c in condiciones}) != len(condiciones):
            raise ErrorRutas(f"{pregunta_id}.{clave}: condiciones repetidas")
        if indice < len(opciones) - 1 and not condiciones:
            raise ErrorRutas(f"{pregunta_id}.{clave}: opción general antes de las específicas")
        leidas.append(OpcionDestino(ir, tuple(condiciones)))
    if leidas[-1].cuando:
        raise ErrorRutas(f"{pregunta_id}.{clave}: falta un destino por defecto")
    return tuple(leidas)


def validar_rutas(documento: Any, preguntas: tuple[Pregunta, ...]) -> CatalogoRutas:
    if not isinstance(documento, dict) or set(documento) != {"version", "categorias"} or documento["version"] != 2:
        raise ErrorRutas("rutas.json requiere version 2 y categorias")
    if not isinstance(documento["categorias"], list):
        raise ErrorRutas("categorias debe ser una lista")
    preguntas_ids = {pregunta.id for pregunta in preguntas}
    hechos = {pregunta.hecho for pregunta in preguntas}
    categorias: list[Categoria] = []
    ids: set[str] = set()
    cubiertas: set[str] = set()
    for registro in documento["categorias"]:
        if not isinstance(registro, dict) or set(registro) != {"id", "nombre", "inicio", "nodos"}:
            raise ErrorRutas("Cada categoría requiere id, nombre, inicio y nodos")
        ident, nombre, inicio, nodos_doc = (registro[c] for c in ("id", "nombre", "inicio", "nodos"))
        if not isinstance(ident, str) or not ident or ident in ids or not isinstance(nombre, str) or not nombre.strip():
            raise ErrorRutas("ID o nombre de categoría inválido o duplicado")
        if (not isinstance(inicio, str) or not isinstance(nodos_doc, dict)
                or not nodos_doc or inicio not in nodos_doc):
            raise ErrorRutas(f"Inicio o nodos inválidos en {ident}")
        if not set(nodos_doc) <= preguntas_ids:
            raise ErrorRutas(f"La ruta {ident} referencia preguntas inexistentes")
        nodos: dict[str, Nodo] = {}
        for pregunta_id, transiciones_doc in nodos_doc.items():
            if not isinstance(transiciones_doc, dict) or set(transiciones_doc) != set(CLAVES_RESPUESTA):
                raise ErrorRutas(f"{ident}.{pregunta_id}: se requieren Sí, No y desconocido")
            transiciones = {
                clave: _leer_opciones(transiciones_doc[clave], pregunta_id, clave, hechos)
                for clave in CLAVES_RESPUESTA
            }
            nodos[pregunta_id] = Nodo(pregunta_id, transiciones)
        for nodo in nodos.values():
            for opciones in nodo.transiciones.values():
                for opcion in opciones:
                    if opcion.ir not in nodos and opcion.ir not in TERMINALES:
                        raise ErrorRutas(f"{ident}.{nodo.pregunta_id}: destino inexistente {opcion.ir}")
        visitados: set[str] = set()
        camino: set[str] = set()
        def recorrer(pregunta_id: str) -> None:
            if pregunta_id in camino:
                raise ErrorRutas(f"Ciclo en {ident}.{pregunta_id}")
            if pregunta_id in visitados:
                return
            camino.add(pregunta_id)
            for opciones in nodos[pregunta_id].transiciones.values():
                for opcion in opciones:
                    if opcion.ir in nodos:
                        recorrer(opcion.ir)
            camino.remove(pregunta_id)
            visitados.add(pregunta_id)
        recorrer(inicio)
        if visitados != set(nodos):
            raise ErrorRutas(f"Nodos inalcanzables en {ident}: {', '.join(sorted(set(nodos)-visitados))}")
        ids.add(ident)
        cubiertas.update(nodos)
        categorias.append(Categoria(ident, nombre, inicio, nodos))
    requeridas = {"alimentacion", "lentitud", "video", "sistema", "temperatura", "conectividad", "general"}
    if ids != requeridas or cubiertas != preguntas_ids:
        raise ErrorRutas("Faltan categorías o preguntas sin ruta")
    return CatalogoRutas(tuple(categorias))


def cargar_rutas(ruta: Path, preguntas: tuple[Pregunta, ...]) -> CatalogoRutas:
    try:
        with ruta.open(encoding="utf-8") as archivo:
            documento = json.load(archivo)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ErrorRutas(f"No se pudo cargar {ruta}: {error}") from error
    return validar_rutas(documento, preguntas)
