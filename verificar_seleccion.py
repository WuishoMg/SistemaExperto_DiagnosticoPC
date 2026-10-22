"""Comprueba la selección congelada sin acceder a los casos finales reservados."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent
MANIFIESTO = Path("data/evaluacion/MANIFIESTO_SELECCION.json")

# Lista cerrada: no contiene la reserva final ni acepta rutas proporcionadas por el JSON.
ARCHIVOS_CONGELADOS = (
    "data/conocimiento/diagnosticos.json",
    "data/conocimiento/hechos.json",
    "data/conocimiento/reglas.json",
    "data/conocimiento_avance2/criterios_c.json",
    "data/conocimiento_avance2/hechos.json",
    "data/conocimiento_avance2/reglas.json",
    "data/evaluacion/casos_desarrollo.json",
    "data/evaluacion/fuentes.json",
    "data/evaluacion/historico/casos_desarrollo_etapa4_v1.json",
    "data/interfaz/preguntas.json",
    "data/interfaz/rutas.json",
    "docs/PROTOCOLO_EVALUACION_AVANCE_2.md",
    "docs/REVISION_CASOS_ETAPA_4_1.md",
    "evaluar_desarrollo.py",
    "src/diagnostico_pc/conocimiento_b.py",
    "src/diagnostico_pc/conocimiento_c.py",
    "src/diagnostico_pc/gestor_preguntas.py",
    "src/diagnostico_pc/hechos.py",
    "src/diagnostico_pc/modelo_a.py",
    "src/diagnostico_pc/modelo_b.py",
    "src/diagnostico_pc/modelo_c.py",
    "src/diagnostico_pc/preguntas.py",
    "src/diagnostico_pc/rutas.py",
    "src/diagnostico_pc/selector.py",
    "src/diagnostico_pc/validacion.py",
    "validar_casos.py",
    "src/diagnostico_pc/contratos.py",
    "src/diagnostico_pc/consola.py",
    "diagnosticar.py",
    "docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md",
    "data/evaluacion/resultados_etapa5/proveniencia.json",
    "data/evaluacion/resultados_etapa5/predicciones_brutas.json",
    "data/evaluacion/resultados_etapa5/metricas.json",
    "data/evaluacion/resultados_etapa5/matrices.json",
    "data/evaluacion/resultados_etapa5/distribuciones.json",
    "data/evaluacion/resultados_etapa5/comparaciones.json",
    "data/evaluacion/resultados_etapa5/advertencias.json",
    "data/evaluacion/resultados_etapa5/errores.json",
    "data/evaluacion/resultados_etapa5/graficas/principal.svg",
    "data/evaluacion/resultados_etapa5/graficas/metricas.svg",
    "data/evaluacion/resultados_etapa5/graficas/matrices_A.svg",
    "data/evaluacion/resultados_etapa5/graficas/matrices_B.svg",
    "data/evaluacion/resultados_etapa5/graficas/matrices_C.svg",
    "verificar_seleccion.py",
)


class ErrorSeleccion(ValueError):
    """El manifiesto o una versión congelada no coincide."""


def sha256(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(65536), b""):
            digest.update(bloque)
    return digest.hexdigest()


def verificar(datos: dict | None = None, raiz: Path = RAIZ) -> int:
    """Verifica únicamente los archivos de la lista cerrada y la procedencia de etapa 5."""
    if datos is None:
        datos = json.loads((raiz / MANIFIESTO).read_text(encoding="utf-8"))
    if datos.get("version") != 1 or datos.get("id_version") != "avance2-etapa6-seleccion-v1":
        raise ErrorSeleccion("Versión del manifiesto de selección inesperada")
    if (datos.get("modelo_seleccionado") != "C"
            or datos.get("modelo_predeterminado_actual") != "A"
            or datos.get("modelo_predeterminado_aplicacion_final") != "C"):
        raise ErrorSeleccion("Selección o predeterminado inesperado")
    if (datos.get("algoritmo") != "SHA-256"
            or datos.get("procedencia_etapa5") != "data/evaluacion/resultados_etapa5/proveniencia.json"
            or datos.get("casos_desarrollo_elegibles") != 55
            or datos.get("casos_desarrollo_excluidos") != 5):
        raise ErrorSeleccion("Procedencia o alcance de desarrollo inesperado")
    archivos = datos.get("archivos")
    if not isinstance(archivos, dict) or set(archivos) != set(ARCHIVOS_CONGELADOS):
        raise ErrorSeleccion("La lista de archivos congelados es distinta")
    for nombre in ARCHIVOS_CONGELADOS:
        esperado = archivos[nombre]
        if not isinstance(esperado, str) or len(esperado) != 64:
            raise ErrorSeleccion(f"Huella no válida: {nombre}")
        if sha256(raiz / nombre) != esperado:
            raise ErrorSeleccion(f"Huella distinta: {nombre}")
    procedencia = json.loads(
        (raiz / "data/evaluacion/resultados_etapa5/proveniencia.json").read_text(encoding="utf-8")
    )
    if datos.get("git_head_base") != procedencia["git_head"]:
        raise ErrorSeleccion("Git HEAD base distinto de la Etapa 5")
    if any(archivos.get(nombre) != huella for nombre, huella in procedencia["huellas"].items()):
        raise ErrorSeleccion("Una huella difiere de la procedencia de Etapa 5")
    if archivos["data/evaluacion/resultados_etapa5/predicciones_brutas.json"] != procedencia["predicciones_sha256"]:
        raise ErrorSeleccion("La captura difiere de la procedencia de Etapa 5")
    return len(ARCHIVOS_CONGELADOS)


def main() -> int:
    try:
        cantidad = verificar()
    except (ErrorSeleccion, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Selección no verificada: {exc}", file=sys.stderr)
        return 1
    print(f"Selección C verificada: {cantidad} archivos coinciden; A continúa predeterminado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
