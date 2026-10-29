# Sistema experto de diagnóstico de fallas en PC

Proyecto universitario de IA simbólica. **Avance 1 finalizado; Avance 2 cerrado como versión académica `avance-2`.** El Modelo A obtiene hipótesis mediante reglas SI–ENTONCES. El Modelo B añade encadenamiento hacia adelante con hechos derivados y trazas. El Modelo C reutiliza B y ordena hipótesis mediante criterios simbólicos ordinales. Los tres modelos se compararon sobre 55 viñetas elegibles de desarrollo; C fue seleccionado y congelado por la utilidad y explicación de su orden de revisión. Los 20 casos finales siguen reservados. La comparación académica no mide precisión en equipos reales.

## Aplicación gráfica de la entrega final

La aplicación PySide6/Qt Quick usa internamente el Modelo C y presenta hipótesis, recomendaciones y razonamiento sin mostrar nombres de modelos ni una comparación académica. Incluye siete rutas de consulta, respuestas `verdadero`/`falso`/`desconocido`, edición de respuestas, alternativas ordenadas por criterios simbólicos y exportación de un reporte técnico PDF. En Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-gui.txt
.\.venv\Scripts\python.exe interfaz_grafica.py
```

Desde resultados, **Visualizar razonamiento** abre una pantalla adicional con el flujo de observaciones → reglas activadas → hechos derivados → hipótesis. Sus conexiones proceden de las trazas de C. Permite seleccionar nodos para consultar sus detalles, resaltar soportes, usar zoom y desplazamiento y regresar al resultado sin cambiar respuestas ni repetir la inferencia. Los hechos derivados aparecen solo cuando se activan las reglas que los producen; el panel de detalle no muestra contadores de reglas inactivas ni preguntas omitidas. La interfaz conserva el estilo blanco, lavanda y violeta, con tarjetas, mascotas y sonidos.

Como ejemplo reproducible de dos hechos derivados, elige **«El sistema operativo no inicia o presenta errores»** y responde, en orden: `No`, `No`, `Sí`, `No`, `Sí`, `No`, `No`. La secuencia corresponde a las preguntas `p16`, `p06`, `p26`, `p12`, `p10`, `p17` y `p11`; el «Sí» de `p10` indica que la unidad aparece en BIOS/UEFI. El resultado registra «Fallo situado en la etapa de arranque» y «Fallo de arranque con unidad visible en firmware». Es un recorrido de demostración, no una confirmación de avería física.

La consola conserva A como modelo predeterminado. La arquitectura, las pruebas y las limitaciones de la aplicación gráfica se describen en [la documentación de la entrega final](docs/ENTREGA_FINAL_INTERFAZ.md). El visualizador está publicado en `main`; la revisión visual final y el empaquetado ejecutable siguen pendientes.

## Probar el cuestionario

La consola requiere Python 3.11 o posterior y no tiene paquetes externos. Desde la raíz del proyecto:

```powershell
python diagnosticar.py
```

El selector acepta `--modelo A`, `--modelo B` y `--modelo C`; A es el predeterminado. Para ver una cadena multinivel reproducible:

```powershell
python diagnosticar.py --modelo B --respuestas ejemplos/arranque_multinivel_b.json
```

Para comparar un conflicto real de dos hipótesis, ejecuta:

```powershell
python diagnosticar.py --modelo B --respuestas ejemplos/hipotesis_termicas_c.json
python diagnosticar.py --modelo C --respuestas ejemplos/hipotesis_termicas_c.json
```

B presenta primero los indicios térmicos por su desempate de especificidad e ID. C presenta primero la temperatura alta medida porque la clasifica como prueba técnica específica; conserva los indicios como alternativa. C ordena por calidad máxima de evidencia original, número de observaciones originales distintas, prioridad técnica ordinal e ID estable. No suma hechos derivados ni cadenas repetidas como observaciones adicionales. La prioridad de revisión no es probabilidad ni certeza sobre una pieza. La explicación completa y las limitaciones están en `docs/AVANCE_2.md`.

Elige uno de los siete problemas. Cada ruta comienza con una pregunta relacionada con esa elección. La categoría permanece fija; cuando una respuesta impide seguir, la consola lo explica y ofrece iniciar otra consulta. Cambiar de categoría requiere confirmación y descarta las respuestas anteriores.

Responde con **1. Sí**, **2. No**, **3. No estoy seguro** o con `s/n/?`. Enter también equivale a «No estoy seguro» mientras se pregunta. Usa `v` para volver, `e` para editar una respuesta anterior, `c` para solicitar un cambio de categoría y `f` para finalizar con la evidencia disponible. Editar una respuesta descarta las posteriores porque el camino puede cambiar. Al terminar una ruta, Enter muestra el resultado disponible. Si video queda bloqueado por ausencia de señales de energía, se ofrece iniciar alimentación y no se presenta automáticamente un diagnóstico de otra ruta.

Una comprobación técnica que no realizaste puede contestarse «No estoy seguro». Esto registra `desconocido`, nunca `falso`. Las conclusiones son hipótesis o áreas de revisión; no identifican automáticamente una pieza averiada. El orden usual por especificidad de reglas no expresa probabilidad. Si hay temperatura alta medida, la consola presenta ese hallazgo antes que los indicios subjetivos.

La ruta de video diferencia un logotipo breve de imagen que permanece. En conectividad puedes indicar cortes intermitentes o una página concreta que falla aunque la página de prueba abra. En sistema puedes registrar un error ocurrido durante el uso; si no hay observaciones para identificar su causa, el resultado lo dirá explícitamente.

## Validación y ejemplos

```powershell
python validar_conocimiento.py
python verificar_seleccion.py
python verificar_gui_razonamiento.py
python -m unittest discover -s auditoria -v
python diagnosticar.py --respuestas ejemplos/ram.json
python diagnosticar.py --respuestas ejemplos/sin_conclusion.json
```

`--respuestas` acepta un objeto JSON con IDs de hechos y estados internos `verdadero`, `falso` o `desconocido`; los omitidos quedan desconocidos. Los antiguos hechos compuestos `s_no_enciende`, `s_lentitud_o_congelamientos` y `s_proceso_consumo_alto` se retiraron: el programa indica los IDs separados que deben registrarse. No los convierte automáticamente, porque una respuesta compuesta no determina las dos observaciones individuales.

`validar_casos.py` comprueba estructura y huella sin ejecutar A, B ni C, pero **lee el archivo final reservado**. También lo hace `tests/test_validacion_casos.py`, incluido en la batería global `unittest discover -s tests`. No ejecutar esos dos recorridos mientras esté vigente la restricción de no abrir la reserva. Los 60 casos de desarrollo están en `data/evaluacion/casos_desarrollo.json`; el archivo local `data/evaluacion/casos_finales_reservados.json` debe permanecer fuera de GitHub. El [protocolo](docs/PROTOCOLO_EVALUACION_AVANCE_2.md) define métricas y exclusiones antes de experimentar; la distribución y sus límites se resumen en [Avance 2](docs/AVANCE_2.md). La reserva final no se usa para ajustar reglas ni seleccionar modelos.

La última verificación de la interfaz ampliada pasó **94 pruebas funcionales seguras**, **10 auditorías**, la validación de conocimiento, las **44 huellas protegidas** de selección y las **113 huellas** del manifiesto actual de la GUI. La prueba Qt cubrió el visualizador a 760×600, 1080×760 y 1440×900, sin avisos `polish() loop`. `data/interfaz/MANIFIESTO_GUI.json` conserva las 109 huellas del respaldo `pre-finalizacion`; el manifiesto nuevo `data/interfaz/MANIFIESTO_GUI_RAZONAMIENTO.json` verifica la GUI ampliada. La batería global y `validar_casos.py` siguen pendientes por la reserva final.

La [revisión metodológica 4.1](docs/REVISION_CASOS_ETAPA_4_1.md) documenta la versión anterior y la corrección de los 60 casos de desarrollo. Esa revisión validó solo desarrollo; el validador global anterior carga también la reserva y no se utilizó para esta corrección.

## Organización

- `data/conocimiento/`: 36 hechos, 18 diagnósticos y 42 reglas JSON.
- `data/interfaz/preguntas.json`: 36 preguntas, ayudas y polaridad visible.
- `data/interfaz/rutas.json`: grafo declarativo de siete categorías y tres transiciones por nodo.
- `src/diagnostico_pc/gestor_preguntas.py`: sesión, historial, retroceso y cambio explícito; no infiere diagnósticos.
- `src/diagnostico_pc/modelo_a.py`: motor de inferencia directa del Avance 1.
- `src/diagnostico_pc/contratos.py` y `selector.py`: contrato común y selección de A/B/C.
- `data/conocimiento_avance2/`: dos hechos derivados y cuatro reglas adicionales, separados del conocimiento original.
- `src/diagnostico_pc/conocimiento_b.py` y `modelo_b.py`: validación de la ampliación y encadenamiento multinivel.
- `data/conocimiento_avance2/criterios_c.json`, `conocimiento_c.py` y `modelo_c.py`: metadatos validados y orden simbólico posterior al cierre de B.
- `docs/PREGUNTAS.md` y `docs/BASE_CONOCIMIENTOS.md`: adquisición dinámica y representación de conocimiento, respectivamente.
- `docs/AVANCE_1.md`, `docs/AVANCE_2.md` y `CHECKLIST.md`: estado y resultados observados.
- `docs/PROTOCOLO_EVALUACION_AVANCE_2.md` y `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md`: protocolo previo y medición de desarrollo; `docs/REVISION_CASOS_ETAPA_4_1.md` conserva la revisión histórica protegida por huellas.
- `data/evaluacion/`, `evaluar_desarrollo.py` y `verificar_seleccion.py`: datos de desarrollo, resultados congelados, reproducción y comprobación de la selección.
- `src/diagnostico_pc/gui/`: sesión, puente Qt, serialización, reporte PDF y transformación de trazas en grafo; `qml/` contiene la interfaz y el visualizador.
- `verificar_gui_razonamiento.py` y `data/interfaz/MANIFIESTO_GUI_RAZONAMIENTO.json`: verificación SHA-256 de la GUI ampliada, separada del respaldo histórico.

**Verificación histórica del cierre del Avance 1:** `python validar_conocimiento.py` confirmó 36 hechos, 36 preguntas, 42 reglas, 18 diagnósticos y siete rutas. Pasaron 35 pruebas habituales y 10 de auditoría; ambos ejemplos JSON terminaron correctamente. La auditoría encontró testigos interactivos para 42/42 reglas y 18/18 diagnósticos. El tag anotado `avance-1` identifica esa versión. Los resultados posteriores de B y C, la evaluación de desarrollo y la selección de C constan en [Avance 2](docs/AVANCE_2.md).
