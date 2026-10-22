"""Orden simbólico de hipótesis después del cierre inferencial del Modelo B."""

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .conocimiento_b import leer_ampliacion
from .conocimiento_c import CALIDADES, leer_criterios, validar_criterios
from .hechos import EstadoHecho
from .modelo_a import DiagnosticoInferido, MemoriaTrabajo
from .modelo_b import ModeloB, TrazaInferencia
from .validacion import leer_documentos


@dataclass(frozen=True)
class CriterioHipotesis:
    diagnostico_id: str
    observaciones: tuple[str, ...]
    calidad: int
    especificidad: int
    prioridad: int

    @property
    def clave(self) -> tuple[int, int, int, str]:
        return (-self.calidad, -self.especificidad, -self.prioridad, self.diagnostico_id)


def motivo_precedencia(primero: CriterioHipotesis, segundo: CriterioHipotesis) -> str:
    if primero.calidad != segundo.calidad:
        return f"calidad de evidencia ({CALIDADES[primero.calidad]} frente a {CALIDADES[segundo.calidad]})"
    if primero.especificidad != segundo.especificidad:
        return f"observaciones originales distintas ({primero.especificidad} frente a {segundo.especificidad})"
    if primero.prioridad != segundo.prioridad:
        return f"prioridad técnica ordinal ({primero.prioridad} frente a {segundo.prioridad})"
    return "ID estable en empate de los tres criterios anteriores"


@dataclass(frozen=True)
class ResultadoModeloC:
    memoria: MemoriaTrabajo
    principal: DiagnosticoInferido | None
    alternativos: tuple[DiagnosticoInferido, ...]
    explicacion_sin_conclusion: str | None
    trazas: tuple[TrazaInferencia, ...]
    rondas: int
    observaciones_confirmadas: dict[str, EstadoHecho]
    criterios: tuple[CriterioHipotesis, ...]
    explicacion_prioridad: str
    orden_b: tuple[str, ...]


class ModeloC:
    """Reutiliza B sin alterar sus reglas, hechos derivados ni activaciones."""

    def __init__(
        self, hechos_base: dict, diagnosticos_base: dict, reglas_base: dict,
        hechos_nuevos: dict, reglas_nuevas: dict, criterios_doc: dict,
    ):
        self.motor_b = ModeloB(
            hechos_base, diagnosticos_base, reglas_base, hechos_nuevos, reglas_nuevas
        )
        validar_criterios(criterios_doc, self.motor_b.sintomas, set(self.motor_b.diagnosticos))
        self.sintomas = self.motor_b.sintomas
        self.hechos = self.motor_b.hechos
        self.diagnosticos = self.motor_b.diagnosticos
        self.reglas = self.motor_b.reglas
        self.calidades = {entrada["id"]: entrada["nivel"] for entrada in criterios_doc["evidencia"]}
        self.prioridades = {entrada["id"]: entrada["nivel"] for entrada in criterios_doc["prioridades"]}

    @classmethod
    def desde_directorios(cls, base: Path, ampliacion: Path) -> "ModeloC":
        return cls(
            *leer_documentos(base), *leer_ampliacion(ampliacion),
            leer_criterios(ampliacion / "criterios_c.json"),
        )

    def evaluar(self, respuestas: Mapping[str, str]) -> ResultadoModeloC:
        resultado_b = self.motor_b.evaluar(respuestas)
        por_regla = {traza.regla_id: traza for traza in resultado_b.trazas}
        soportes: dict[tuple[str, EstadoHecho], list[TrazaInferencia]] = {}
        for traza in resultado_b.trazas:
            if traza.conclusion_tipo == "hecho":
                soportes.setdefault((traza.conclusion_id, traza.conclusion_estado), []).append(traza)

        def originales(traza: TrazaInferencia) -> set[str]:
            encontrados: set[str] = set()
            for condicion in traza.condiciones:
                if condicion.hecho_id in self.sintomas:
                    if resultado_b.observaciones_confirmadas.get(condicion.hecho_id) == condicion.estado:
                        encontrados.add(condicion.hecho_id)
                else:
                    for soporte in soportes.get((condicion.hecho_id, condicion.estado), ()):
                        encontrados.update(originales(soporte))
            return encontrados

        hipotesis = (resultado_b.principal, *resultado_b.alternativos)
        puntuadas = []
        for diagnostico in hipotesis:
            if diagnostico is None:
                continue
            observaciones: set[str] = set()
            for regla in diagnostico.reglas:
                observaciones.update(originales(por_regla[regla.id]))
            calidad = max((self.calidades[hecho] for hecho in observaciones), default=0)
            criterio = CriterioHipotesis(
                diagnostico.id, tuple(sorted(observaciones)), calidad,
                len(observaciones), self.prioridades[diagnostico.id],
            )
            puntuadas.append((criterio, diagnostico))
        puntuadas.sort(key=lambda par: par[0].clave)
        orden_b = tuple(d.id for d in hipotesis if d is not None)
        if not puntuadas:
            explicacion = "Sin hipótesis compatibles; no se aplica orden de prioridad."
        elif len(puntuadas) == 1:
            explicacion = "Única hipótesis compatible; no hubo conflicto que resolver."
        else:
            primero, segundo = puntuadas[0][0], puntuadas[1][0]
            motivo = motivo_precedencia(primero, segundo)
            explicacion = f"{primero.diagnostico_id} precede a {segundo.diagnostico_id} por {motivo}."
            if tuple(c.diagnostico_id for c, _ in puntuadas) == orden_b:
                explicacion += " B y C conservan el mismo orden en esta consulta; sus criterios coinciden aquí."
            else:
                explicacion += " El orden difiere del de B por la precedencia simbólica indicada."
        return ResultadoModeloC(
            resultado_b.memoria,
            puntuadas[0][1] if puntuadas else None,
            tuple(d for _, d in puntuadas[1:]),
            resultado_b.explicacion_sin_conclusion,
            resultado_b.trazas, resultado_b.rondas,
            resultado_b.observaciones_confirmadas,
            tuple(c for c, _ in puntuadas), explicacion, orden_b,
        )
