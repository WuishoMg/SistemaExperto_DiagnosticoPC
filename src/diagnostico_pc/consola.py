"""Interfaz de texto para consultar el modelo seleccionado."""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from .modelo_a import DiagnosticoInferido
from .contratos import ResultadoInferencia
from .selector import MODELO_PREDETERMINADO, MODELOS, seleccionar_modelo
from .modelo_b import ResultadoModeloB, TrazaInferencia
from .modelo_c import ResultadoModeloC, motivo_precedencia
from .conocimiento_c import CALIDADES, PRIORIDADES
from .coherencia import detectar_contradicciones
from .hechos import EstadoHecho, normalizar_observaciones
from .preguntas import ErrorPreguntas, Pregunta, RespuestaVisible, cargar_preguntas
from .gestor_preguntas import GestorPreguntas
from .rutas import CatalogoRutas, ErrorRutas, cargar_rutas
from .validacion import ErrorConocimiento


RESPUESTAS = {
    "1": RespuestaVisible.SI,
    "s": RespuestaVisible.SI,
    "si": RespuestaVisible.SI,
    "sí": RespuestaVisible.SI,
    "2": RespuestaVisible.NO,
    "n": RespuestaVisible.NO,
    "no": RespuestaVisible.NO,
    "3": RespuestaVisible.NO_ESTOY_SEGURO,
    "": RespuestaVisible.NO_ESTOY_SEGURO,
    "?": RespuestaVisible.NO_ESTOY_SEGURO,
    "no estoy seguro": RespuestaVisible.NO_ESTOY_SEGURO,
}


@dataclass(frozen=True)
class ConsultaCondicional:
    observaciones: dict[str, str]
    terminal: str | None


def preguntar_sintomas(
    preguntas: tuple[Pregunta, ...], entrada: TextIO, salida: TextIO
) -> dict[str, str]:
    """Recoge respuestas visibles usando el mapeo propio de cada pregunta."""
    respuestas: dict[str, str] = {}
    print("Responde con 1/2/3 o con s/n/?.", file=salida)
    for numero, pregunta in enumerate(preguntas, start=1):
        while True:
            print(f"\n{numero:02d}/{len(preguntas)} {pregunta.texto}", file=salida)
            print(f"Ayuda: {pregunta.ayuda}", file=salida)
            print("1. Sí", file=salida)
            print("2. No", file=salida)
            print("3. No estoy seguro", file=salida)
            print("Respuesta: ", end="", file=salida, flush=True)
            respuesta = entrada.readline()
            if respuesta == "":
                raise EOFError("La consulta terminó antes de responder todos los síntomas")
            normalizada = RESPUESTAS.get(respuesta.strip().lower())
            if normalizada is not None:
                respuestas[pregunta.hecho] = pregunta.estado_para(normalizada).value
                break
            print("Respuesta inválida; elige Sí, No o No estoy seguro.", file=salida)
    return respuestas


def _elegir_categoria(rutas: CatalogoRutas, entrada: TextIO, salida: TextIO) -> str:
    print("\n¿Qué problema presenta tu computadora?", file=salida)
    for numero, categoria in enumerate(rutas.categorias, start=1):
        print(f"{numero}. {categoria.nombre}", file=salida)
    while True:
        print("Elige una opción (1-7): ", end="", file=salida, flush=True)
        linea = entrada.readline()
        if linea == "":
            raise EOFError("La consulta terminó antes de elegir un problema")
        opcion = linea.strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(rutas.categorias):
            return rutas.categorias[int(opcion) - 1].id
        print("Opción inválida; elige un número del 1 al 7.", file=salida)


def _confirmar_cambio(gestor: GestorPreguntas, rutas: CatalogoRutas, entrada: TextIO, salida: TextIO) -> bool:
    nueva = _elegir_categoria(rutas, entrada, salida)
    print("El cambio inicia una consulta nueva y descarta las respuestas actuales. ¿Confirmas? (s/n): ",
          end="", file=salida, flush=True)
    linea = entrada.readline()
    if linea == "":
        raise EOFError("La consulta terminó antes de confirmar el cambio")
    if linea.strip().lower() in {"s", "si", "sí", "1"}:
        gestor.cambiar_categoria(nueva)
        print("Consulta nueva iniciada.", file=salida)
        return True
    print("Se conserva la consulta actual.", file=salida)
    return False


