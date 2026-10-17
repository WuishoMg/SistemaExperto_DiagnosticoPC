"""Motor de reglas directas y Modelo A del primer avance académico."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from .hechos import EstadoHecho, condicion_satisfecha, normalizar_observaciones
from .validacion import leer_documentos, validar_documentos


@dataclass(frozen=True)
class CondicionVerificada:
    hecho_id: str
    nombre: str
    estado: EstadoHecho


@dataclass(frozen=True)
class ReglaActivada:
    id: str
    explicacion: str
    condiciones: tuple[CondicionVerificada, ...]

    @property
    def especificidad(self) -> int:
        return len(self.condiciones)


@dataclass(frozen=True)
class DiagnosticoInferido:
    id: str
    nombre: str
    categoria: str
    descripcion: str
    recomendaciones: tuple[str, ...]
    reglas: tuple[ReglaActivada, ...]

    @property
    def especificidad(self) -> int:
        return max(regla.especificidad for regla in self.reglas)


@dataclass
class MemoriaTrabajo:
    """Hechos de la consulta y conclusiones obtenidas durante el recorrido."""

    hechos: dict[str, EstadoHecho]
    reglas_activadas: list[str] = field(default_factory=list)
    conclusiones: dict[str, list[ReglaActivada]] = field(default_factory=dict)

    def registrar(self, diagnostico_id: str, regla: ReglaActivada) -> None:
        self.reglas_activadas.append(regla.id)
        self.conclusiones.setdefault(diagnostico_id, []).append(regla)


@dataclass(frozen=True)
class ResultadoModeloA:
    memoria: MemoriaTrabajo
    principal: DiagnosticoInferido | None
    alternativos: tuple[DiagnosticoInferido, ...]
    explicacion_sin_conclusion: str | None


class ModeloA:
    """Encadena hechos observados hacia diagnósticos directos en un recorrido."""

    def __init__(self, hechos_doc: dict, diagnosticos_doc: dict, reglas_doc: dict):
        validar_documentos(hechos_doc, diagnosticos_doc, reglas_doc)
        self.hechos = {hecho["id"]: hecho for hecho in hechos_doc["hechos"]}
        self.diagnosticos = {
            diagnostico["id"]: diagnostico for diagnostico in diagnosticos_doc["diagnosticos"]
        }
        self.reglas = sorted(reglas_doc["reglas"], key=lambda regla: regla["id"])
        self.sintomas = {
            identificador for identificador, hecho in self.hechos.items()
            if hecho["tipo"] == "sintoma"
        }

    @classmethod
    def desde_directorio(cls, directorio: Path) -> "ModeloA":
        return cls(*leer_documentos(directorio))

    def evaluar(self, respuestas: Mapping[str, str]) -> ResultadoModeloA:
        observaciones = normalizar_observaciones(self.sintomas, respuestas)
        memoria = MemoriaTrabajo(
            hechos={identificador: EstadoHecho.DESCONOCIDO for identificador in self.hechos}
        )
        memoria.hechos.update(observaciones)

        # En el Modelo A las reglas concluyen diagnósticos directos. Las reglas
        # para hechos derivados se reservan para modelos posteriores.
        for regla in self.reglas:
            if regla["conclusion"]["tipo"] != "diagnostico":
                continue
            if not all(
                condicion_satisfecha(
                    memoria.hechos[condicion["hecho"]], EstadoHecho(condicion["estado"])
                )
                for condicion in regla["condiciones"]
            ):
                continue
            verificadas = tuple(
                CondicionVerificada(
                    hecho_id=condicion["hecho"],
                    nombre=self.hechos[condicion["hecho"]]["nombre"],
                    estado=memoria.hechos[condicion["hecho"]],
                )
                for condicion in regla["condiciones"]
            )
            memoria.registrar(
                regla["conclusion"]["id"],
                ReglaActivada(regla["id"], regla["explicacion"], verificadas),
            )

        inferidos = []
        for diagnostico_id, evidencias in memoria.conclusiones.items():
            definicion = self.diagnosticos[diagnostico_id]
            inferidos.append(
                DiagnosticoInferido(
                    id=diagnostico_id,
                    nombre=definicion["nombre"],
                    categoria=definicion["categoria"],
                    descripcion=definicion["descripcion"],
                    recomendaciones=tuple(definicion["recomendaciones"]),
                    reglas=tuple(sorted(evidencias, key=lambda r: (-r.especificidad, r.id))),
                )
            )

        # La especificidad es un orden de presentación, no una probabilidad.
        inferidos.sort(key=lambda diagnostico: (-diagnostico.especificidad, diagnostico.id))
        if inferidos:
            return ResultadoModeloA(memoria, inferidos[0], tuple(inferidos[1:]), None)
        if all(estado == EstadoHecho.DESCONOCIDO for estado in observaciones.values()):
            motivo = "No se aportaron observaciones confirmadas; no hay base para activar reglas."
        else:
            motivo = (
                "Ninguna regla directa coincide con los hechos disponibles. "
                "Se requiere más información o revisión técnica."
            )
        return ResultadoModeloA(memoria, None, (), motivo)
