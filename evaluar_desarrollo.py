"""Evaluación reproducible del desarrollo, sin acceder a la reserva final.

La captura persiste salidas de los motores antes de que el análisis lea referencias.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from diagnostico_pc.gestor_preguntas import GestorPreguntas  # noqa: E402
from diagnostico_pc.preguntas import RespuestaVisible, cargar_preguntas  # noqa: E402
from diagnostico_pc.rutas import cargar_rutas  # noqa: E402
from diagnostico_pc.selector import seleccionar_modelo  # noqa: E402
from validar_casos import ErrorCasos, _validar_caso  # noqa: E402

SALIDA = ROOT / "data" / "evaluacion" / "resultados_etapa5"
MODELOS = ("A", "B", "C")
ARCHIVOS_BASE = (
    "data/conocimiento/hechos.json", "data/conocimiento/diagnosticos.json",
    "data/conocimiento/reglas.json", "data/conocimiento_avance2/hechos.json",
    "data/conocimiento_avance2/reglas.json", "data/conocimiento_avance2/criterios_c.json",
    "data/interfaz/preguntas.json", "data/interfaz/rutas.json",
    "data/evaluacion/casos_desarrollo.json", "data/evaluacion/fuentes.json",
    "data/evaluacion/historico/casos_desarrollo_etapa4_v1.json",
    "validar_casos.py", "docs/PROTOCOLO_EVALUACION_AVANCE_2.md",
    "docs/REVISION_CASOS_ETAPA_4_1.md",
)
MOTORES = (
    "src/diagnostico_pc/modelo_a.py", "src/diagnostico_pc/modelo_b.py",
    "src/diagnostico_pc/modelo_c.py", "src/diagnostico_pc/hechos.py",
    "src/diagnostico_pc/selector.py", "src/diagnostico_pc/gestor_preguntas.py",
    "src/diagnostico_pc/preguntas.py", "src/diagnostico_pc/rutas.py",
    "src/diagnostico_pc/validacion.py", "src/diagnostico_pc/conocimiento_b.py",
    "src/diagnostico_pc/conocimiento_c.py", "evaluar_desarrollo.py",
)
ALCANCES_ELEGIBLES = {"cuestionario_extremo_a_extremo", "fuera_catalogo"}


def cargar(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def guardar(ruta: Path, valor: object) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(valor, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def huella(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def comprobar_base() -> tuple[dict, list[str], dict]:
    manifiesto = cargar(ROOT / "data/evaluacion/MANIFIESTO.json")
    huellas = {}
    for nombre in ARCHIVOS_BASE:
        actual = huella(ROOT / nombre)
        if actual != manifiesto["archivos"][nombre]:
            raise ValueError(f"Huella distinta del manifiesto: {nombre}")
        huellas[nombre] = actual
    for nombre in MOTORES:
        huellas[nombre] = huella(ROOT / nombre)
    validacion = subprocess.run(
        [sys.executable, "validar_conocimiento.py"], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if validacion.returncode:
        raise ValueError("Falló validar_conocimiento.py: " + validacion.stderr)
    desarrollo = cargar(ROOT / "data/evaluacion/casos_desarrollo.json")
    if desarrollo.get("version") != 1 or desarrollo.get("grupo") != "desarrollo":
        raise ValueError("Versión o grupo de desarrollo inesperado")
    casos = desarrollo.get("casos")
    if not isinstance(casos, list) or len(casos) != 60:
        raise ValueError("Se esperaban 60 casos de desarrollo")
    hechos = cargar(ROOT / "data/conocimiento/hechos.json")
    diagnosticos = cargar(ROOT / "data/conocimiento/diagnosticos.json")
    sintomas = {h["id"] for h in hechos["hechos"] if h["tipo"] == "sintoma"}
    ids_diagnosticos = sorted(d["id"] for d in diagnosticos["diagnosticos"])
    if len(ids_diagnosticos) != 18:
        raise ValueError("Se esperaban 18 diagnósticos")
    preguntas = cargar_preguntas(ROOT / "data/interfaz/preguntas.json", sintomas)
    rutas = cargar_rutas(ROOT / "data/interfaz/rutas.json", preguntas)
    refs = {f["id"] for f in cargar(ROOT / "data/evaluacion/fuentes.json")["fuentes"]}
    for indice, caso in enumerate(casos, 1):
        if caso.get("id") != f"D{indice:03d}":
            raise ValueError(f"ID de desarrollo inesperado en posición {indice}")
        _validar_caso(caso, preguntas, rutas, sintomas, set(ids_diagnosticos), refs)
    elegibles = [c for c in casos if c["alcance"] in ALCANCES_ELEGIBLES]
    excluidos = [c for c in casos if c["alcance"] not in ALCANCES_ELEGIBLES]
    if (len(elegibles), len(excluidos), sum(bool(c["hipotesis_defendibles"]) for c in elegibles),
            sum(c["prioridad_revision"] is not None for c in elegibles)) != (55, 5, 38, 10):
        raise ValueError("Cambió la distribución esperada de desarrollo")
    if [c["id"] for c in excluidos] != ["D012", "D022", "D032", "D043", "D060"]:
        raise ValueError("Cambió la lista de casos excluidos")
    return desarrollo, ids_diagnosticos, {
        "huellas": huellas, "validacion_conocimiento": validacion.stdout.strip(),
        "reserva_sha256_registrada": manifiesto["archivos"]["data/evaluacion/casos_finales_reservados.json"],
        "preguntas": preguntas, "rutas": rutas,
    }


def proyectar_entrada(caso: dict) -> dict:
    """Únicos campos del caso accesibles durante la inferencia."""
    return {clave: caso[clave] for clave in ("id", "ruta", "tipo_escenario", "trayecto_preguntas", "observaciones")}


def reproducir_entrada(entrada: dict, preguntas, rutas) -> dict[str, str]:
    por_id = {p.id: p for p in preguntas}
    gestor = GestorPreguntas(preguntas, rutas, entrada["ruta"])
    observaciones = {}
    for pregunta_id in entrada["trayecto_preguntas"]:
        siguiente = gestor.siguiente()
        if siguiente is None or siguiente.id != pregunta_id:
            raise ValueError(f"{entrada['id']}: trayecto inalcanzable")
        hecho = por_id[pregunta_id].hecho
        estado = entrada["observaciones"][hecho]
        opciones = [r for r in RespuestaVisible if por_id[pregunta_id].estado_para(r).value == estado]
        if len(opciones) != 1:
            raise ValueError(f"{entrada['id']}: estado sin respuesta única")
        gestor.responder(pregunta_id, opciones[0])
        observaciones[hecho] = estado
    if gestor.estado_final is None or observaciones != entrada["observaciones"]:
        raise ValueError(f"{entrada['id']}: observaciones distintas del trayecto")
    return observaciones


def serializar_resultado(resultado, derivados: set[str]) -> dict:
    orden = [d.id for d in (resultado.principal, *resultado.alternativos) if d is not None]
    if len(orden) != len(set(orden)):
        raise ValueError("El motor produjo diagnósticos duplicados")
    return {
        "orden": orden,
        "principal": orden[0] if orden else None,
        "reglas_activadas": list(resultado.memoria.reglas_activadas),
        "hechos_derivados": {
            ident: resultado.memoria.hechos[ident].value for ident in sorted(derivados)
            if ident in resultado.memoria.hechos and resultado.memoria.hechos[ident].value != "desconocido"
        },
    }


def comprobar_bc(predicciones: dict) -> list[str]:
    return [
        caso["id"] for caso in predicciones["casos"]
        if set(caso["modelos"]["B"]["orden"]) != set(caso["modelos"]["C"]["orden"])
    ]


def capturar(salida: Path) -> None:
    bruto = salida / "predicciones_brutas.json"
    if bruto.exists():
        raise ValueError("Ya existe la captura; use otra carpeta para no sobrescribirla")
    desarrollo, diagnosticos, base = comprobar_base()
    def git(*argumentos):
        return subprocess.run(["git", *argumentos], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", check=True).stdout.strip()
    git_head_previo = git("rev-parse", "HEAD")
    git_estado_previo = git("status", "--porcelain=v1")
    entradas = [proyectar_entrada(c) for c in desarrollo["casos"] if c["alcance"] in ALCANCES_ELEGIBLES]
    excluidos = [c["id"] for c in desarrollo["casos"] if c["alcance"] not in ALCANCES_ELEGIBLES]
    derivados = {h["id"] for h in cargar(ROOT / "data/conocimiento_avance2/hechos.json")["hechos"]}
    motores = {nombre: seleccionar_modelo(nombre) for nombre in MODELOS}
    registros = []
    for entrada in entradas:
        observaciones = reproducir_entrada(entrada, base["preguntas"], base["rutas"])
        modelos = {
            nombre: serializar_resultado(motor.evaluar(dict(observaciones)), derivados)
            for nombre, motor in motores.items()
        }
        for nombre in MODELOS:
            if not set(modelos[nombre]["orden"]) <= set(diagnosticos):
                raise ValueError(f"{entrada['id']}: salida {nombre} fuera de catálogo")
        registros.append({
            "id": entrada["id"], "ruta": entrada["ruta"],
            "tipo_escenario": entrada["tipo_escenario"],
            "observaciones": observaciones, "modelos": modelos,
        })
    predicciones = {
        "version": 1, "desarrollo_sha256": base["huellas"]["data/evaluacion/casos_desarrollo.json"],
        "elegibles": len(registros), "excluidos": excluidos, "casos": registros,
    }
    guardar(bruto, predicciones)
    procedencia = {
        "version": 1, "python": sys.version, "git_head": git_head_previo,
        "git_estado_previo": git_estado_previo,
        "huellas": base["huellas"], "predicciones_sha256": huella(bruto),
        "reserva_sha256_registrada": base["reserva_sha256_registrada"],
        "validacion_conocimiento": base["validacion_conocimiento"],
        "comandos": ["python evaluar_desarrollo.py capturar", "python evaluar_desarrollo.py analizar"],
        "advertencia_reserva": "La reserva final no se abrió ni se procesó; su huella registrada no se recalculó.",
    }
    guardar(salida / "proveniencia.json", procedencia)
    diferencias = comprobar_bc(predicciones)
    if diferencias:
        guardar(salida / "regresiones_bc.json", {"ids": diferencias})
        raise ValueError("B y C difieren en sus conjuntos: " + ", ".join(diferencias))
    print(f"Captura guardada: {len(registros)} casos elegibles, {len(excluidos)} excluidos; B/C con conjuntos iguales.")


def razon(numerador: int | float, denominador: int) -> dict:
    return {"numerador": numerador, "denominador": denominador,
            "valor": numerador / denominador if denominador else None}


def calcular_modelo(casos: list[dict], nombre: str, diagnosticos: list[str]) -> tuple[dict, dict, list[dict]]:
    tp = fp = fn = exactos = positivos = vacios = 0
    exactos_positivos = exactos_vacios = principal = 0
    abstenciones_correctas = abstenciones_incorrectas = salidas_espurias = 0
    extras = omitidas = 0
    prioridades = aciertos_prioridad = 0
    reciprocos = 0.0
    matrices = {d: {"tn": 0, "fp": 0, "fn": 0, "tp": 0} for d in diagnosticos}
    errores = []
    for caso in casos:
        referencia = set(caso["referencia"])
        orden = caso["modelos"][nombre]["orden"]
        prediccion = set(orden)
        extra = sorted(prediccion - referencia)
        omitida = sorted(referencia - prediccion)
        coincide = prediccion == referencia
        exactos += coincide
        positivos += bool(referencia)
        vacios += not referencia
        exactos_positivos += bool(referencia) and coincide
        exactos_vacios += not referencia and coincide
        principal += bool(referencia) and bool(orden) and orden[0] in referencia
        abstenciones_correctas += not referencia and not prediccion
        abstenciones_incorrectas += bool(referencia) and not prediccion
        salidas_espurias += not referencia and bool(prediccion)
        tp += len(prediccion & referencia)
        fp += len(extra)
        fn += len(omitida)
        extras += len(extra)
        omitidas += len(omitida)
        for d in diagnosticos:
            clave = ("tp" if d in referencia else "fp") if d in prediccion else ("fn" if d in referencia else "tn")
            matrices[d][clave] += 1
        if caso["prioridad"] is not None:
            prioridades += 1
            objetivo = caso["prioridad"]
            aciertos_prioridad += bool(orden) and orden[0] == objetivo
            reciprocos += 1 / (orden.index(objetivo) + 1) if objetivo in orden else 0
        errores.append({
            "id": caso["id"], "ruta": caso["ruta"], "tipo_escenario": caso["tipo_escenario"],
            "modelo": nombre, "referencia": sorted(referencia), "prediccion": orden,
            "exacto": coincide, "extras": extra, "omitidas": omitida,
            "abstencion_correcta": not referencia and not prediccion,
            "abstencion_incorrecta": bool(referencia) and not prediccion,
            "salida_espuria": not referencia and bool(prediccion),
            "principal_correcto": bool(referencia) and bool(orden) and orden[0] in referencia,
            "prioridad_referencia": caso["prioridad"],
            "prioridad_correcta": None if caso["prioridad"] is None else bool(orden) and orden[0] == caso["prioridad"],
        })
    n = len(casos)
    for d, valores in matrices.items():
        valores["soporte"] = valores["tp"] + valores["fn"]
        valores["total"] = n
        if sum(valores[x] for x in ("tn", "fp", "fn", "tp")) != n:
            raise ValueError(f"Matriz inconsistente: {d}")
    metricas = {
        "casos": n, "positivos": positivos, "referencia_vacia": vacios,
        "accuracy": razon(exactos, n),
        "accuracy_positivos": razon(exactos_positivos, positivos),
        "accuracy_referencia_vacia": razon(exactos_vacios, vacios),
        "tp": tp, "fp": fp, "fn": fn,
        "precision_micro": razon(tp, tp + fp),
        "recall_micro": razon(tp, tp + fn),
        "f1_micro": razon(2 * tp, 2 * tp + fp + fn),
        "principal": razon(principal, positivos),
        "abstenciones_correctas": razon(abstenciones_correctas, vacios),
        "abstenciones_incorrectas": razon(abstenciones_incorrectas, positivos),
        "salidas_espurias": razon(salidas_espurias, vacios),
        "hipotesis_extra": extras, "hipotesis_omitidas": omitidas,
        "prioridad_principal": razon(aciertos_prioridad, int(prioridades)),
        "prioridad_rango_reciproco_medio": razon(reciprocos, int(prioridades)),
    }
    return metricas, matrices, errores


def distribuciones(errores: list[dict], campo: str) -> dict:
    grupos = {}
    for error in errores:
        clave = error[campo]
        d = grupos.setdefault(clave, {"casos": 0, "exactos": 0, "con_extras": 0,
                                     "con_omisiones": 0, "abstenciones_incorrectas": 0,
                                     "abstenciones_correctas": 0, "salidas_espurias": 0})
        d["casos"] += 1
        d["exactos"] += error["exacto"]
        d["con_extras"] += bool(error["extras"])
        d["con_omisiones"] += bool(error["omitidas"])
        d["abstenciones_incorrectas"] += error["abstencion_incorrecta"]
        d["abstenciones_correctas"] += error["abstencion_correcta"]
        d["salidas_espurias"] += error["salida_espuria"]
    return dict(sorted(grupos.items()))


def porcentaje(r: dict) -> str:
    return "indefinido" if r["valor"] is None else f"{100 * r['valor']:.1f} %"


def celda(r: dict) -> str:
    return f"{r['numerador']:g}/{r['denominador']} ({porcentaje(r)})"


def svg_barras(salida: Path, titulo: str, etiquetas: list[str], series: dict[str, list[float | None]]) -> None:
    ancho = 900
    alto = 120 + len(etiquetas) * 72
    colores = {"A": "#2563eb", "B": "#d97706", "C": "#059669"}
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
              '<rect width="100%" height="100%" fill="white"/>',
              f'<text x="24" y="35" font-size="22" font-family="sans-serif">{html.escape(titulo)}</text>']
    for j, modelo in enumerate(MODELOS):
        partes.append(f'<rect x="{640+j*78}" y="17" width="13" height="13" fill="{colores[modelo]}"/>')
        partes.append(f'<text x="{657+j*78}" y="29" font-size="14" font-family="sans-serif">{modelo}</text>')
    for i, etiqueta in enumerate(etiquetas):
        y = 75 + i * 72
        partes.append(f'<text x="24" y="{y+15}" font-size="14" font-family="sans-serif">{html.escape(etiqueta)}</text>')
        for j, modelo in enumerate(MODELOS):
            valor = series[modelo][i]
            if valor is None:
                continue
            yy = y + 22 + j * 13
            partes.append(f'<rect x="230" y="{yy}" width="{round(520*valor)}" height="10" fill="{colores[modelo]}"/>')
            partes.append(f'<text x="{min(760, 235+round(520*valor))}" y="{yy+9}" font-size="12" font-family="sans-serif">{100*valor:.1f}%</text>')
    partes.append('</svg>')
    salida.write_text("\n".join(partes) + "\n", encoding="utf-8")


def svg_matrices(salida: Path, modelo: str, matrices: dict) -> None:
    ancho, alto = 1080, 1060
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
              '<rect width="100%" height="100%" fill="white"/>',
              f'<text x="20" y="32" font-size="22" font-family="sans-serif">Modelo {modelo}: matrices por diagnóstico (N=55)</text>',
              '<text x="20" y="55" font-size="13" font-family="sans-serif">Filas: referencia ausente/presente. Columnas: predicción ausente/presente.</text>']
    for i, (diagnostico, m) in enumerate(sorted(matrices.items())):
        x = 20 + (i % 3) * 355
        y = 78 + (i // 3) * 160
        partes.append(f'<text x="{x}" y="{y+15}" font-size="15" font-family="sans-serif">{html.escape(diagnostico)}</text>')
        partes.append(f'<text x="{x}" y="{y+34}" font-size="12" font-family="sans-serif">soporte={m["soporte"]}</text>')
        for j, clave in enumerate(("tn", "fp", "fn", "tp")):
            xx = x + (j % 2) * 164
            yy = y + 46 + (j // 2) * 45
            valor = m[clave]
            color = "#d1fae5" if clave in ("tn", "tp") else "#fee2e2"
            partes.append(f'<rect x="{xx}" y="{yy}" width="152" height="38" fill="{color}" stroke="#9ca3af"/>')
            partes.append(f'<text x="{xx+10}" y="{yy+24}" font-size="15" font-family="sans-serif">{clave.upper()}: {valor}</text>')
    partes.append('</svg>')
    salida.write_text("\n".join(partes) + "\n", encoding="utf-8")


def informe(metricas: dict, matrices: dict, distribucion: dict, errores: list[dict],
            comparaciones: dict, procedencia: dict) -> str:
    lineas = ["# Resultados experimentales — Avance 2, etapa 5", "",
              "## Metodología y custodia", "",
              "Se evaluaron 55 de los 60 casos de desarrollo: 54 de cuestionario extremo a extremo y D050 fuera del catálogo. Se excluyeron D012, D022, D032, D043 y D060 por limitación del cuestionario. Las viñetas son académicas; las etiquetas son hipótesis defendibles, no fallas físicas confirmadas.", "",
              "Cada trayecto se reprodujo con el gestor de preguntas. Los tres motores recibieron las mismas observaciones obtenibles, con `verdadero`, `falso` y `desconocido` distintos. La captura bruta se guardó antes de comparar etiquetas; relato, justificación y prioridad no fueron entradas de los motores. La reserva final no se abrió ni se ejecutó.", "",
              f"Versión de desarrollo: SHA-256 `{procedencia['huellas']['data/evaluacion/casos_desarrollo.json']}`. Python: `{procedencia['python'].split()[0]}`. Git HEAD: `{procedencia['git_head']}`. Predicciones: SHA-256 `{procedencia['predicciones_sha256']}`. Las huellas completas, el estado previo de Git y los comandos están en `proveniencia.json`.", "",
              "## Tabla comparativa", "",
              "| Métrica | A | B | C |", "| --- | ---: | ---: | ---: |"]
    filas = [("Accuracy exacto", "accuracy"), ("Accuracy con referencia positiva", "accuracy_positivos"),
             ("Accuracy con referencia vacía", "accuracy_referencia_vacia"),
             ("Precisión micro", "precision_micro"), ("Recall micro", "recall_micro"),
             ("F1 micro", "f1_micro"), ("Principal en referencia", "principal"),
             ("Abstenciones correctas", "abstenciones_correctas"),
             ("Abstenciones incorrectas", "abstenciones_incorrectas"),
             ("Salidas espurias con referencia vacía", "salidas_espurias"),
             ("Principal prioritario, mismos 10 casos", "prioridad_principal"),
             ("Rango recíproco medio, mismos 10 casos", "prioridad_rango_reciproco_medio")]
    for nombre, clave in filas:
        if clave == "prioridad_rango_reciproco_medio":
            valores = [f"{metricas[m][clave]['numerador']:.3f}/{metricas[m][clave]['denominador']} = {metricas[m][clave]['valor']:.3f}" for m in MODELOS]
        else:
            valores = [celda(metricas[m][clave]) for m in MODELOS]
        lineas.append("| " + nombre + " | " + " | ".join(valores) + " |")
    for nombre, clave in (("TP", "tp"), ("FP / hipótesis extra", "fp"), ("FN / hipótesis omitidas", "fn")):
        lineas.append("| " + nombre + " | " + " | ".join(str(metricas[m][clave]) for m in MODELOS) + " |")
    lineas += ["", "Los 55 casos incluyen 38 referencias positivas y 17 vacías. La prioridad se evalúa sobre los mismos 10 casos para A, B y C; su rango recíproco vale cero cuando la prioridad está ausente. Las métricas micro usan los TP, FP y FN agregados, sin crear verdaderos positivos por pares vacíos.", "",
               "![Métricas de A, B y C](../data/evaluacion/resultados_etapa5/graficas/metricas.svg)", "",
               "![Acierto del diagnóstico principal](../data/evaluacion/resultados_etapa5/graficas/principal.svg)", "",
               "### Comparación de prioridades justificadas", "",
               "| Caso | Prioridad | A: principal / rango | B: principal / rango | C: principal / rango |",
               "| --- | --- | --- | --- | --- |"]
    por_caso = {(e["id"], e["modelo"]): e for e in errores}
    prioridades = sorted(e["id"] for e in errores if e["modelo"] == "A" and e["prioridad_referencia"])
    for ident in prioridades:
        objetivo = por_caso[(ident, "A")]["prioridad_referencia"]
        valores = []
        for modelo in MODELOS:
            orden = por_caso[(ident, modelo)]["prediccion"]
            rango = orden.index(objetivo) + 1 if objetivo in orden else "ausente"
            valores.append(f"`{orden[0]}` / {rango}" if orden else f"ninguno / {rango}")
        lineas.append(f"| {ident} | `{objetivo}` | " + " | ".join(valores) + " |")
    lineas += ["",
               "## Matrices de confusión por diagnóstico", "",
               "Cada matriz usa 55 casos. Filas: referencia ausente/presente; columnas: predicción ausente/presente. La tabla presenta TN, FP, FN y TP en ese orden.", ""]
    bajos = sorted(d for d, v in matrices["A"].items() if v["soporte"] <= 2)
    lineas += ["Soporte bajo (≤2 casos): " + (", ".join(f"`{d}` ({matrices['A'][d]['soporte']})" for d in bajos) or "ninguno") + ". Interpretar sus resultados individuales con cautela.", ""]
    for modelo in MODELOS:
        lineas += [f"### Modelo {modelo}", "", "| Diagnóstico | Soporte | TN | FP | FN | TP |",
                   "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for d, m in sorted(matrices[modelo].items()):
            lineas.append(f"| `{d}` | {m['soporte']} | {m['tn']} | {m['fp']} | {m['fn']} | {m['tp']} |")
        lineas += ["", f"![Matrices del Modelo {modelo}](../data/evaluacion/resultados_etapa5/graficas/matrices_{modelo}.svg)", ""]
    lineas += ["## Errores por ruta y tipo de escenario", "",
               "Los conteos de extras, omisiones y abstenciones pueden solaparse dentro de un caso.", ""]
    for campo, titulo in (("ruta", "Ruta"), ("tipo_escenario", "Tipo de escenario")):
        lineas += [f"### {titulo}", "", "| Modelo | Grupo | Casos | Exactos | Con extras | Con omisiones | Abstenciones indebidas | Salidas espurias |",
                   "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for modelo in MODELOS:
            for grupo, d in distribucion[modelo][campo].items():
                lineas.append(f"| {modelo} | {grupo} | {d['casos']} | {d['exactos']} | {d['con_extras']} | {d['con_omisiones']} | {d['abstenciones_incorrectas']} | {d['salidas_espurias']} |")
        lineas.append("")
    lineas += ["## Análisis de casos y comparaciones", ""]
    for modelo in MODELOS:
        es = [e for e in errores if e["modelo"] == modelo]
        def ids(predicado):
            return ", ".join(e["id"] for e in es if predicado(e)) or "ninguno"
        lineas += [f"### Modelo {modelo}", "",
                   f"- Conjunto exacto: {ids(lambda e: e['exacto'])}.",
                   f"- Hipótesis omitidas: {ids(lambda e: bool(e['omitidas']))}.",
                   f"- Hipótesis adicionales: {ids(lambda e: bool(e['extras']))}.",
                   f"- Abstención indebida: {ids(lambda e: e['abstencion_incorrecta'])}.",
                   f"- Abstención correcta: {ids(lambda e: e['abstencion_correcta'])}.", ""]
    lineas += [f"A y B difirieron en el conjunto de {len(comparaciones['conjuntos_a_b'])}/55 casos: " + (", ".join(comparaciones["conjuntos_a_b"]) or "ninguno") + ".",
               f"B y C mantuvieron el mismo conjunto en 55/55 casos. Cambiaron el orden en {len(comparaciones['orden_b_c'])}/55: " + (", ".join(comparaciones["orden_b_c"]) or "ninguno") + ".",
               f"B activó al menos un hecho derivado en {len(comparaciones['hechos_derivados_b'])}/55 casos: " + (", ".join(comparaciones["hechos_derivados_b"]) or "ninguno") + ".",
               ""]
    if not comparaciones["conjuntos_a_b"]:
        lineas.append("En este desarrollo, los seis casos con hechos derivados no añadieron ni quitaron hipótesis frente a A. La ampliación de conocimiento de B produjo trazas adicionales, pero no cambió las métricas de conjunto observadas.")
    else:
        lineas.append("Las diferencias A/B pueden reflejar el conocimiento adicional de B; estos datos no aíslan un efecto causal del mecanismo multinivel.")
    lineas += ["Los hechos derivados se examinan mediante trazas y su activación, sin contarlos como observaciones independientes. C solo reordena las hipótesis de B, por lo que no mejora su accuracy de conjunto. Las prioridades son órdenes técnicos de revisión, no probabilidades.", ""]
    errores_a = [e for e in errores if e["modelo"] == "A" and not e["exacto"]]
    if errores_a:
        extras = Counter(d for e in errores_a for d in e["extras"])
        omitidas = Counter(d for e in errores_a for d in e["omitidas"])
        lineas += [f"Los {len(errores_a)} errores de conjunto de A (iguales para B/C aquí) incluyen hipótesis extra "
                   + ", ".join(f"`{d}` ({n})" for d, n in sorted(extras.items()))
                   + " y omitidas " + (", ".join(f"`{d}` ({n})" for d, n in sorted(omitidas.items())) or "ninguna") + ".",
                   "Las salidas adicionales se concentran en hipótesis amplias de revisión de energía e indicios de video; esta es una descripción de los casos observados, no una indicación para ajustar reglas durante la etapa.", ""]
    lineas += [
               "## Reproducción, limitaciones y conclusiones preliminares", "",
               "Desde la raíz del repositorio: `python evaluar_desarrollo.py capturar` y luego `python evaluar_desarrollo.py analizar`. Para repetir sin sobrescribir la captura original, pasar `--salida RUTA_TEMPORAL` a ambos comandos. Los JSON y SVG se regeneran desde la captura y las referencias originales, sin editar cifras a mano.", "",
               "`python validar_casos.py` y la batería global de `unittest discover` se omitieron porque actualmente abren los casos finales reservados. Se ejecutaron pruebas funcionales seleccionadas que no hacen esa lectura. Los cinco casos excluidos no contribuyen a denominadores. La baja frecuencia de varios diagnósticos y la similitud entre algunas viñetas limitan la generalización. Estas cifras muestran concordancia con viñetas académicas hipotéticas y no precisión demostrada en computadoras reales. No se selecciona modelo en esta etapa.", ""]
    return "\n".join(lineas)


def analizar(salida: Path) -> None:
    bruto = salida / "predicciones_brutas.json"
    procedencia = cargar(salida / "proveniencia.json")
    if huella(bruto) != procedencia["predicciones_sha256"]:
        raise ValueError("La captura bruta cambió")
    predicciones = cargar(bruto)
    diferencias = comprobar_bc(predicciones)
    if diferencias:
        guardar(salida / "regresiones_bc.json", {"ids": diferencias})
        raise ValueError("B y C difieren en sus conjuntos: " + ", ".join(diferencias))
    desarrollo, diagnosticos, base = comprobar_base()
    if base["huellas"] != procedencia["huellas"]:
        raise ValueError("Cambió el desarrollo, catálogo o motor desde la captura")
    if predicciones["desarrollo_sha256"] != base["huellas"]["data/evaluacion/casos_desarrollo.json"]:
        raise ValueError("La versión de desarrollo no coincide")
    referencias = {c["id"]: c for c in desarrollo["casos"] if c["alcance"] in ALCANCES_ELEGIBLES}
    if len(predicciones["casos"]) != 55 or [c["id"] for c in predicciones["casos"]] != list(referencias):
        raise ValueError("La captura no corresponde a los 55 casos elegibles")
    casos = []
    for pred in predicciones["casos"]:
        ref = referencias[pred["id"]]
        if (pred["ruta"], pred["tipo_escenario"]) != (ref["ruta"], ref["tipo_escenario"]):
            raise ValueError(f"Metadatos cambiados: {pred['id']}")
        casos.append({**pred, "referencia": ref["hipotesis_defendibles"],
                      "prioridad": ref["prioridad_revision"]["diagnostico"] if ref["prioridad_revision"] else None})
    metricas = {}
    matrices = {}
    errores = []
    distribucion = {}
    for modelo in MODELOS:
        metricas[modelo], matrices[modelo], detalle = calcular_modelo(casos, modelo, diagnosticos)
        errores.extend(detalle)
        distribucion[modelo] = {campo: distribuciones(detalle, campo) for campo in ("ruta", "tipo_escenario")}
    comparaciones = {
        "conjuntos_a_b": [c["id"] for c in casos if set(c["modelos"]["A"]["orden"]) != set(c["modelos"]["B"]["orden"])],
        "orden_b_c": [c["id"] for c in casos if c["modelos"]["B"]["orden"] != c["modelos"]["C"]["orden"]],
        "hechos_derivados_b": [c["id"] for c in casos if c["modelos"]["B"]["hechos_derivados"]],
    }
    guardar(salida / "metricas.json", metricas)
    guardar(salida / "matrices.json", matrices)
    guardar(salida / "distribuciones.json", distribucion)
    guardar(salida / "errores.json", errores)
    guardar(salida / "comparaciones.json", comparaciones)
    guardar(salida / "advertencias.json", {
        "diagnosticos_soporte_bajo_hasta_dos": [
            d for d, m in sorted(matrices["A"].items()) if m["soporte"] <= 2
        ],
        "casos_excluidos": predicciones["excluidos"],
        "pruebas_globales_omitidas": ["python validar_casos.py", "python -m unittest discover -s tests -v"],
        "limites": [
            "Viñetas académicas hipotéticas; no confirman fallas físicas ni precisión en equipos reales.",
            "A y B no aíslan el efecto del mecanismo multinivel porque B usa conocimiento adicional.",
            "C reordena hipótesis de B; no cambia la exactitud de conjunto.",
        ],
    })
    graficas = salida / "graficas"
    graficas.mkdir(parents=True, exist_ok=True)
    svg_barras(graficas / "metricas.svg", "Métricas de conjunto y multietiqueta (%)",
               ["Accuracy", "Precisión micro", "Recall micro", "F1 micro"],
               {m: [metricas[m][k]["valor"] for k in ("accuracy", "precision_micro", "recall_micro", "f1_micro")] for m in MODELOS})
    svg_barras(graficas / "principal.svg", "Diagnóstico principal y prioridad (%)",
               ["Principal en referencia (38)", "Principal prioritario (10)"],
               {m: [metricas[m][k]["valor"] for k in ("principal", "prioridad_principal")] for m in MODELOS})
    for modelo in MODELOS:
        svg_matrices(graficas / f"matrices_{modelo}.svg", modelo, matrices[modelo])
    if salida == SALIDA:
        (ROOT / "docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md").write_text(
            informe(metricas, matrices, distribucion, errores, comparaciones, procedencia), encoding="utf-8")
    print("Análisis guardado: 55 casos, 18 matrices por modelo y prioridad A/B/C sobre 10 casos.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fase", choices=("capturar", "analizar"))
    parser.add_argument("--salida", type=Path, default=SALIDA)
    args = parser.parse_args()
    try:
        if args.fase == "capturar":
            capturar(args.salida.resolve())
        else:
            analizar(args.salida.resolve())
    except (OSError, ValueError, KeyError, ErrorCasos) as error:
        print(f"Evaluación detenida: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
