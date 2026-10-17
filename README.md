# Sistema experto de diagnóstico de fallas en PC

Proyecto universitario de IA simbólica desarrollado por fases. **Estado actual: Fase 3 terminada; Avance 1 pendiente de validación y cierre.** El Modelo A realiza diagnósticos directos por reglas de producción y explica sus conclusiones. Los modelos B y C aún no existen.

## Requisitos y comprobación

- Python 3.11 o posterior. El Avance 1 se verificó con Python 3.14.2 en Windows.
- Git para control de versiones. El Avance 1 no necesita paquetes externos.

Desde la raíz del proyecto:

```powershell
python validar_conocimiento.py
python -m unittest discover -s tests -v
python diagnosticar.py
```

La consulta interactiva muestra [20 preguntas en lenguaje cotidiano](docs/PREGUNTAS.md), cada una con una ayuda breve. Responde `1`/`Sí`, `2`/`No` o `3`/`No estoy seguro`; Enter también significa No estoy seguro. La respuesta se traduce al estado interno según la polaridad de cada pregunta: **Sí no siempre significa `verdadero`**. Para repetir dos demostraciones desde archivos JSON:

```powershell
python diagnosticar.py --respuestas ejemplos/ram.json
python diagnosticar.py --respuestas ejemplos/sin_conclusion.json
```

Un archivo de respuestas es un objeto JSON con IDs de síntomas y valores **internos** `verdadero`, `falso` o `desconocido`; los síntomas omitidos quedan desconocidos. Este formato técnico sigue igual para las pruebas y futuras comparaciones. El programa muestra hipótesis, reglas activadas, hechos verificados y recomendaciones. El diagnóstico principal se ordena por la mayor cantidad de condiciones de una regla activada; en empates, por ID de diagnóstico. Ese orden no representa probabilidad ni certeza.

La documentación del catálogo está en [docs/BASE_CONOCIMIENTOS.md](docs/BASE_CONOCIMIENTOS.md), el informe académico en [docs/AVANCE_1.md](docs/AVANCE_1.md) y las evidencias de fase en [CHECKLIST.md](CHECKLIST.md).

## Organización

- `data/conocimiento/`: definiciones JSON de hechos, diagnósticos y reglas.
- `data/interfaz/preguntas.json`: texto, ayuda y polaridad de las 20 preguntas visibles.
- `src/diagnostico_pc/hechos.py`: estados trivalentes y normalización de observaciones.
- `src/diagnostico_pc/validacion.py`: validador estático del conocimiento.
- `src/diagnostico_pc/preguntas.py`: validación y mapeo de respuestas visibles, reutilizables en otras interfaces.
- `src/diagnostico_pc/modelo_a.py`: memoria de trabajo, recorrido de reglas directas y resultados explicables.
- `src/diagnostico_pc/consola.py` y `diagnosticar.py`: consulta de texto interactiva o mediante archivo.
- `ejemplos/`: dos respuestas pequeñas para demostrar una hipótesis y una consulta sin conclusión.
- `tests/`: pruebas automáticas de integridad y estados.
- `docs/`: documentación académica por fase y, más adelante, por entrega.

## Versiones de las entregas

Los tags `avance-1`, `avance-2` y `entrega-final` se crearán únicamente al cerrar cada entrega con autorización expresa. Antes de cambiar de versión, ejecutar `git status --short` y conservar cualquier cambio local. Cuando los tags existan:

```powershell
git switch --detach avance-1
git switch --detach avance-2
git switch --detach entrega-final
git switch main
```

Cada versión documentará sus requisitos y forma de ejecución. Actualmente no existe ningún tag de entrega: el Avance 1 debe revisarse y autorizarse para su cierre.