def _editar_respuesta(gestor: GestorPreguntas, entrada: TextIO, salida: TextIO) -> None:
    if not gestor.historial:
        print("Todavía no hay respuestas para editar.", file=salida)
        return
    print("Respuestas de esta consulta:", file=salida)
    for numero, registro in enumerate(gestor.historial, start=1):
        texto = gestor.preguntas[registro.pregunta_id].texto
        print(f"{numero}. {texto} — {registro.respuesta.value}", file=salida)
    print("Número a corregir (las respuestas posteriores se volverán a preguntar): ",
          end="", file=salida, flush=True)
    linea = entrada.readline()
    if linea == "":
        raise EOFError("La consulta terminó antes de elegir una respuesta")
    if linea.strip().isdigit():
        try:
            gestor.editar(int(linea.strip()) - 1)
            return
        except ValueError:
            pass
    print("Número fuera del historial; no se cambió ninguna respuesta.", file=salida)


def preguntar_condicional(
    preguntas: tuple[Pregunta, ...], rutas: CatalogoRutas, entrada: TextIO, salida: TextIO
) -> ConsultaCondicional:
    """Conduce una consulta; la inferencia queda exclusivamente en Modelo A."""
    categoria = _elegir_categoria(rutas, entrada, salida)
    gestor = GestorPreguntas(preguntas, rutas, categoria)
    print("Responde con 1/2/3 o s/n/?. v: volver; e: editar; c: cambiar; f: finalizar.", file=salida)
    ruta_anterior: str | None = None
    while True:
        ruta = gestor.categoria_actual
        if ruta != ruta_anterior:
            print(f"\nRuta actual: {rutas.por_id[ruta].nombre}", file=salida)
            ruta_anterior = ruta
        contradicciones = gestor.contradicciones
        if contradicciones:
            print("\nHay respuestas que no coinciden para este intento de uso:", file=salida)
            for contradiccion in contradicciones:
                preguntas_afectadas = "; ".join(
                    f"«{gestor.preguntas[identificador].texto}»"
                    for identificador in contradiccion.preguntas
                )
                print(f"- {contradiccion.explicacion} Revisa: {preguntas_afectadas}", file=salida)
            print("Escribe v para volver, e para editar o c para cambiar de problema: ",
                  end="", file=salida, flush=True)
            linea = entrada.readline()
            if linea == "":
                raise EOFError("La consulta terminó con respuestas contradictorias")
            accion = linea.strip().lower()
            if accion == "v":
                gestor.volver()
            elif accion == "e":
                _editar_respuesta(gestor, entrada, salida)
            elif accion == "c":
                if _confirmar_cambio(gestor, rutas, entrada, salida):
                    ruta_anterior = None
            else:
                print("Primero corrige la contradicción con v o e.", file=salida)
            continue
        pregunta = gestor.siguiente()
        if pregunta is None:
            terminal = gestor.estado_final
            mensajes = {
                "@resultado": "Se completaron las comprobaciones útiles de esta ruta.",
                "@insuficiente": "No hay observaciones suficientes para continuar esta ruta de forma útil.",
                "@bloqueo_energia": "Las señales de encendido no permiten continuar con la falla elegida. Puedes iniciar otro diagnóstico.",
                "@bloqueo_imagen": "Ahora aparece imagen y no se observó una distorsión; puedes elegir otro diagnóstico.",
                "@bloqueo_sistema": "Hay energía e imagen, pero el sistema no inicia. Puedes cambiar al diagnóstico del sistema.",
                "@patron_red_sin_causa": "Se registró un problema de conexión, pero estas observaciones no identifican todavía su causa.",
                "@error_uso_sin_causa": "Se registró un error durante el uso del sistema, pero estas observaciones no identifican todavía su causa.",
            }
            print(f"\n{mensajes.get(terminal, 'Consulta detenida.')}", file=salida)
            print("Enter: ver resultado disponible; v: volver; e: editar; c: cambiar; f: finalizar.", file=salida)
            linea = entrada.readline()
            accion = linea.strip().lower()
            if accion == "v":
                if gestor.volver() is None:
                    print("Todavía no hay respuestas para revisar.", file=salida)
                continue
            if accion == "e":
                _editar_respuesta(gestor, entrada, salida)
                continue
            if accion == "c":
                if _confirmar_cambio(gestor, rutas, entrada, salida):
                    ruta_anterior = None
                continue
            if accion in {"", "f"} or linea == "":
                return ConsultaCondicional(gestor.observaciones, terminal)
            print("Opción inválida; usa Enter, v, e, c o f.", file=salida)
            continue
        print(f"\n{pregunta.texto}", file=salida)
        print(f"Ayuda: {pregunta.ayuda}", file=salida)
        print("1. Sí", file=salida)
        print("2. No", file=salida)
        print("3. No estoy seguro", file=salida)
        print("Respuesta (1/2/3, s/n/?, v, e, c o f): ", end="", file=salida, flush=True)
        linea = entrada.readline()
        if linea == "":
            raise EOFError("La consulta terminó antes de responder la pregunta")
        accion = linea.strip().lower()
        if accion == "v":
            if gestor.volver() is None:
                print("Todavía no hay respuestas para revisar.", file=salida)
            continue
        if accion == "e":
            _editar_respuesta(gestor, entrada, salida)
            continue
        if accion == "c":
            if _confirmar_cambio(gestor, rutas, entrada, salida):
                ruta_anterior = None
            continue
        if accion == "f":
            return ConsultaCondicional(gestor.observaciones, gestor.estado_final)
        respuesta = RESPUESTAS.get(accion)
        if respuesta is None:
            print("Respuesta inválida; elige Sí, No o No estoy seguro.", file=salida)
            continue
        gestor.responder(pregunta.id, respuesta)


