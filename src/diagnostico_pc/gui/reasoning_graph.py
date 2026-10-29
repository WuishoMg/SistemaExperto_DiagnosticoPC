"""Proyección y disposición visual de una consulta ya inferida; no ejecuta reglas."""

from collections import defaultdict
from textwrap import shorten


ANCHO_NODO = 224
ALTO_NODO = 162
ALTOS_ESPECIALES = {"regla": 184, "derivado": 214, "hipotesis": 230}
ANCHO_SECCION = 756
MARGEN = 20
ESPACIO_TARJETAS = 14
ESPACIO_SECCIONES = 34


def _resumen(texto: str, limite: int = 70) -> str:
    """Texto breve para la tarjeta; el detalle conserva el original completo."""
    return shorten(texto.strip(), width=limite, placeholder="…") if texto else ""


def _disponer(nodos: dict, conexiones: list[dict]) -> tuple[list[dict], int, int]:
    """Fija toda la geometría antes de entregarla a Qt Quick."""
    niveles_reglas = {n["id"]: max(1, int(n.get("nivel") or 1))
                      for n in nodos.values() if n["tipo"] == "regla"}
    niveles_derivados = defaultdict(list)
    for conexion in conexiones:
        if conexion["tipo"] == "conclusion" and conexion["destino"].startswith("h:"):
            niveles_derivados[conexion["destino"]].append(niveles_reglas.get(conexion["origen"], 1))
    etapas = [("observacion", 0, "Observaciones del usuario")]
    max_nivel = max(niveles_reglas.values(), default=0)
    for nivel in range(1, max_nivel + 1):
        etapas.append(("regla", nivel, "Reglas activadas" if nivel == 1 else f"Reglas activadas · etapa {nivel}"))
        if any(min(niveles_derivados.get(n["id"], [1])) == nivel
               for n in nodos.values() if n["tipo"] == "derivado"):
            etapas.append(("derivado", nivel, "Hechos derivados" if nivel == 1 else f"Hechos derivados · etapa {nivel}"))
    if any(n["tipo"] == "derivado" for n in nodos.values()) and max_nivel == 0:
        etapas.append(("derivado", 1, "Hechos derivados"))
    if any(n["tipo"] == "hipotesis" for n in nodos.values()):
        etapas.extend((("principal", 0, "Hipótesis principal"),
                       ("alternativas", 0, "Hipótesis alternativas")))

    secciones = []
    y = MARGEN
    for tipo, nivel, titulo in etapas:
        if tipo == "observacion":
            miembros = [n for n in nodos.values() if n["tipo"] == "observacion"]
        elif tipo == "regla":
            miembros = [n for n in nodos.values() if n["tipo"] == "regla" and niveles_reglas[n["id"]] == nivel]
        elif tipo == "derivado":
            miembros = [n for n in nodos.values() if n["tipo"] == "derivado"
                        and min(niveles_derivados.get(n["id"], [1])) == nivel]
        elif tipo == "principal":
            miembros = [n for n in nodos.values() if n["tipo"] == "hipotesis" and n["orden"] == 1]
        else:
            miembros = [n for n in nodos.values() if n["tipo"] == "hipotesis" and n["orden"] > 1]
        if not miembros:
            continue
        miembros.sort(key=lambda n: (n.get("orden", 0), n["id"]))
        filas = (len(miembros) + 2) // 3
        altos_fila = [max(ALTOS_ESPECIALES.get(n["tipo"], ALTO_NODO)
                          for n in miembros[fila * 3:(fila + 1) * 3]) for fila in range(filas)]
        alto = 54 + sum(altos_fila) + (filas - 1) * ESPACIO_TARJETAS + 20
        secciones.append({"tipo": tipo, "titulo": titulo, "x": MARGEN, "y": y,
                          "ancho": ANCHO_SECCION, "alto": alto, "cantidad": len(miembros)})
        for indice, nodo in enumerate(miembros):
            columna = indice % 3
            fila = indice // 3
            nodo.update({"x": MARGEN + 28 + columna * (ANCHO_NODO + ESPACIO_TARJETAS),
                         "y": y + 54 + sum(altos_fila[:fila]) + fila * ESPACIO_TARJETAS,
                         "ancho": ANCHO_NODO,
                         "alto": ALTOS_ESPECIALES.get(nodo["tipo"], ALTO_NODO)})
            if len(miembros) == 1:
                nodo["x"] = MARGEN + (ANCHO_SECCION - ANCHO_NODO) // 2
            elif len(miembros) == 2:
                nodo["x"] = MARGEN + 136 + indice * (ANCHO_NODO + ESPACIO_TARJETAS)
        y += alto + ESPACIO_SECCIONES
    return secciones, ANCHO_SECCION + 2 * MARGEN, max(y - ESPACIO_SECCIONES + MARGEN, 220)


