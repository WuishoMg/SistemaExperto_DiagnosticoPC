"""Sesión de preguntas: recorre el grafo y adquiere hechos sin inferir diagnósticos."""

from dataclasses import dataclass

from .coherencia import Contradiccion, detectar_contradicciones
from .hechos import EstadoHecho
from .preguntas import Pregunta, RespuestaVisible
from .rutas import CatalogoRutas, TERMINALES


@dataclass(frozen=True)
class RespuestaRegistrada:
    pregunta_id: str
    respuesta: RespuestaVisible


class GestorPreguntas:
    def __init__(self, preguntas: tuple[Pregunta, ...], rutas: CatalogoRutas, categoria: str):
        if categoria not in rutas.por_id:
            raise ValueError(f"Categoría desconocida: {categoria}")
        self.preguntas = {pregunta.id: pregunta for pregunta in preguntas}
        self.rutas = rutas
        self.categoria_elegida = categoria
        self.historial: list[RespuestaRegistrada] = []

    @property
    def categoria_actual(self) -> str:
        return self.categoria_elegida

    @property
    def hechos(self) -> dict[str, EstadoHecho]:
        estados = {pregunta.hecho: EstadoHecho.DESCONOCIDO for pregunta in self.preguntas.values()}
        for registro in self.historial:
            pregunta = self.preguntas[registro.pregunta_id]
            estados[pregunta.hecho] = pregunta.estado_para(registro.respuesta)
        return estados

    @property
    def observaciones(self) -> dict[str, str]:
        return {hecho: estado.value for hecho, estado in self.hechos.items()}

    @property
    def contradicciones(self) -> tuple[Contradiccion, ...]:
        return detectar_contradicciones(self.hechos)

    def _posición(self) -> str:
        categoria = self.rutas.por_id[self.categoria_elegida]
        registros = {registro.pregunta_id: registro.respuesta for registro in self.historial}
        hechos = self.hechos
        posicion = categoria.inicio
        vistos: set[str] = set()
        while posicion not in TERMINALES:
            if posicion in vistos:
                raise RuntimeError(f"Ciclo al recorrer la ruta {self.categoria_elegida}")
            vistos.add(posicion)
            respuesta = registros.get(posicion)
            if respuesta is None:
                return posicion
            posicion = categoria.nodos[posicion].destino(respuesta, hechos)
        return posicion

    @property
    def estado_final(self) -> str | None:
        if self.contradicciones:
            return None
        posicion = self._posición()
        return posicion if posicion in TERMINALES else None

    def siguiente(self) -> Pregunta | None:
        if self.contradicciones:
            return None
        posicion = self._posición()
        return None if posicion in TERMINALES else self.preguntas[posicion]

    def responder(self, pregunta_id: str, respuesta: RespuestaVisible) -> None:
        siguiente = self.siguiente()
        if siguiente is None or siguiente.id != pregunta_id:
            raise ValueError("La pregunta no corresponde al paso actual")
        if not isinstance(respuesta, RespuestaVisible):
            raise ValueError("Respuesta visible inválida")
        self.historial.append(RespuestaRegistrada(pregunta_id, respuesta))

    def volver(self) -> RespuestaRegistrada | None:
        return self.historial.pop() if self.historial else None

    def editar(self, indice: int) -> RespuestaRegistrada:
        """Elimina la respuesta elegida y las posteriores, que dependían de ella."""
        if not 0 <= indice < len(self.historial):
            raise ValueError("Número de respuesta fuera del historial")
        registro = self.historial[indice]
        del self.historial[indice:]
        return registro

    def cambiar_categoria(self, categoria: str) -> None:
        """Inicia una consulta nueva; la consola debe pedir confirmación antes."""
        if categoria not in self.rutas.por_id:
            raise ValueError(f"Categoría desconocida: {categoria}")
        self.categoria_elegida = categoria
        self.historial.clear()