def _mostrar_diagnostico(diagnostico: DiagnosticoInferido, salida: TextIO) -> None:
    print(f"- {diagnostico.nombre} [{diagnostico.categoria}]", file=salida)
    print(f"  {diagnostico.descripcion}", file=salida)
    print("  Reglas y hechos observados:", file=salida)
    for regla in diagnostico.reglas:
        print(f"  * {regla.id}: {regla.explicacion}", file=salida)
        for condicion in regla.condiciones:
            print(f"    - {condicion.nombre}: {condicion.estado.value}", file=salida)
    print("  Recomendaciones:", file=salida)
    for recomendacion in diagnostico.recomendaciones:
        print(f"  * {recomendacion}", file=salida)


def mostrar_resultado(resultado: ResultadoInferencia, salida: TextIO) -> None:
    print("\n=== Resultado del Modelo A ===", file=salida)
    if resultado.principal is None:
        print("Sin diagnóstico concluyente.", file=salida)
        print(resultado.explicacion_sin_conclusion, file=salida)
        return
    diagnosticos = [resultado.principal, *resultado.alternativos]
    contexto_energia = None
    if (resultado.memoria.hechos.get("s_monitor_externo_funciona") == EstadoHecho.VERDADERO
            and any(d.id == "d_pantalla_principal" for d in diagnosticos)):
        contexto_energia = next(
            (d for d in diagnosticos if d.id == "d_revision_inicio_energia"), None
        )
        if contexto_energia is not None:
            diagnosticos.remove(contexto_energia)
    medicion_alta = resultado.memoria.hechos.get("s_temperatura_alta") == EstadoHecho.VERDADERO
    indice_medicion = next(
        (i for i, diagnostico in enumerate(diagnosticos) if diagnostico.id == "d_sobrecalentamiento"),
        None,
    )
    if medicion_alta and indice_medicion is not None and indice_medicion > 0:
        diagnosticos.insert(0, diagnosticos.pop(indice_medicion))
        print("Temperatura alta medida (se presenta primero por ser una observación directa):", file=salida)
    else:
        print("Hipótesis principal (ordenada por especificidad, no por probabilidad):", file=salida)
    _mostrar_diagnostico(diagnosticos[0], salida)
    if len(diagnosticos) > 1:
        print("\nOtras hipótesis compatibles:", file=salida)
        for diagnostico in diagnosticos[1:]:
            _mostrar_diagnostico(diagnostico, salida)
    if contexto_energia is not None:
        print("\nEvidencia complementaria de energía presente (integrada en la revisión de pantalla):", file=salida)
        for regla in contexto_energia.reglas:
            print(f"  * {regla.id}: {regla.explicacion}", file=salida)
            for condicion in regla.condiciones:
                print(f"    - {condicion.nombre}: {condicion.estado.value}", file=salida)
    print("\nEstas son hipótesis; confirme la causa con pruebas técnicas.", file=salida)


