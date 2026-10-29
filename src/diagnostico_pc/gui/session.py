"""Estado de una consulta gráfica, independiente de Qt y de QML."""

from pathlib import Path

from diagnostico_pc.coherencia import Contradiccion
from diagnostico_pc.gestor_preguntas import GestorPreguntas
from diagnostico_pc.preguntas import RespuestaVisible, cargar_preguntas
from diagnostico_pc.rutas import cargar_rutas
from diagnostico_pc.selector import seleccionar_modelo

from .serialization import serializar_resultado
from .reasoning_graph import construir_grafo


RAIZ_PROYECTO = Path(__file__).resolve().parents[3]

MENSAJES_TERMINALES = {
    "@resultado": "Se completaron las comprobaciones útiles de esta ruta.",
    "@insuficiente": "No hay observaciones suficientes para continuar esta ruta de forma útil.",
    "@bloqueo_energia": "Las señales de encendido no permiten continuar con la falla elegida. Puedes iniciar otro diagnóstico.",
    "@bloqueo_imagen": "Ahora aparece imagen y no se observó una distorsión; puedes elegir otro diagnóstico.",
    "@bloqueo_sistema": "Hay energía e imagen, pero el sistema no inicia. Puedes cambiar al diagnóstico del sistema.",
    "@patron_red_sin_causa": "Se registró un problema de conexión, pero estas observaciones no identifican todavía su causa.",
    "@error_uso_sin_causa": "Se registró un error durante el uso del sistema, pero estas observaciones no identifican todavía su causa.",
}


class SesionGrafica:
    def __init__(self, raiz: Path = RAIZ_PROYECTO):
        self.raiz = raiz
        self.modelo_c = seleccionar_modelo("C", raiz / "data" / "conocimiento")
        self.preguntas = cargar_preguntas(
            raiz / "data" / "interfaz" / "preguntas.json", self.modelo_c.sintomas
        )
        self.rutas = cargar_rutas(raiz / "data" / "interfaz" / "rutas.json", self.preguntas)
        self.gestor: GestorPreguntas | None = None
        self.pantalla = "bienvenida"
        self.resultado: dict = {}
        self.grafo: dict = {}
        self.error = ""

    def _invalidar(self) -> None:
        self.resultado = {}
        self.grafo = {}
        self.error = ""

    def ir_a_seleccion(self) -> None:
        self.pantalla = "seleccion"

    def elegir_categoria(self, categoria: str) -> None:
        self.gestor = GestorPreguntas(self.preguntas, self.rutas, categoria)
        self._invalidar()
        self.pantalla = "preguntas"

    def iniciar_nueva_consulta(self, categoria: str) -> None:
        # GestorPreguntas valida el ID antes de reemplazar la sesión.
        self.elegir_categoria(categoria)

    def responder(self, pregunta_id: str, respuesta: str) -> None:
        gestor = self._exigir_gestor()
        gestor.responder(pregunta_id, RespuestaVisible(respuesta))
        self._invalidar()
        self.pantalla = "preguntas"

    def volver(self) -> None:
        gestor = self._exigir_gestor()
        if gestor.volver() is not None:
            self._invalidar()
            self.pantalla = "preguntas"
        elif self.pantalla == "resultados":
            self._invalidar()
            self.pantalla = "preguntas"

    def editar(self, indice: int) -> None:
        self._exigir_gestor().editar(indice)
        self._invalidar()
        self.pantalla = "preguntas"

    def ver_resultado(self) -> dict:
        gestor = self._exigir_gestor()
        if gestor.contradicciones:
            raise ValueError("Corrige las respuestas contradictorias antes de ver el resultado.")
        if gestor.estado_final == "@bloqueo_energia":
            raise ValueError(MENSAJES_TERMINALES["@bloqueo_energia"])
        self.pantalla = "analisis"
        try:
            self.resultado = serializar_resultado(self.modelo_c.evaluar(gestor.observaciones))
        except Exception:
            self.pantalla = "preguntas"
            raise
        self.pantalla = "resultados"
        return self.resultado

    def ver_razonamiento(self) -> dict:
        if self.pantalla != "resultados" or not self.resultado:
            raise ValueError("Primero consulta un resultado para visualizar el razonamiento.")
        gestor = self._exigir_gestor()
        if not self.grafo:
            self.grafo = construir_grafo(
                self.resultado, gestor.historial, gestor.preguntas,
                self.modelo_c.hechos, self.modelo_c.reglas, gestor.categoria_actual,
            )
        self.pantalla = "razonamiento"
        return self.grafo

    def volver_a_resultados(self) -> None:
        if self.pantalla != "razonamiento":
            raise ValueError("La visualización de razonamiento no está abierta.")
        self.pantalla = "resultados"

    def comparar_modelos(self) -> list[dict]:
        gestor = self._exigir_gestor()
        if gestor.contradicciones or gestor.estado_final == "@bloqueo_energia":
            raise ValueError("Corrige o cambia la consulta antes de comparar los modelos.")
        return [
            serializar_resultado(
                seleccionar_modelo(nombre, self.raiz / "data" / "conocimiento").evaluar(
                    gestor.observaciones
                ), nombre
            )
            for nombre in ("A", "B", "C")
        ]

    def _exigir_gestor(self) -> GestorPreguntas:
        if self.gestor is None:
            raise ValueError("Primero elige una categoría.")
        return self.gestor

    def estado(self) -> dict:
        gestor = self.gestor
        pregunta = gestor.siguiente() if gestor else None
        contradicciones: tuple[Contradiccion, ...] = gestor.contradicciones if gestor else ()
        terminal = gestor.estado_final if gestor else None
        return {
            "pantalla": self.pantalla,
            "categorias": [{"id": c.id, "nombre": c.nombre} for c in self.rutas.categorias],
            "categoriaActual": gestor.categoria_actual if gestor else "",
            "preguntaActual": (
                {"id": pregunta.id, "texto": pregunta.texto, "ayuda": pregunta.ayuda}
                if pregunta else {}
            ),
            "historial": [
                {
                    "indice": i,
                    "preguntaId": registro.pregunta_id,
                    "texto": gestor.preguntas[registro.pregunta_id].texto,
                    "respuesta": registro.respuesta.value,
                }
                for i, registro in enumerate(gestor.historial)
            ] if gestor else [],
            "terminal": terminal or "",
            "mensajeTerminal": MENSAJES_TERMINALES.get(terminal, ""),
            "contradicciones": [
                {"explicacion": c.explicacion, "preguntas": list(c.preguntas)}
                for c in contradicciones
            ],
            "analizando": self.pantalla == "analisis",
            "resultado": self.resultado,
            "grafo": self.grafo,
            "error": self.error,
        }
