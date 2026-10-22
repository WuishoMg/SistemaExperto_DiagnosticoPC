"""Encadenamiento hacia adelante multinivel con trazas de cada regla."""

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .conocimiento_b import leer_ampliacion, validar_ampliacion
from .hechos import EstadoHecho, condicion_satisfecha, normalizar_observaciones
from .modelo_a import CondicionVerificada, DiagnosticoInferido, MemoriaTrabajo, ReglaActivada
from .validacion import leer_documentos


class ConflictoInferencia(ValueError):
    """Dos cadenas intentan asignar estados opuestos a un hecho derivado."""


@dataclass(frozen=True)
class TrazaInferencia:
    regla_id: str
    nivel: int
    explicacion: str
    condiciones: tuple[CondicionVerificada, ...]
    conclusion_tipo: str
    conclusion_id: str
    conclusion_estado: EstadoHecho | None


@dataclass(frozen=True)
class ResultadoModeloB:
    memoria: MemoriaTrabajo
    principal: DiagnosticoInferido | None
    alternativos: tuple[DiagnosticoInferido, ...]
    explicacion_sin_conclusion: str | None
    trazas: tuple[TrazaInferencia, ...]
    rondas: int
    observaciones_confirmadas: dict[str, EstadoHecho]


class ModeloB:
    """Aplica cada regla una vez cuando sus condiciones son explícitamente verdaderas o falsas."""

    def __init__(
        self, hechos_base: dict, diagnosticos_base: dict, reglas_base: dict,
        hechos_nuevos: dict, reglas_nuevas: dict,
    ):
        hechos_doc, diagnosticos_doc, reglas_doc = validar_ampliacion(
            hechos_base, diagnosticos_base, reglas_base, hechos_nuevos, reglas_nuevas
        )
        self.hechos = {hecho["id"]: hecho for hecho in hechos_doc["hechos"]}
        self.diagnosticos = {d["id"]: d for d in diagnosticos_doc["diagnosticos"]}
        self.reglas = sorted(reglas_doc["reglas"], key=lambda regla: regla["id"])
        self.sintomas = {
            identificador for identificador, hecho in self.hechos.items()
            if hecho["tipo"] == "sintoma"
        }

    @classmethod
    def desde_directorios(cls, base: Path, ampliacion: Path) -> "ModeloB":
        return cls(*leer_documentos(base), *leer_ampliacion(ampliacion))

    def evaluar(self, respuestas: Mapping[str, str]) -> ResultadoModeloB:
        observaciones = normalizar_observaciones(self.sintomas, respuestas)
        memoria = MemoriaTrabajo(
            hechos={identificador: EstadoHecho.DESCONOCIDO for identificador in self.hechos}
        )
        memoria.hechos.update(observaciones)
        niveles = {identificador: 0 for identificador in self.sintomas}
        activadas: set[str] = set()
        trazas: list[TrazaInferencia] = []
        rondas = 0

        while True:
            # La ronda lee una instantánea: una conclusión nueva habilita reglas
            # dependientes solo en la siguiente ronda.
            aplicables = [
                regla for regla in self.reglas
                if regla["id"] not in activadas and all(
                    condicion_satisfecha(
                        memoria.hechos[condicion["hecho"]], EstadoHecho(condicion["estado"])
                    ) for condicion in regla["condiciones"]
                )
            ]
            if not aplicables:
                break

            propuestas: dict[str, tuple[EstadoHecho, str]] = {}
            for regla in aplicables:
                conclusion = regla["conclusion"]
                if conclusion["tipo"] != "hecho":
                    continue
                identificador = conclusion["id"]
                estado = EstadoHecho(conclusion["estado"])
                anterior = propuestas.get(identificador)
                if anterior is not None and anterior[0] != estado:
                    raise ConflictoInferencia(
                        f"Conclusiones contradictorias para {identificador}: "
                        f"{anterior[1]} y {regla['id']}"
                    )
                if memoria.hechos[identificador] not in (EstadoHecho.DESCONOCIDO, estado):
                    raise ConflictoInferencia(
                        f"Conclusión contradictoria para {identificador}: {regla['id']}"
                    )
                propuestas[identificador] = (estado, regla["id"])

            rondas += 1
            for regla in aplicables:
                condiciones = tuple(
                    CondicionVerificada(
                        hecho_id=condicion["hecho"],
                        nombre=self.hechos[condicion["hecho"]]["nombre"],
                        estado=memoria.hechos[condicion["hecho"]],
                    ) for condicion in regla["condiciones"]
                )
                nivel = 1 + max(niveles[condicion.hecho_id] for condicion in condiciones)
                conclusion = regla["conclusion"]
                estado_conclusion = (
                    EstadoHecho(conclusion["estado"])
                    if conclusion["tipo"] == "hecho" else None
                )
                trazas.append(TrazaInferencia(
                    regla_id=regla["id"], nivel=nivel,
                    explicacion=regla["explicacion"], condiciones=condiciones,
                    conclusion_tipo=conclusion["tipo"], conclusion_id=conclusion["id"],
                    conclusion_estado=estado_conclusion,
                ))
                activadas.add(regla["id"])
                if conclusion["tipo"] == "diagnostico":
                    memoria.registrar(
                        conclusion["id"], ReglaActivada(regla["id"], regla["explicacion"], condiciones)
                    )
                else:
                    memoria.reglas_activadas.append(regla["id"])
                    identificador = conclusion["id"]
                    memoria.hechos[identificador] = estado_conclusion
                    niveles[identificador] = min(niveles.get(identificador, nivel), nivel)

        inferidos = []
        for diagnostico_id, evidencias in memoria.conclusiones.items():
            definicion = self.diagnosticos[diagnostico_id]
            inferidos.append(DiagnosticoInferido(
                id=diagnostico_id,
                nombre=definicion["nombre"],
                categoria=definicion["categoria"],
                descripcion=definicion["descripcion"],
                recomendaciones=tuple(definicion["recomendaciones"]),
                reglas=tuple(sorted(evidencias, key=lambda r: (-r.especificidad, r.id))),
            ))
        inferidos.sort(key=lambda diagnostico: (-diagnostico.especificidad, diagnostico.id))
        motivo = None
        if not inferidos:
            motivo = (
                "No se aportaron observaciones confirmadas; no hay base para activar reglas."
                if all(estado == EstadoHecho.DESCONOCIDO for estado in observaciones.values())
                else "Ninguna cadena de reglas concluye un diagnóstico con los hechos disponibles. "
                     "Se requiere más información o revisión técnica."
            )
        return ResultadoModeloB(
            memoria=memoria,
            principal=inferidos[0] if inferidos else None,
            alternativos=tuple(inferidos[1:]),
            explicacion_sin_conclusion=motivo,
            trazas=tuple(trazas),
            rondas=rondas,
            observaciones_confirmadas={
                identificador: estado for identificador, estado in observaciones.items()
                if estado != EstadoHecho.DESCONOCIDO
            },
        )