def _mostrar_traza_b(
    traza: TrazaInferencia, soportes: dict[str, list[TrazaInferencia]],
    salida: TextIO, sangria: str = "  ",
) -> None:
    print(f"{sangria}Nivel {traza.nivel} — {traza.regla_id}: {traza.explicacion}", file=salida)
    for condicion in traza.condiciones:
        respaldos = [
            soporte for soporte in soportes.get(condicion.hecho_id, [])
            if soporte.conclusion_estado == condicion.estado
        ]
        origen = "derivado" if respaldos else "observado"
        print(f"{sangria}  - {condicion.nombre} [{origen}]: {condicion.estado.value}", file=salida)
        for indice, respaldo in enumerate(respaldos, start=1):
            if len(respaldos) > 1:
                print(f"{sangria}    Soporte alternativo {indice}:", file=salida)
            _mostrar_traza_b(respaldo, soportes, salida, sangria + "    ")


def mostrar_resultado_b(resultado: ResultadoModeloB, salida: TextIO) -> None:
    print("\n=== Resultado del Modelo B ===", file=salida)
    unidad = "ronda" if resultado.rondas == 1 else "rondas"
    print(f"Punto fijo alcanzado tras {resultado.rondas} {unidad} con reglas activadas.", file=salida)
    soportes: dict[str, list[TrazaInferencia]] = {}
    por_regla = {}
    for traza in resultado.trazas:
        por_regla[traza.regla_id] = traza
        if traza.conclusion_tipo == "hecho":
            soportes.setdefault(traza.conclusion_id, []).append(traza)
    if soportes:
        print("Hechos derivados (no son respuestas del usuario):", file=salida)
        for hecho_id in sorted(soportes):
            traza = soportes[hecho_id][0]
            print(
                f"- {traza.conclusion_id}: {traza.conclusion_estado.value}; "
                f"respaldado por {', '.join(s.regla_id for s in soportes[hecho_id])}",
                file=salida,
            )
    if resultado.principal is None:
        print("Sin diagnóstico concluyente.", file=salida)
        print(resultado.explicacion_sin_conclusion, file=salida)
        return
    for indice, diagnostico in enumerate((resultado.principal, *resultado.alternativos)):
        titulo = "Hipótesis principal" if indice == 0 else "Hipótesis alternativa"
        print(f"\n{titulo}: {diagnostico.nombre} [{diagnostico.categoria}]", file=salida)
        print(diagnostico.descripcion, file=salida)
        print("Cadenas de inferencia y evidencias:", file=salida)
        for regla in diagnostico.reglas:
            _mostrar_traza_b(por_regla[regla.id], soportes, salida)
        print("Recomendaciones:", file=salida)
        for recomendacion in diagnostico.recomendaciones:
            print(f"  * {recomendacion}", file=salida)
    print("\nEstas son hipótesis; confirme la causa con pruebas técnicas.", file=salida)


