"""Convierte resultados inferidos en datos simples aptos para QML y PDF."""

from diagnostico_pc.conocimiento_c import CALIDADES, PRIORIDADES
from diagnostico_pc.modelo_b import ResultadoModeloB
from diagnostico_pc.modelo_c import ResultadoModeloC


def _condicion(condicion) -> dict:
    return {
        "hechoId": condicion.hecho_id,
        "nombre": condicion.nombre,
        "estado": condicion.estado.value,
    }


def _diagnostico(diagnostico) -> dict:
    return {
        "id": diagnostico.id,
        "nombre": diagnostico.nombre,
        "categoria": diagnostico.categoria,
        "descripcion": diagnostico.descripcion,
        "recomendaciones": list(diagnostico.recomendaciones),
        "reglas": [
            {
                "id": regla.id,
                "explicacion": regla.explicacion,
                "condiciones": [_condicion(c) for c in regla.condiciones],
            }
            for regla in diagnostico.reglas
        ],
    }


def serializar_resultado(resultado, modelo: str = "C") -> dict:
    hipotesis = [d for d in (resultado.principal, *resultado.alternativos) if d]
    trazas = list(resultado.trazas) if isinstance(resultado, ResultadoModeloB | ResultadoModeloC) else []
    derivados = [
        {
            "hechoId": hecho_id,
            "estado": resultado.memoria.hechos[hecho_id].value,
            "reglas": [t.regla_id for t in trazas if t.conclusion_tipo == "hecho" and t.conclusion_id == hecho_id],
        }
        for hecho_id in sorted({t.conclusion_id for t in trazas if t.conclusion_tipo == "hecho"})
    ]
    criterios = []
    if isinstance(resultado, ResultadoModeloC):
        criterios = [
            {
                "diagnosticoId": c.diagnostico_id,
                "observaciones": list(c.observaciones),
                "calidad": c.calidad,
                "calidadTexto": CALIDADES[c.calidad] if c.calidad else "sin observaciones confirmadas",
                "especificidad": c.especificidad,
                "prioridad": c.prioridad,
                "prioridadTexto": PRIORIDADES[c.prioridad],
            }
            for c in resultado.criterios
        ]
    return {
        "modelo": modelo,
        "principal": _diagnostico(hipotesis[0]) if hipotesis else None,
        "alternativas": [_diagnostico(d) for d in hipotesis[1:]],
        "explicacionSinConclusion": resultado.explicacion_sin_conclusion or "",
        "explicacionPrioridad": getattr(resultado, "explicacion_prioridad", ""),
        "criterios": criterios,
        "observacionesConfirmadas": {
            k: v.value for k, v in getattr(resultado, "observaciones_confirmadas", {}).items()
        },
        "hechosDerivados": derivados,
        "trazas": [
            {
                "reglaId": t.regla_id,
                "nivel": t.nivel,
                "explicacion": t.explicacion,
                "condiciones": [_condicion(c) for c in t.condiciones],
                "conclusionTipo": t.conclusion_tipo,
                "conclusionId": t.conclusion_id,
                "conclusionEstado": t.conclusion_estado.value if t.conclusion_estado else "",
            }
            for t in trazas
        ],
        "aviso": "Estas son hipótesis para revisión técnica; confirme la causa con pruebas técnicas.",
    }
