# Sistema experto de diagnóstico de fallas en PC

Proyecto universitario de IA simbólica desarrollado por fases. **Estado actual: Fase 2 terminada; el sistema aún no ejecuta diagnósticos.** La base de conocimientos y su validador están disponibles; el motor de inferencia y el Modelo A corresponden a la Fase 3.

## Requisitos y comprobación

- Python 3.11 o posterior. Esta fase se verificó con Python 3.14.2 en Windows.
- Git para control de versiones. La Fase 2 no necesita paquetes externos.

Desde la raíz del proyecto:

```powershell
python validar_conocimiento.py
python -m unittest discover -s tests -v
```

La documentación del catálogo y su formato está en [docs/BASE_CONOCIMIENTOS.md](docs/BASE_CONOCIMIENTOS.md). El progreso y las evidencias están en [CHECKLIST.md](CHECKLIST.md).

## Organización

- `data/conocimiento/`: definiciones JSON de hechos, diagnósticos y reglas.
- `src/diagnostico_pc/hechos.py`: estados trivalentes y normalización de observaciones.
- `src/diagnostico_pc/validacion.py`: validador estático del conocimiento.
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

Cada versión documentará sus requisitos y forma de ejecución. Actualmente no existe ningún tag de entrega.
