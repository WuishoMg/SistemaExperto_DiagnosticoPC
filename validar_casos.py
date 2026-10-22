"""Valida viñetas y reserva sin importar ni ejecutar motores de inferencia."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from diagnostico_pc.hechos import EstadoHecho  # noqa: E402
from diagnostico_pc.gestor_preguntas import GestorPreguntas  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import cargar_rutas  # noqa: E402

CARPETA = RAIZ / "data" / "evaluacion"
ARCHIVOS = ("casos_desarrollo.json", "casos_finales_reservados.json")
CLAVES_CASO = {
    "id", "ruta", "tipo_escenario", "relato", "trayecto_preguntas", "observaciones",
    "hipotesis_defendibles", "prioridad_revision", "evidencia_conocida",
    "informacion_faltante", "comprobaciones_adicionales", "justificacion_tecnica",
    "referencias", "estado_causa", "alcance",
}
TIPOS = {
    "evidencia_suficiente", "parcial", "ambigua", "simultanea", "tension_aparente",
    "comprobacion_adicional", "insuficiente", "fuera_cobertura",
}
ALCANCES = {"cuestionario_extremo_a_extremo", "fuera_catalogo", "limitacion_cuestionario"}


class ErrorCasos(ValueError):
    pass


def _exigir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ErrorCasos(mensaje)


def _texto(valor: object) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def _lista_textos(valor: object, *, vacia: bool = False) -> bool:
    return isinstance(valor, list) and (vacia or bool(valor)) and all(_texto(x) for x in valor)


def _validar_caso(caso: dict, preguntas, rutas, hechos: set[str], diagnosticos: set[str], refs: set[str]) -> None:
    ident = caso.get("id", "sin ID")
    _exigir(set(caso) == CLAVES_CASO, f"{ident}: campos faltantes o extra")
    _exigir(_texto(caso["relato"]) and _texto(caso["justificacion_tecnica"]), f"{ident}: relato o justificación vacíos")
    _exigir(caso["ruta"] in rutas.por_id, f"{ident}: ruta inexistente")
    _exigir(caso["tipo_escenario"] in TIPOS, f"{ident}: tipo inválido")
    _exigir(caso["alcance"] in ALCANCES, f"{ident}: alcance inválido")
    _exigir(caso["estado_causa"] == "no_confirmada", f"{ident}: causa indebidamente confirmada")
    _exigir(_lista_textos(caso["informacion_faltante"]) and _lista_textos(caso["comprobaciones_adicionales"]), f"{ident}: faltan límites o comprobaciones")
    _exigir(_lista_textos(caso["referencias"]) and set(caso["referencias"]) <= refs, f"{ident}: referencias inválidas")
    _exigir(isinstance(caso["observaciones"], dict) and bool(caso["observaciones"]), f"{ident}: observaciones vacías")
    _exigir(set(caso["observaciones"]) <= hechos, f"{ident}: hecho fuera de catálogo")
    _exigir(all(x in {e.value for e in EstadoHecho} for x in caso["observaciones"].values()), f"{ident}: estado inválido")
    etiquetas = caso["hipotesis_defendibles"]
    _exigir(_lista_textos(etiquetas, vacia=True) and len(etiquetas) == len(set(etiquetas)) and set(etiquetas) <= diagnosticos, f"{ident}: diagnósticos inválidos")
    if caso["alcance"] != "cuestionario_extremo_a_extremo":
        _exigir(not etiquetas, f"{ident}: límite de cobertura con etiqueta de catálogo")
    if caso["tipo_escenario"] == "fuera_cobertura":
        _exigir(not etiquetas, f"{ident}: fuera de cobertura con diagnóstico")
    prioridad = caso["prioridad_revision"]
    if prioridad is not None:
        _exigir(len(etiquetas) > 1, f"{ident}: prioridad sin varias hipótesis")
        _exigir(isinstance(prioridad, dict) and set(prioridad) == {"diagnostico", "justificacion"}, f"{ident}: prioridad mal formada")
        _exigir(prioridad["diagnostico"] in etiquetas and _texto(prioridad["justificacion"]), f"{ident}: prioridad sin sustento")
    _exigir(isinstance(caso["trayecto_preguntas"], list) and bool(caso["trayecto_preguntas"]), f"{ident}: trayecto vacío")
    preguntas_por_id = {x.id: x for x in preguntas}
    gestor = GestorPreguntas(preguntas, rutas, caso["ruta"])
    obtenidas = {}
    for pregunta_id in caso["trayecto_preguntas"]:
        siguiente = gestor.siguiente()
        _exigir(siguiente is not None and siguiente.id == pregunta_id, f"{ident}: pregunta inalcanzable {pregunta_id}")
        hecho = preguntas_por_id[pregunta_id].hecho
        _exigir(hecho in caso["observaciones"], f"{ident}: falta observación de {pregunta_id}")
        estado = caso["observaciones"][hecho]
        respuesta = next((r for r in RespuestaVisible if preguntas_por_id[pregunta_id].estado_para(r).value == estado), None)
        _exigir(respuesta is not None, f"{ident}: polaridad imposible en {pregunta_id}")
        gestor.responder(pregunta_id, respuesta)
        obtenidas[hecho] = estado
    _exigir(gestor.estado_final is not None, f"{ident}: trayecto incompleto o contradictorio")
    _exigir(caso["observaciones"] == obtenidas, f"{ident}: observaciones que la ruta no puede obtener")
    conocidos = caso["evidencia_conocida"]
    _exigir(isinstance(conocidos, list), f"{ident}: evidencia conocida inválida")
    _exigir([(x.get("hecho"), x.get("estado")) for x in conocidos if isinstance(x, dict)] == [(h, s) for h, s in obtenidas.items() if s != "desconocido"], f"{ident}: evidencia conocida no coincide")
    _exigir(all(isinstance(x, dict) and set(x) == {"hecho", "estado", "detalle"} and _texto(x["detalle"]) for x in conocidos), f"{ident}: evidencia conocida mal formada")
    desconocidos = {h for h, s in obtenidas.items() if s == "desconocido"}
    _exigir(desconocidos <= set(caso["informacion_faltante"]), f"{ident}: se omitió una respuesta desconocida")


def validar_documentos(desarrollo: dict, final: dict, fuentes: dict, preguntas, rutas, hechos: set[str], diagnosticos: set[str]) -> dict:
    _exigir(isinstance(fuentes, dict) and fuentes.get("version") == 1 and isinstance(fuentes.get("fuentes"), list), "Catálogo de fuentes inválido")
    _exigir(all(isinstance(x, dict) and set(x) == {"id", "entidad", "titulo", "url", "uso"} and all(_texto(v) for v in x.values()) and x["url"].startswith("https://") for x in fuentes["fuentes"]), "Fuente inválida")
    refs = [x["id"] for x in fuentes["fuentes"]]
    _exigir(len(refs) == len(set(refs)), "IDs de fuentes duplicados")
    todos = []
    for documento, grupo, cantidad, prefijo in ((desarrollo, "desarrollo", 60, "D"), (final, "final_reservado", 20, "F")):
        _exigir(isinstance(documento, dict) and set(documento) == {"version", "naturaleza", "grupo", "casos"} and documento["version"] == 1 and documento["grupo"] == grupo and _texto(documento["naturaleza"]), f"{grupo}: encabezado inválido")
        _exigir(isinstance(documento["casos"], list) and len(documento["casos"]) == cantidad, f"{grupo}: cantidad inválida")
        for indice, caso in enumerate(documento["casos"], 1):
            _exigir(isinstance(caso, dict) and caso.get("id") == f"{prefijo}{indice:03d}", f"{grupo}: ID inválido")
            _validar_caso(caso, preguntas, rutas, hechos, diagnosticos, set(refs))
            todos.append(caso)
    _exigir({c["ruta"] for c in todos} == set(rutas.por_id), "Falta cobertura de una ruta")
    # La igualdad de firma entre grupos revela reutilización aun con una narración distinta.
    firmas_desarrollo = {(c["ruta"], tuple(sorted(c["observaciones"].items()))) for c in desarrollo["casos"]}
    for caso in final["casos"]:
        _exigir((caso["ruta"], tuple(sorted(caso["observaciones"].items()))) not in firmas_desarrollo, f"{caso['id']}: observaciones duplicadas entre grupos")
    return {"categoria": Counter(c["ruta"] for c in todos), "tipo": Counter(c["tipo_escenario"] for c in todos), "alcance": Counter(c["alcance"] for c in todos)}


def main() -> int:
    try:
        desarrollo = json.loads((CARPETA / ARCHIVOS[0]).read_text(encoding="utf-8"))
        reservado_bytes = (CARPETA / ARCHIVOS[1]).read_bytes()
        final = json.loads(reservado_bytes.decode("utf-8"))
        fuentes = json.loads((CARPETA / "fuentes.json").read_text(encoding="utf-8"))
        esperado = (CARPETA / "RESERVA_FINAL.sha256").read_text(encoding="ascii").split()[0]
        _exigir(hashlib.sha256(reservado_bytes).hexdigest() == esperado, "Huella SHA-256 de reserva final no coincide")
        hechos_doc = json.loads((RAIZ / "data/conocimiento/hechos.json").read_text(encoding="utf-8"))
        diagnosticos_doc = json.loads((RAIZ / "data/conocimiento/diagnosticos.json").read_text(encoding="utf-8"))
        hechos = {x["id"] for x in hechos_doc["hechos"] if x["tipo"] == "sintoma"}
        diagnosticos = {x["id"] for x in diagnosticos_doc["diagnosticos"]}
        preguntas = cargar_preguntas(RAIZ / "data/interfaz/preguntas.json", hechos)
        rutas = cargar_rutas(RAIZ / "data/interfaz/rutas.json", preguntas)
        resumen = validar_documentos(desarrollo, final, fuentes, preguntas, rutas, hechos, diagnosticos)
    except (OSError, UnicodeError, json.JSONDecodeError, ErrorCasos, ValueError) as error:
        print(f"Casos inválidos: {error}", file=sys.stderr)
        return 1
    print("Casos estructuralmente válidos: 60 desarrollo y 20 final reservado.")
    for nombre, conteo in resumen.items():
        print(f"{nombre}: " + ", ".join(f"{clave}={conteo[clave]}" for clave in sorted(conteo)))
    print("Huella SHA-256 de la reserva final verificada; no se ejecutó ningún modelo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