def mostrar_resultado_c(resultado: ResultadoModeloC, salida: TextIO) -> None:
    print("\n=== Resultado del Modelo C ===", file=salida)
    unidad = "ronda" if resultado.rondas == 1 else "rondas"
    print(f"Cierre inferencial de B: {resultado.rondas} {unidad}; mismas reglas y hechos derivados.", file=salida)
    print("Precedencia: calidad máxima de observación original, número de observaciones originales distintas, prioridad técnica ordinal, ID estable.", file=salida)
    print("Estos criterios ordenan la revisión; no son probabilidades ni certeza diagnóstica.", file=salida)
    print("Observaciones originales confirmadas:", file=salida)
    for hecho_id, estado in sorted(resultado.observaciones_confirmadas.items()):
        print(f"- {hecho_id}: {estado.value}", file=salida)
    derivados: dict[str, list[str]] = {}
    por_regla = {}
    soportes: dict[str, list[TrazaInferencia]] = {}
    for traza in resultado.trazas:
        por_regla[traza.regla_id] = traza
        if traza.conclusion_tipo == "hecho":
            derivados.setdefault(traza.conclusion_id, []).append(traza.regla_id)
            soportes.setdefault(traza.conclusion_id, []).append(traza)
    print("Hechos derivados:", file=salida)
    for hecho_id, reglas in sorted(derivados.items()):
        print(f"- {hecho_id}: {resultado.memoria.hechos[hecho_id].value}; reglas {', '.join(reglas)}", file=salida)
    if resultado.principal is None:
        print("Sin diagnóstico concluyente.", file=salida)
        print(resultado.explicacion_sin_conclusion, file=salida)
        return
    print(f"Decisión: {resultado.explicacion_prioridad}", file=salida)
    for indice, (diagnostico, criterio) in enumerate(zip(
        (resultado.principal, *resultado.alternativos), resultado.criterios
    )):
        titulo = "Hipótesis principal" if indice == 0 else f"Hipótesis alternativa {indice}"
        print(f"\n{titulo}: {diagnostico.nombre} [{diagnostico.categoria}]", file=salida)
        print(diagnostico.descripcion, file=salida)
        print(
            f"Criterios: calidad {criterio.calidad} ({CALIDADES[criterio.calidad]}); "
            f"{criterio.especificidad} observaciones distintas; prioridad {criterio.prioridad} "
            f"({PRIORIDADES[criterio.prioridad]}); ID {diagnostico.id}.", file=salida,
        )
        print(f"Soporte original: {', '.join(criterio.observaciones)}", file=salida)
        if indice:
            anterior = resultado.criterios[indice - 1]
            print(f"Orden: {anterior.diagnostico_id} precede a {criterio.diagnostico_id} por {motivo_precedencia(anterior, criterio)}.", file=salida)
        print("Reglas activadas y cadenas:", file=salida)
        for regla in diagnostico.reglas:
            _mostrar_traza_b(por_regla[regla.id], soportes, salida)
        print("Recomendaciones:", file=salida)
        for recomendacion in diagnostico.recomendaciones:
            print(f"  * {recomendacion}", file=salida)
    print("\nEstas son hipótesis; confirme la causa con pruebas técnicas.", file=salida)


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnóstico simbólico básico de fallas en PC")
    parser.add_argument(
        "--respuestas", type=Path,
        help="Archivo JSON opcional con estados por ID de síntoma; omisiones = desconocido",
    )
    parser.add_argument(
        "--modelo", type=str.upper, choices=MODELOS, default=MODELO_PREDETERMINADO,
        help="Modelo de inferencia A, B o C (predeterminado: A)",
    )
    opciones = parser.parse_args(argumentos)
    raiz = Path(__file__).resolve().parents[2]
    try:
        modelo = seleccionar_modelo(opciones.modelo, raiz / "data" / "conocimiento")
        if opciones.respuestas is None:
            preguntas = cargar_preguntas(raiz / "data" / "interfaz" / "preguntas.json", modelo.sintomas)
            rutas = cargar_rutas(raiz / "data" / "interfaz" / "rutas.json", preguntas)
            consulta = preguntar_condicional(preguntas, rutas, sys.stdin, sys.stdout)
            if consulta.terminal == "@bloqueo_energia":
                print("\nNo hay diagnóstico de video con las señales observadas. "
                      "Elige alimentación en una consulta nueva si deseas investigarlo.", file=sys.stdout)
                return 0
            respuestas = consulta.observaciones
        else:
            with opciones.respuestas.open(encoding="utf-8") as archivo:
                respuestas = json.load(archivo)
            if not isinstance(respuestas, dict):
                raise ValueError("El archivo de respuestas debe contener un objeto JSON")
            conflictos = detectar_contradicciones(normalizar_observaciones(modelo.sintomas, respuestas))
            if conflictos:
                raise ValueError("Respuestas contradictorias: " + " ".join(c.explicacion for c in conflictos))
        resultado = modelo.evaluar(respuestas)
        if isinstance(resultado, ResultadoModeloC):
            mostrar_resultado_c(resultado, sys.stdout)
        elif isinstance(resultado, ResultadoModeloB):
            mostrar_resultado_b(resultado, sys.stdout)
        else:
            mostrar_resultado(resultado, sys.stdout)
    except (ErrorConocimiento, ErrorPreguntas, ErrorRutas, ValueError, OSError, UnicodeError, json.JSONDecodeError, EOFError) as error:
        print(f"No se pudo completar la consulta: {error}", file=sys.stderr)
        return 2
    return 0
