"""Puente QObject entre QML y la sesión Python."""

from pathlib import Path

from PySide6.QtCore import QObject, Property, QTimer, QUrl, Signal, Slot

from .pdf_export import exportar_reporte
from .session import SesionGrafica


class PuenteDiagnostico(QObject):
    estadoCambiado = Signal()

    def __init__(self, sesion: SesionGrafica | None = None):
        super().__init__()
        self.sesion = sesion or SesionGrafica()
        self._comparacion: list[dict] = []

    def _estado(self, clave):
        return self.sesion.estado()[clave]

    pantalla = Property(str, lambda self: self._estado("pantalla"), notify=estadoCambiado)
    categorias = Property("QVariantList", lambda self: self._estado("categorias"), notify=estadoCambiado)
    categoriaActual = Property(str, lambda self: self._estado("categoriaActual"), notify=estadoCambiado)
    preguntaActual = Property("QVariantMap", lambda self: self._estado("preguntaActual"), notify=estadoCambiado)
    historial = Property("QVariantList", lambda self: self._estado("historial"), notify=estadoCambiado)
    terminal = Property(str, lambda self: self._estado("terminal"), notify=estadoCambiado)
    mensajeTerminal = Property(str, lambda self: self._estado("mensajeTerminal"), notify=estadoCambiado)
    contradicciones = Property("QVariantList", lambda self: self._estado("contradicciones"), notify=estadoCambiado)
    analizando = Property(bool, lambda self: self._estado("analizando"), notify=estadoCambiado)
    resultado = Property("QVariantMap", lambda self: self._estado("resultado"), notify=estadoCambiado)
    grafo = Property("QVariantMap", lambda self: self._estado("grafo"), notify=estadoCambiado)
    error = Property(str, lambda self: self._estado("error"), notify=estadoCambiado)
    comparacion = Property("QVariantList", lambda self: self._comparacion, notify=estadoCambiado)

    @Property(str, notify=estadoCambiado)
    def recursoMascota(self):
        carpeta = Path(__file__).with_name("assets") / "mascota"
        pantalla = self.sesion.pantalla
        candidatos = {
            "bienvenida": ("mascota-saludando.png", "mascota-saludando.jpg"),
            "seleccion": ("mascota-default1.png",),
            "preguntas": ("mascota-escribiendo1.png",),
            "analisis": ("mascota-analizando1.png",),
            "resultados": ("mascota-idea1.png",),
        }.get(pantalla, ())
        for extension in ("png", "webp", "svg", "gif", "jpg"):
            candidatos += (f"{pantalla}.{extension}",)
        for nombre in candidatos:
            ruta = carpeta / nombre
            if ruta.is_file():
                return QUrl.fromLocalFile(str(ruta)).toString()
        return ""

    def _accion(self, funcion, *args):
        try:
            funcion(*args)
            self.sesion.error = ""
            self._comparacion = []
        except (ValueError, OSError, RuntimeError) as error:
            self.sesion.error = str(error)
        self.estadoCambiado.emit()

    @Slot()
    def irASeleccion(self):
        self._accion(self.sesion.ir_a_seleccion)

    @Slot(str)
    def elegirCategoria(self, categoria):
        self._accion(self.sesion.elegir_categoria, categoria)

    @Slot(str, str)
    def responder(self, pregunta_id, respuesta):
        self._accion(self.sesion.responder, pregunta_id, respuesta)

    @Slot()
    def volver(self):
        self._accion(self.sesion.volver)

    @Slot()
    def verRazonamiento(self):
        self._accion(self.sesion.ver_razonamiento)

    @Slot()
    def volverAResultados(self):
        self._accion(self.sesion.volver_a_resultados)

    @Slot(int)
    def editar(self, indice):
        self._accion(self.sesion.editar, indice)

    @Slot(str)
    def iniciarNuevaConsulta(self, categoria):
        self._accion(self.sesion.iniciar_nueva_consulta, categoria)

    @Slot()
    def verResultado(self):
        if self.sesion.gestor is None:
            self._accion(self.sesion.ver_resultado)
            return
        if self.sesion.gestor.contradicciones or self.sesion.gestor.estado_final == "@bloqueo_energia":
            self._accion(self.sesion.ver_resultado)
            return
        self.sesion.pantalla = "analisis"
        self.sesion.error = ""
        self.estadoCambiado.emit()
        gestor_pendiente = self.sesion.gestor
        QTimer.singleShot(0, lambda: self._evaluar(gestor_pendiente))

    def _evaluar(self, gestor_pendiente):
        if self.sesion.gestor is gestor_pendiente and self.sesion.pantalla == "analisis":
            self._accion(self.sesion.ver_resultado)

    @Slot()
    def compararModelos(self):
        try:
            self._comparacion = self.sesion.comparar_modelos()
            self.sesion.error = ""
        except (ValueError, OSError, RuntimeError) as error:
            self.sesion.error = str(error)
        self.estadoCambiado.emit()

    @Slot(str)
    def exportarPdf(self, ruta):
        try:
            if not self.sesion.resultado:
                raise ValueError("Primero consulta un resultado para exportarlo.")
            url = QUrl(ruta)
            destino = Path(url.toLocalFile() if url.isLocalFile() else ruta)
            exportar_reporte(
                destino, self.sesion.resultado, self.sesion.gestor.observaciones,
                self.sesion.modelo_c.hechos,
                {self.sesion.gestor.preguntas[r.pregunta_id].hecho for r in self.sesion.gestor.historial},
            )
            self.sesion.error = ""
        except (ValueError, OSError, RuntimeError) as error:
            self.sesion.error = str(error)
        self.estadoCambiado.emit()