def construir_grafo(resultado: dict, historial, preguntas: dict, hechos: dict,
                    reglas: list[dict], categoria: str = "") -> dict:
    """Construye un DAG solo con relaciones presentes en trazas de C.

    ``historial`` contiene las preguntas realmente contestadas. El catálogo de
    reglas se consulta únicamente para enumerar las no activadas.
    """
    nodos: dict[str, dict] = {}
    conexiones: list[dict] = []
    avisos: list[str] = []
    sin_preguntar = []
    respondidas = {}
    for registro in historial:
        pregunta = preguntas[registro.pregunta_id]
        respondidas[pregunta.hecho] = (pregunta, pregunta.estado_para(registro.respuesta).value)

    for hecho_id, definicion in sorted(hechos.items()):
        if definicion["tipo"] != "sintoma":
            continue
        if hecho_id not in respondidas:
            sin_preguntar.append({"id": hecho_id, "nombre": definicion["nombre"]})
            continue
        pregunta, estado = respondidas[hecho_id]
        nodos[f"o:{hecho_id}"] = {
            "id": f"o:{hecho_id}", "tipo": "observacion", "referencia": hecho_id,
            "etiqueta": definicion["nombre"], "estado": estado,
            "detalle": pregunta.texto, "pregunta": pregunta.texto,
            "descripcion": definicion.get("descripcion", ""), "nivel": 0,
        }

    hipotesis = [h for h in [resultado.get("principal"), *(resultado.get("alternativas") or [])] if h]
    criterios = {c["diagnosticoId"]: c for c in resultado.get("criterios", [])}
    for indice, hipotesis_item in enumerate(hipotesis):
        identificador = hipotesis_item["id"]
        nodos[f"d:{identificador}"] = {
            "id": f"d:{identificador}", "tipo": "hipotesis", "referencia": identificador,
            "etiqueta": hipotesis_item["nombre"], "estado": "",
            "detalle": hipotesis_item.get("descripcion", ""),
            "resumen": _resumen(hipotesis_item.get("descripcion", "")), "nivel": 0,
            "orden": indice + 1, "criterio": criterios.get(identificador, {}),
        }

    trazas = resultado.get("trazas") or []
    activadas = set()
    for traza in trazas:
        regla_id = traza.get("reglaId")
        if not regla_id:
            avisos.append("Una traza carece de ID de regla; se omitió.")
            continue
        activadas.add(regla_id)
        nodo_regla = f"r:{regla_id}"
        nodos[nodo_regla] = {
            "id": nodo_regla, "tipo": "regla", "referencia": regla_id,
            "etiqueta": regla_id, "estado": "activada",
            "detalle": traza.get("explicacion", ""), "nivel": traza.get("nivel", 0),
            "resumen": _resumen(traza.get("explicacion", "")),
            "condiciones": traza.get("condiciones") or [],
            "conclusion": {"tipo": traza.get("conclusionTipo", ""),
                           "id": traza.get("conclusionId", ""),
                           "estado": traza.get("conclusionEstado", "")},
        }
        for condicion in traza.get("condiciones") or []:
            hecho_id = condicion.get("hechoId")
            estado = condicion.get("estado")
            origen = f"o:{hecho_id}" if hecho_id in hechos and hechos[hecho_id]["tipo"] == "sintoma" else f"h:{hecho_id}"
            if origen.startswith("h:") and hecho_id in hechos and hechos[hecho_id]["tipo"] == "derivado":
                nodos.setdefault(origen, {
                    "id": origen, "tipo": "derivado", "referencia": hecho_id,
                    "etiqueta": hechos[hecho_id]["nombre"], "estado": estado,
                    "detalle": hechos[hecho_id].get("descripcion", ""),
                    "resumen": _resumen(hechos[hecho_id].get("descripcion", "")), "nivel": 0,
                })
            if origen not in nodos or nodos[origen]["estado"] != estado:
                avisos.append(f"No se pudo verificar la condición {hecho_id} de {regla_id}; se omitió su conexión.")
                continue
            conexiones.append({"id": f"{origen}>{nodo_regla}", "origen": origen,
                               "destino": nodo_regla, "tipo": "condicion", "estado": estado})

        conclusion_tipo = traza.get("conclusionTipo")
        conclusion_id = traza.get("conclusionId")
        if conclusion_tipo == "hecho" and conclusion_id in hechos and hechos[conclusion_id]["tipo"] == "derivado":
            destino = f"h:{conclusion_id}"
            estado = traza.get("conclusionEstado")
            if destino in nodos and nodos[destino]["estado"] != estado:
                avisos.append(f"Estados incompatibles para {conclusion_id}; se omitió una conexión.")
                continue
            nodos.setdefault(destino, {
                "id": destino, "tipo": "derivado", "referencia": conclusion_id,
                "etiqueta": hechos[conclusion_id]["nombre"], "estado": estado,
                "detalle": hechos[conclusion_id].get("descripcion", ""),
                "resumen": _resumen(hechos[conclusion_id].get("descripcion", "")), "nivel": 0,
            })
        elif conclusion_tipo == "diagnostico":
            destino = f"d:{conclusion_id}"
            if destino not in nodos:
                avisos.append(f"La conclusión {conclusion_id} no figura entre las hipótesis; se omitió su conexión.")
                continue
            estado = ""
        else:
            avisos.append(f"La conclusión de {regla_id} no es verificable; se omitió su conexión.")
            continue
        conexiones.append({"id": f"{nodo_regla}>{destino}", "origen": nodo_regla,
                           "destino": destino, "tipo": "conclusion", "estado": estado})

    # Las trazas son el único origen de aristas. El catálogo nunca activa reglas.
    no_activadas = [r["id"] for r in reglas if r["id"] not in activadas]
    conclusiones_derivadas = {a["destino"] for a in conexiones if a["tipo"] == "conclusion"}
    for identificador, nodo in nodos.items():
        if nodo["tipo"] == "derivado" and identificador not in conclusiones_derivadas:
            avisos.append(f"No consta la regla que produjo {nodo['referencia']} en las trazas disponibles.")

    generadoras = defaultdict(list)
    for conexion in conexiones:
        if conexion["tipo"] == "conclusion":
            generadoras[conexion["destino"]].append(conexion["origen"].removeprefix("r:"))
    for nodo in nodos.values():
        if nodo["tipo"] == "derivado":
            nodo["generadoras"] = sorted(set(generadoras[nodo["id"]]))
        elif nodo["tipo"] == "regla":
            conclusion = nodo["conclusion"]
            destino = ("h:" if conclusion["tipo"] == "hecho" else "d:") + conclusion["id"]
            conclusion["nombre"] = nodos.get(destino, {}).get("etiqueta", conclusion["id"])

    predecesoras = defaultdict(list)
    for conexion in conexiones:
        predecesoras[conexion["destino"]].append(conexion["origen"])
    soportes = {}
    for hipotesis_item in hipotesis:
        inicio = f"d:{hipotesis_item['id']}"
        vistos = {inicio}
        pendientes = [inicio]
        while pendientes:
            for origen in predecesoras[pendientes.pop()]:
                if origen not in vistos:
                    vistos.add(origen)
                    pendientes.append(origen)
        soportes[inicio] = sorted(vistos)
        nodos[inicio]["soportesDetalle"] = {
            tipo: [nodos[k]["etiqueta"] for k in sorted(vistos)
                   if nodos[k]["tipo"] == tipo]
            for tipo in ("observacion", "regla", "derivado")
        }

    secciones, ancho, alto = _disponer(nodos, conexiones)

    return {
        "nodos": list(nodos.values()), "conexiones": conexiones,
        "secciones": secciones, "ancho": ancho, "alto": alto, "categoria": categoria,
        "hipotesis": [f"d:{h['id']}" for h in hipotesis],
        "soportes": soportes, "reglasNoActivadas": no_activadas,
        "sinPreguntar": sin_preguntar, "avisos": list(dict.fromkeys(avisos)),
        "explicacionSinConclusion": resultado.get("explicacionSinConclusion", ""),
        "explicacionPrioridad": resultado.get("explicacionPrioridad", ""),
    }
