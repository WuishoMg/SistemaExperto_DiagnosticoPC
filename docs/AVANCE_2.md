# Avance 2 — Modelos simbólicos de diagnóstico

**Estado al 22 de octubre de 2026:** Avance 2 cerrado por autorización expresa del usuario como versión académica `avance-2`. Los modelos A, B y C están implementados y evaluados en desarrollo; C queda seleccionado para la futura aplicación gráfica. La evaluación final permanece reservada.

Las secciones de etapas anteriores registran el estado **en aquel momento**; sus frases sobre trabajo futuro no sustituyen este estado vigente. `AVANCE_1.md` documenta A, `BASE_CONOCIMIENTOS.md` la representación simbólica, `PREGUNTAS.md` la adquisición dinámica, el protocolo conserva las decisiones anteriores al experimento y el informe de resultados conserva la medición de la etapa 5. La revisión 4.1 permanece como registro histórico separado porque su ruta y huella forman parte de la selección congelada.

## Objetivo y alcance

El Avance 2 prepara el desarrollo y la comparación reproducible de tres modelos de razonamiento simbólico sobre el mismo problema de diagnóstico de PC. El Modelo A es la inferencia directa SI–ENTONCES del Avance 1. El Modelo B implementa encadenamiento hacia adelante multinivel con hechos derivados. El Modelo C reutiliza ese cierre y resuelve conflictos de orden mediante criterios simbólicos explícitos. No se usan redes neuronales ni aprendizaje automático para estos motores.

La etapa 1 preparó el contrato de inferencia, el selector y la integración de A. La etapa 2 incorporó B. La etapa 3 incorpora C sin cambiar los catálogos originales, las reglas de B, las preguntas, las rutas ni la inferencia de A/B.

## Arquitectura registrada en la etapa 1

| Responsabilidad | Archivo | Estado |
| --- | --- | --- |
| Conocimiento declarativo | `data/conocimiento/{hechos,reglas,diagnosticos}.json` | Conservado de Avance 1. |
| Hechos trivalentes | `src/diagnostico_pc/hechos.py` | Conserva `verdadero`, `falso` y `desconocido`; una omisión es desconocida. |
| Cuestionario y siete rutas | `data/interfaz/`, `preguntas.py`, `rutas.py`, `gestor_preguntas.py` | Recogen y normalizan observaciones sin inferir diagnósticos. |
| Contrato de inferencia y resultado | `src/diagnostico_pc/contratos.py` | Protocolos estructurales `ModeloInferencia` y `ResultadoInferencia`. |
| Selector | `src/diagnostico_pc/selector.py` | Construye A, B o C; A sigue predeterminado. |
| Modelo A | `src/diagnostico_pc/modelo_a.py` | Sin cambios; satisface el contrato con su API y su resultado existentes. |
| Presentación | `src/diagnostico_pc/consola.py` | Acepta `--modelo`; A es predeterminado y conserva la salida previa. |
| Evaluación diagnóstica | Pendiente **en la etapa 1** | En etapas posteriores se prepararon las viñetas y se evaluó solo desarrollo. |

El contrato exige `sintomas`, `evaluar(respuestas)` y un resultado con memoria de hechos, hipótesis principal, alternativas y explicación cuando no hay conclusión. `ResultadoModeloA` ya cumple esa estructura; no se transforman sus diagnósticos, reglas, recomendaciones ni explicaciones. La consola mantiene la presentación vigente de A, incluidas las decisiones de contexto documentadas en el Avance 1. El contrato es estructural: la comprobación en tiempo de ejecución verifica presencia de miembros, y las pruebas verifican sus valores.

En la etapa 1, `python diagnosticar.py` y `python diagnosticar.py --modelo A` usaban el mismo motor; B y C terminaban con un mensaje de no implementado. B se habilitó en la etapa 2 y C en la etapa 3. Los tres comparten el cuestionario existente.

## Etapa 2: encadenamiento multinivel del Modelo B

La base original contiene reglas que llevan directamente de síntomas observados a diagnósticos. B permite además que una regla concluya un **hecho derivado**, que otra regla lo use como condición y que una regla posterior llegue a un diagnóstico. Un hecho derivado es una conclusión intermedia de reglas; la consola lo distingue explícitamente de las respuestas del usuario.

La ampliación vive en `data/conocimiento_avance2/` y contiene **2 hechos derivados y 4 reglas nuevas**. Usa los mismos 36 síntomas observables, los 18 diagnósticos existentes y las 42 reglas originales. No añade causas ni diagnósticos. Los dos hechos intermedios son:

1. `h_fallo_etapa_arranque`: la evidencia sitúa el problema en la etapa de arranque, sin identificar todavía la causa. Puede respaldarse por un inicio no utilizable después del POST o por un mensaje del firmware sobre dispositivo de arranque ausente.
2. `h_fallo_arranque_unidad_visible`: además del patrón anterior, se comprobó que la unidad aparece en BIOS/UEFI (`s_unidad_no_detectada=falso`). Esto orienta a revisar configuración o archivos de arranque, sin confirmar una avería física.

`r_b_arranque_tras_post` y `r_b_mensaje_arranque` son soportes alternativos del primer hecho. `r_b_arranque_unidad_visible` exige ese hecho y la comprobación explícita de la unidad. `r_b_revision_arranque` lleva al diagnóstico ya existente `d_arranque_so`. Las reglas originales continúan activándose en B, por lo que pueden aportar soportes directos adicionales para el mismo diagnóstico. Los soportes se enumeran como justificaciones simbólicas, nunca como probabilidades independientes.

El motor evalúa por rondas. Cada ronda lee los estados obtenidos hasta ese momento; las conclusiones nuevas habilitan reglas en la ronda siguiente. Se detiene cuando ninguna regla pendiente tiene todas sus condiciones satisfechas: ese es el **punto fijo**. Cada regla se activa a lo sumo una vez. La validación rechaza ciclos entre hechos derivados; si dos reglas aplicables proponen estados opuestos para el mismo hecho, la evaluación se detiene con un error de contradicción en lugar de elegir uno arbitrariamente. La omisión y «No estoy seguro» permanecen `desconocido`, de modo que nunca satisfacen una condición `falso`.

`ResultadoModeloB` conserva los campos del contrato común (`memoria`, `principal`, `alternativos`, `explicacion_sin_conclusion`) y añade trazas con ID de regla, condiciones, conclusión y nivel, además del número de rondas y las observaciones confirmadas. La consola recorre las trazas desde cada regla diagnóstica hasta los hechos observados y muestra cada soporte alternativo de un hecho derivado. Las recomendaciones provienen del diagnóstico original. La presentación de A conserva su texto previo.

### Recorrido reproducible

Ejecutar `python diagnosticar.py --modelo B --respuestas ejemplos/arranque_multinivel_b.json`. El ejemplo técnico aporta `s_so_no_inicia=verdadero`, `s_post_completado=verdadero`, `s_sin_dispositivo_arranque=verdadero` y `s_unidad_no_detectada=falso`. La salida observada llegó al punto fijo tras **3 rondas**:

```text
Observaciones: sistema no utilizable, POST completado, mensaje de dispositivo ausente, unidad sí visible
  → nivel 1: r_b_arranque_tras_post y r_b_mensaje_arranque
  → h_fallo_etapa_arranque=verdadero (dos soportes)
  → nivel 2: r_b_arranque_unidad_visible
  → h_fallo_arranque_unidad_visible=verdadero
  → nivel 3: r_b_revision_arranque
  → d_arranque_so: posible problema de configuración o archivos de arranque
```

En el mismo recorrido también se activaron `r_so_no_inicia_unidad_presente` y `r_so_mensaje_unidad_presente` del catálogo original. La hipótesis se muestra con sus tres reglas diagnósticas y las cadenas de evidencia; no se presenta como confirmación de la causa. Si la detección de la unidad queda desconocida, el segundo hecho derivado y la regla diagnóstica nueva no se activan.

### Diferencia actual entre A y B

| Aspecto | A | B |
| --- | --- | --- |
| Conocimiento usado | 36 hechos observables, 42 reglas directas, 18 diagnósticos. | La misma base más 2 hechos derivados y 4 reglas. |
| Recorrido | Una pasada de reglas directas. | Rondas hasta punto fijo; admite cadenas de hechos derivados. |
| Explicación | Reglas diagnósticas y observaciones directas. | Trazas por nivel, observaciones, hechos derivados y soportes alternativos. |
| Selección | Predeterminado; `--modelo A`. | `--modelo B` explícito. |

La diferencia de arquitectura está demostrada en pruebas funcionales. Todavía no se ha medido cuál modelo diagnostica mejor: no existen las 80 viñetas ni una comparación experimental.

## Etapa 3: resolución simbólica de conflictos del Modelo C

C llama una sola vez a `ModeloB.evaluar`. Conserva exactamente su memoria trivalente, las reglas activadas, las trazas y el conjunto de hipótesis; cambia únicamente cuál se presenta como principal y el orden de alternativas. Los metadatos están en `data/conocimiento_avance2/criterios_c.json`, aparte de los tres catálogos originales y de las cuatro reglas de B. El validador exige cobertura exacta de las 36 observaciones originales y los 18 diagnósticos, niveles válidos, IDs únicos y justificación por entrada.

La precedencia es lexicográfica:

1. **Calidad máxima del soporte original:** 3 = prueba técnica específica (medición, diagnóstico de firmware o comparación técnica); 2 = observación directa; 1 = indicio perceptivo sin medición. Se usa el nivel más alto entre los hechos originales que efectivamente respaldan la hipótesis, no el número de reglas ni una suma de supuestas evidencias independientes.
2. **Especificidad:** cantidad de IDs de observaciones originales *distintas* en todas las cadenas activadas que respaldan esa hipótesis. Las cadenas alternativas pueden compartir observaciones: cada ID se cuenta una sola vez. Los hechos derivados no se cuentan como respuestas nuevas.
3. **Prioridad técnica ordinal:** 2 = revisar temprano por temperatura medida o riesgo de almacenamiento/datos; 1 = revisión habitual. Solo resuelve empates en calidad y especificidad. Es una prioridad de revisión, no una estimación de avería.
4. **ID estable ascendente:** resuelve el empate total de manera reproducible.

Las trazas de B permiten recorrer cada regla diagnóstica hacia sus observaciones originales por los soportes de hechos derivados. C muestra observaciones confirmadas, hechos derivados, reglas y cadenas, hipótesis compatibles, valores ordinales y el criterio que separa cada par consecutivo. La prioridad técnica se documenta por diagnóstico y la calidad por observación. Todos los valores son ordinales: no expresan probabilidad, confianza calibrada ni aprendizaje automático. La hipótesis principal orienta la siguiente revisión y no confirma una pieza dañada.

### Ejemplo diagnóstico reproducible con dos hipótesis

Ejecutar con B y C `python diagnosticar.py --modelo B --respuestas ejemplos/hipotesis_termicas_c.json` y `python diagnosticar.py --modelo C --respuestas ejemplos/hipotesis_termicas_c.json`. El archivo registra temperatura alta medida, calor percibido, ventilador ruidoso y apagado bajo carga. Ambas ejecuciones activan las mismas cinco reglas diagnósticas y las hipótesis `d_indicios_termicos` y `d_sobrecalentamiento`; ninguna requiere hechos derivados. B pone primero los indicios porque ambas hipótesis alcanzan especificidad 2 por regla y su desempate por ID favorece `d_indicios_termicos`. C pone primero `d_sobrecalentamiento` porque su soporte incluye una medición de nivel 3 y el de los indicios alcanza nivel 2. Ambas tienen tres observaciones originales distintas en sus soportes. La alternativa queda visible. Es un ejemplo funcional plausible, no un caso de medición de calidad diagnóstica.

En `ejemplos/arranque_multinivel_b.json`, B y C conservan la misma hipótesis principal `d_arranque_so`. C reúne cuatro observaciones originales distintas pese a las cadenas repetidas y los dos hechos derivados; la coincidencia con B es válida porque solo hay una hipótesis compatible en ese recorrido.

### Verificación observada y límites de etapa 3

- `python validar_conocimiento.py`: código 0; 36 hechos originales, 18 diagnósticos, 42 reglas originales, 2 hechos derivados y 4 reglas de B; metadatos C completos para 36 observaciones y 18 diagnósticos.
- `python -m unittest discover -s tests -v`: **60 pruebas, 0 fallos**. Incluyen equivalencia B/C de hechos, reglas activadas, trazas e hipótesis; orden por criterios, desempates sintéticos deterministas, soportes únicos, desconocidos, alternativas, explicación, validación de metadatos, ciclos y contradicciones. Las pruebas anteriores de A y B siguen pasando.
- `python -m unittest discover -s auditoria -v`: **10 pruebas, 0 fallos**; auditoría de la base y rutas del Avance 1.
- Los ejemplos `ram.json`, `sin_conclusion.json` y `arranque_multinivel_b.json` se verificaron con A/B según su alcance anterior; la comparación térmica se ejecutó con B y C y el arranque multinivel con C. La salida de A predeterminado y A explícito se conserva en las regresiones. Los hashes SHA-256 de salida de A para `ram.json` y `sin_conclusion.json` coinciden con los documentados en la etapa 1: `df92584d199cacb77d8551aa16d9979636eb676b065a62d540cd9ab29e866130` y `42b840266ef58326b33849e7dc2a6cf8b8aeed54882a5988e994e369c4dd01ec`.

El criterio de calidad máxima simplifica una situación con varias observaciones heterogéneas; no evalúa fiabilidad individual ni dependencia causal. La suma de observaciones distintas solo representa amplitud descriptiva y puede favorecer hipótesis con más condiciones compatibles. La prioridad técnica es una decisión de revisión declarada. **Al cierre de la etapa 3** todavía no había viñetas ni evaluación de calidad diagnóstica, métricas o modelo seleccionado. La etapa 4 posterior preparó los casos sin evaluarlos.

## Plan experimental registrado en la etapa 3

La etapa 3 previó **80 viñetas académicas**: 60 para desarrollo y comparación y 20 independientes reservadas para la entrega final. Entonces no se creó ni ejecutó ningún caso. Los 20 finales solo podrán evaluarse una vez después de seleccionar y congelar el modelo; no se usarán para ajustar reglas ni seleccionar modelos. Los casos finales de un intento anterior ya estaban expuestos y no se reutilizan como evaluación inédita.

Las viñetas deberán representar situaciones técnicas plausibles de dificultad variable, información incompleta y desconocida, síntomas compartidos, hipótesis múltiples y situaciones fuera del conocimiento disponible. Las etiquetas se justificarán con criterios independientes de las predicciones. Se revisarán duplicados semánticos, traducciones directas de condiciones de reglas y filtraciones entre desarrollo y reserva final.

La comparación futura informará, como mínimo, accuracy de conjunto exacto de diagnósticos, precision, recall y F1, acierto del diagnóstico principal y comportamiento ante evidencia insuficiente. Deberá definir por anticipado cómo puntuar conjuntos vacíos, hipótesis múltiples y casos fuera de alcance, y conservar datos, versiones y resultados para reproducción. Estas métricas de calidad diagnóstica son distintas de las pruebas funcionales del software realizadas ahora. Las prioridades simbólicas de reglas no son probabilidades.

La docente mencionó como referencia resultados aproximados entre 80 % y 95–97 %, pero ese intervalo no es una meta. No se alterarán casos, etiquetas, predicciones ni reglas para alcanzarlo. Si el rendimiento resulta demasiado alto, se revisarán dificultad, independencia, duplicaciones y filtraciones, conservando los resultados originales.

## Estado por etapa

| Etapa | Estado |
| --- | --- |
| 1. Arquitectura y adaptación de A | Aprobada por el usuario. |
| 2. Modelo B | Aprobada por el usuario. |
| 3. Modelo C | Aprobada por el usuario. |
| 4. Casos y protocolo experimental | Aprobada con observaciones antes de evaluar. |
| 4.1. Corrección de desarrollo | Aprobada antes de evaluar. |
| 5. Evaluación experimental de desarrollo | Completada y revisada por el usuario al autorizar la etapa 6. |
| 6. Selección y cierre técnico | C seleccionado y congelado localmente; pendiente de revisión y autorización de cierre. |
| Evaluación final con 20 casos reservados | Reservada para la entrega final, después de congelar el modelo. |

## Etapa 4: diseño y validación de casos experimentales

Se prepararon **60 viñetas académicas de desarrollo** y **20 viñetas nuevas de reserva final** en archivos distintos bajo `data/evaluacion/`. Los 20 casos finales de un intento anterior se consideran expuestos y no se reutilizaron. Las viñetas describen situaciones hipotéticas; ninguna etiqueta afirma una pieza averiada en un equipo real. Cada registro incluye ruta, relato, respuestas trivalentes alcanzables por el cuestionario, trayecto de preguntas, hipótesis defendibles (incluido conjunto vacío), prioridad de revisión cuando hay varias hipótesis y una justificación técnica, evidencia, información faltante, comprobaciones y fuentes. El etiquetado se basó en el relato, observaciones y documentación técnica, sin obtener predicciones de A, B o C.

El protocolo previo a la medición está en `docs/PROTOCOLO_EVALUACION_AVANCE_2.md`; define conjunto exacto, métricas micro multietiqueta, matrices por diagnóstico, principal, orden, abstención y casos vacíos/múltiples. Exige comparar B y C con el mismo conjunto de hipótesis porque C solo reordena. Las pruebas funcionales siguen separadas de la calidad diagnóstica. La distribución preparada en la etapa 4 se conserva aquí como dato de diseño, anterior a la revisión de desarrollo 4.1:

| Ruta | Desarrollo | Final reservado | Total |
| --- | ---: | ---: | ---: |
| Alimentación | 6 | 2 | 8 |
| Lentitud | 10 | 3 | 13 |
| Video | 10 | 3 | 13 |
| Sistema | 10 | 3 | 13 |
| Temperatura | 8 | 3 | 11 |
| Conectividad | 10 | 4 | 14 |
| General | 6 | 2 | 8 |
| **Total** | **60** | **20** | **80** |

| Tipo de escenario | Desarrollo | Final reservado | Total |
| --- | ---: | ---: | ---: |
| Evidencia suficiente | 20 | 7 | 27 |
| Parcial | 8 | 5 | 13 |
| Ambigua | 6 | 2 | 8 |
| Simultánea | 7 | 1 | 8 |
| Tensión aparente | 6 | 1 | 7 |
| Comprobación adicional | 6 | 1 | 7 |
| Insuficiente | 1 | 2 | 3 |
| Fuera de cobertura | 6 | 1 | 7 |
| **Total** | **60** | **20** | **80** |

Las etiquetas se formularon desde relatos y observaciones, con apoyo de `data/evaluacion/fuentes.json`, sin copiar predicciones. Se admitió un conjunto vacío ante evidencia insuficiente o una situación fuera del catálogo, y varias hipótesis si cada una tiene sustento. La prioridad se anotó solo con motivo técnico de especificidad o preservación de datos, nunca como probabilidad. La revisión interna comprobó relato y respuestas, polaridad inversa, trayectos, IDs, referencias y firmas exactas; la similitud semántica y la plausibilidad técnica requirieron juicio editorial, sin dictamen externo. El validador no prueba independencia semántica ni verdad física. De los 80 casos, 72 corresponden a cuestionario de extremo a extremo (**54 desarrollo, 18 final**), D050 está fuera de catálogo pero es codificable y siete presentan límites del cuestionario (**cinco desarrollo, dos final**). Los denominadores previstos eran 55 y 18 elegibles, respectivamente; los siete limitados requieren análisis cualitativo separado. La distribución revisada de los 60 casos de desarrollo se documenta más adelante y en la revisión 4.1.

**Límites:** 72 casos son de cuestionario de extremo a extremo, uno es fuera del catálogo pero codificable y siete necesitan información que la ruta no recoge o una causa que el catálogo no representa (D012, D022, D032, D043, D060, F011 y F020). Esos siete se reportarán cualitativamente y no se presentarán como evaluación ordinaria de extremo a extremo. La revisión de plausibilidad y similitud fue interna, sin dictamen independiente de técnicos. El validador comprueba estructura y coherencia formal, pero no puede demostrar verdad física de los relatos.

**Validación observada:** `python validar_casos.py` terminó con código 0 y confirmó 60/20, siete rutas, trayectos alcanzables, IDs, estados, evidencia y huella. `python validar_conocimiento.py` terminó con código 0: 36 hechos, 18 diagnósticos, 42 reglas originales, 36 preguntas, siete rutas, dos hechos y cuatro reglas de B, criterios C para 36 observaciones y 18 diagnósticos. `python -m unittest discover -s tests -v` pasó **65 pruebas, 0 fallos**, incluidas cinco nuevas pruebas del validador de casos. `python -m unittest discover -s auditoria -v` pasó **10 pruebas, 0 fallos**. `git diff --check` terminó con código 0. Son verificaciones estructurales y funcionales, no una medición de accuracy, precision, recall o F1.

**Archivos creados en etapa 4:** `data/evaluacion/casos_desarrollo.json`, `casos_finales_reservados.json`, `fuentes.json`, `RESERVA_FINAL.sha256`, `MANIFIESTO.json`, `validar_casos.py`, `tests/test_validacion_casos.py` y `docs/PROTOCOLO_EVALUACION_AVANCE_2.md`. La distribución antes documentada por separado se integró en esta sección. **Modificados entonces:** `README.md`, `CHECKLIST.md` y este documento. La reserva final tiene una huella registrada y permanece sin predicciones. No se cambiaron preguntas, rutas, reglas ni motores para ajustar casos. En **esa etapa** no había métricas, modelo seleccionado, commit, publicación ni tag `avance-2`.

## Verificación observada de la etapa 1

Antes de editar, `main` estaba limpio y `HEAD` coincidía con el commit identificado por el tag anotado `avance-1` (`0907b6220eac500aee5fb1eb5542df5862ddb385`). No había diferencias frente al tag ni implementaciones activas de B/C. Pasaron el validador, 35 pruebas habituales y 10 de auditoría.

Después de implementar esta etapa:

- `python validar_conocimiento.py`: código 0; 36 hechos, 18 diagnósticos, 42 reglas, 36 preguntas y siete rutas.
- `python -m unittest discover -s tests -v`: **41 pruebas, 0 fallos**. Seis pruebas nuevas cubren contrato, selector, A predeterminado, rechazo de B/C, equivalencia de resultados y separación del cuestionario.
- `python -m unittest discover -s auditoria -v`: **10 pruebas, 0 fallos**; se conservan los testigos de 42/42 reglas y 18/18 diagnósticos.
- Los ejemplos `ram.json` y `sin_conclusion.json` terminaron con código 0. Sus salidas estándar UTF-8 conservaron exactamente los hashes SHA-256 previos: `df92584d199cacb77d8551aa16d9979636eb676b065a62d540cd9ab29e866130` y `42b840266ef58326b33849e7dc2a6cf8b8aeed54882a5988e994e369c4dd01ec`, respectivamente. También se compararon las salidas del modo predeterminado y `--modelo A`.

Las pruebas confirman regresión funcional dentro de los escenarios examinados; no miden precisión con computadoras reales. B amplía su resultado con trazas sin cambiar los cuatro campos del contrato común. C puede requerir ampliaciones posteriores.

## Verificación observada de la etapa 2

- `python validar_conocimiento.py`: código 0; base original de 36 hechos, 18 diagnósticos y 42 reglas; 36 preguntas y siete rutas; ampliación B de **2 hechos derivados y 4 reglas** válida y sin ciclos.
- `python -m unittest discover -s tests -v`: **50 pruebas, 0 fallos**. Las nuevas pruebas comprueban cadena de tres niveles, punto fijo, ausencia de activaciones repetidas, desconocidos, reglas no satisfechas, ciclo rechazado, contradicción detectada, soportes alternativos, explicación, selector, consola interactiva y recorridos de las siete rutas con B.
- `python -m unittest discover -s auditoria -v`: **10 pruebas, 0 fallos**. Esta auditoría corresponde a la base y rutas del Avance 1.
- `python diagnosticar.py --modelo B --respuestas ejemplos/arranque_multinivel_b.json`: código 0; tres rondas y diagnóstico `d_arranque_so` con ambos soportes de `h_fallo_etapa_arranque` visibles.
- Los ejemplos existentes `ram.json` y `sin_conclusion.json` se ejecutaron con B y terminaron con código 0. Para A, sus salidas estándar UTF-8 siguieron igual que antes de la etapa 2; se verificó también A predeterminado frente a A explícito.

Estos son resultados de pruebas funcionales, no accuracy, precision, recall ni F1 de diagnósticos. La ampliación solo demuestra la cadena multinivel en el ámbito del arranque; las otras rutas continúan usando reglas directas. No se ha probado exactitud en equipos reales ni se han creado viñetas de evaluación. Las reglas de B permiten una hipótesis proporcionada a las observaciones y no confirman el estado físico de una pieza.

## Archivos de la etapa 1

**Creados:** `src/diagnostico_pc/contratos.py`, `src/diagnostico_pc/selector.py`, `tests/test_arquitectura_avance_2.py`, `docs/AVANCE_2.md`.

**Modificados:** `src/diagnostico_pc/consola.py`, `README.md`, `CHECKLIST.md`.

No se modificó `avance-1` ni se creó `avance-2`. No se publicaron commits o tags.

## Archivos de la etapa 2

**Creados:** `data/conocimiento_avance2/hechos.json`, `data/conocimiento_avance2/reglas.json`, `src/diagnostico_pc/conocimiento_b.py`, `src/diagnostico_pc/modelo_b.py`, `tests/test_modelo_b.py`, `ejemplos/arranque_multinivel_b.json`.

**Modificados:** `src/diagnostico_pc/selector.py`, `src/diagnostico_pc/consola.py`, `validar_conocimiento.py`, `tests/test_arquitectura_avance_2.py`, `README.md`, `CHECKLIST.md`, `docs/AVANCE_2.md`.

`modelo_a.py`, los tres catálogos originales, las preguntas, las rutas y el tag `avance-1` permanecen intactos. No se creó `avance-2` ni se publicó nada.

## Archivos de la etapa 3

**Creados:** `data/conocimiento_avance2/criterios_c.json`, `src/diagnostico_pc/conocimiento_c.py`, `src/diagnostico_pc/modelo_c.py`, `tests/test_modelo_c.py`, `ejemplos/hipotesis_termicas_c.json`.

**Modificados:** `src/diagnostico_pc/selector.py`, `src/diagnostico_pc/consola.py`, `validar_conocimiento.py`, `tests/test_arquitectura_avance_2.py`, `tests/test_modelo_b.py` (nombre de una prueba), `README.md`, `CHECKLIST.md` y este documento. La lógica de inferencia de `modelo_a.py` y `modelo_b.py`, los catálogos de A/B, preguntas, rutas y el tag `avance-1` permanecen intactos. No se creó `avance-2`, no se realizaron commits ni publicaciones.

## Etapa 4.1: corrección metodológica del conjunto de desarrollo

Tras la aprobación con observaciones de la etapa 4, se conservó una copia byte a byte del desarrollo inicial en `data/evaluacion/historico/casos_desarrollo_etapa4_v1.json` y se revisaron solo los 60 casos de desarrollo. D055 y D057 sustituyen dos firmas exactamente duplicadas en rutas distintas. D004–D005, D017–D023 y D037–D044 permanecen como contrastes porque alteran una señal observable relevante. Se mejoró la narrativa de D017, D027, D037 y D045; D010 y D052 dejaron de imponer una prioridad única, y otras prioridades se justificaron por especificidad o preservación de datos. D030 y D045 distinguen hipótesis de distintos niveles de averías simultáneas confirmadas.

La distribución sigue siendo 6 alimentación, 10 lentitud, 10 video, 10 sistema, 8 temperatura, 10 conectividad y 6 general. Hay 22 referencias vacías, 26 de una etiqueta, 11 de dos y una de tres. Son elegibles 55 casos y permanecen excluidos 5 por límites del cuestionario. Los 18 diagnósticos aparecen, pero cuatro solo una vez; no se forzó equilibrio ni se retiraron abstenciones. La revisión detallada, tabla de cambios y limitaciones están en `docs/REVISION_CASOS_ETAPA_4_1.md`.

El conjunto original tiene SHA-256 `3aad28d05c955aab1320416bd91653c8b2137ec2a3e9ea7a11f21f3cdf14972a` y el desarrollo revisado `9f06ba6aad8b61d9d8ecc923c27e364d580e1bf55731d4674aed903019447da9`. El manifiesto registra ambas versiones y conserva la entrada de la reserva final sin recalcularla ni abrirla. Una validación aislada de desarrollo confirmó los 60 recorridos, IDs, estados, referencias y ausencia de firmas duplicadas. La batería completa de casos no se ejecutó porque su implementación lee la reserva. No se ejecutaron modelos A/B/C sobre viñetas, no se calcularon métricas, no se modificaron reglas y no se inició la Etapa 5.

## Etapa 5: evaluación experimental de los modelos A, B y C

Con autorización expresa, se evaluaron únicamente 55 casos elegibles de los 60 de desarrollo; cinco quedaron excluidos por limitaciones del cuestionario. `evaluar_desarrollo.py capturar` reprodujo cada trayecto y entregó las mismas observaciones a los tres motores. Persistió `predicciones_brutas.json` sin referencias antes de que `analizar` leyera las etiquetas. B y C produjeron los mismos conjuntos en 55/55 casos. El desarrollo revisado conservó su SHA-256 `9f06ba6aad8b61d9d8ecc923c27e364d580e1bf55731d4674aed903019447da9`; se preservó también la versión original.

Los tres modelos obtuvieron **48/55 (87,3 %) de accuracy de conjunto exacto**, **50/56 (89,3 %) de precisión micro**, **50/51 (98,0 %) de recall micro** y **100/107 (93,5 %) de F1 micro**. El principal perteneció a la referencia en **35/38** casos positivos; hubo **16/17 abstenciones correctas** y una indebida. A y B coincidieron en los conjuntos de los 55 casos; los hechos derivados de B se activaron en seis sin añadir o quitar hipótesis frente a A. C cambió el orden en cuatro casos. En los mismos diez casos con prioridad justificada, el principal coincidió **2/10 en A, 2/10 en B y 4/10 en C**; los rangos recíprocos medios fueron **0,567, 0,567 y 0,700**, respectivamente. Son prioridades de revisión técnica, no probabilidades. No se atribuye una mejora causal al mecanismo multinivel ni se afirma que C mejore la exactitud de conjunto frente a B.

El informe completo `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md` contiene la tabla, 18 matrices por modelo, gráficas, errores por ruta y escenario, IDs de casos y limitaciones. Predicciones, métricas, matrices, distribuciones, comparaciones, errores, advertencias, gráficas y huellas están en `data/evaluacion/resultados_etapa5/`. Una repetición en carpeta temporal produjo **12 archivos deterministas idénticos**. `python validar_conocimiento.py` pasó; **65 pruebas funcionales seguras** y **10 pruebas de auditoría** pasaron sin fallos. Se omitieron `validar_casos.py` y la batería global porque sus implementaciones leen la reserva final; esta no se abrió ni ejecutó.

**Archivos creados en etapa 5:** `evaluar_desarrollo.py`, `tests/test_evaluacion_desarrollo.py`, `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md` y los resultados bajo `data/evaluacion/resultados_etapa5/`. **Modificados:** `CHECKLIST.md` y este documento. No se modificaron motores, reglas, etiquetas, casos ni conocimiento, ni se creó commit o tag. No se seleccionó modelo, no se inició la etapa siguiente y no se cerró el Avance 2. La concordancia con viñetas académicas no demuestra precisión en computadoras reales.

## Etapa 6: selección y congelación del Modelo C

El usuario confirmó la revisión de las etapas 1 a 5 y autorizó únicamente esta etapa. Antes de seleccionar se cotejaron de nuevo las 26 huellas de entradas y código y la de `predicciones_brutas.json` frente a la proveniencia de la etapa 5: todas coincidieron. Sobre los 55 casos elegibles A, B y C empataron en accuracy exacto **48/55 (87,3 %)**, precisión micro **50/56 (89,3 %)**, recall micro **50/51 (98,0 %)**, F1 micro **100/107 (93,5 %)** y principal incluido en referencia **35/38 (92,1 %)**. A/B/C conservaron los mismos conjuntos. En diez prioridades justificadas, C obtuvo **4/10** y rango recíproco medio **0,700**, frente a **2/10** y **0,567** de A y B. Se selecciona C por la utilidad de su orden de revisión y la explicación de sus criterios, aceptando su mayor complejidad. La muestra de diez casos no demuestra superioridad estadística general y C no mejoró el accuracy de conjunto.

La arquitectura, el método y la selección se explican en este documento; `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md` conserva tablas, matrices, gráficas, errores y límites de la medición. El manifiesto `data/evaluacion/MANIFIESTO_SELECCION.json` fija la versión `avance2-etapa6-seleccion-v1`, Git HEAD base y SHA-256 de **44 archivos** de código, catálogos, cuestionario, protocolo, desarrollo y resultados. `python verificar_seleccion.py` confirma las huellas mediante una lista cerrada que excluye la reserva final. **A sigue predeterminado** en el selector y la consola; **C será predeterminado en la futura aplicación gráfica**. A, B y C permanecen invocables por separado.

**Verificación observada:** `python validar_conocimiento.py` terminó con código 0; **68 pruebas funcionales seguras** y **10 de auditoría** pasaron sin fallos. Tres pruebas nuevas comprobaron manifiesto intacto, rechazo de una huella alterada y rechazo de una ruta adicional. Una nueva captura y análisis en carpeta temporal reprodujeron exactamente **12 archivos deterministas** de la etapa 5; confirmaron 55 elegibles, cinco excluidos y conjuntos B/C iguales. Las ejecuciones explícitas de A, B y C con `ejemplos/ram.json` terminaron con código 0; la salida predeterminada coincidió con A. `python verificar_seleccion.py` comprobó los 44 archivos y `git diff --check` terminó con código 0. No se ejecutaron `validar_casos.py` ni la batería global de `tests` porque abren el archivo final reservado.

**Archivos creados en etapa 6:** `data/evaluacion/MANIFIESTO_SELECCION.json`, `verificar_seleccion.py` y `tests/test_seleccion_modelo.py`; los registros de esa etapa también mencionan un informe académico independiente que ya no estaba en el árbol al iniciar esta consolidación. Su función de explicar la selección y consultar las cifras se cubre ahora con este documento y el informe de resultados. **Modificados entonces:** este documento y `CHECKLIST.md`. Permanecen las limitaciones de viñetas hipotéticas, soporte escaso de varios diagnósticos y ausencia de validación en equipos reales. No se modificaron motores, reglas, prioridades, etiquetas, selector ni consola; no se abrió ni evaluó la reserva final. No hubo commit, tag, publicación, interfaz gráfica ni PDF. El cierre en Git requiere revisión y autorización expresa del usuario.

## Consolidación documental previa al cierre

La documentación de consulta queda en seis archivos principales: `AVANCE_1.md`, `AVANCE_2.md`, `BASE_CONOCIMIENTOS.md`, `PREGUNTAS.md`, `PROTOCOLO_EVALUACION_AVANCE_2.md` y `RESULTADOS_EXPERIMENTALES_AVANCE_2.md`. `REVISION_CASOS_ETAPA_4_1.md` es un séptimo registro necesario: ambos manifiestos y el evaluador de desarrollo conservan su ruta y huella. Se integraron aquí la distribución antes separada y, en los documentos técnicos del Avance 1, las conclusiones vigentes de sus auditorías y rediseño. Los originales de Avance 1 permanecen recuperables desde el tag `avance-1`.

En esta consolidación no se alteraron los tres documentos protegidos, los resultados experimentales, los motores, el conocimiento, el cuestionario ni las rutas. `python verificar_seleccion.py` confirmó las **44 huellas**; `python validar_conocimiento.py`, **68 pruebas funcionales seleccionadas** y **10 pruebas de auditoría** terminaron correctamente. La batería global y `validar_casos.py` se omitieron porque sus implementaciones actuales leen la reserva final. No se evaluaron casos finales ni se creó commit, tag o publicación. Estas verificaciones conservan la reproducibilidad del desarrollo; no añaden evidencia de rendimiento en equipos reales.

## Cierre definitivo del Avance 2

Por autorización expresa del usuario, la versión académica de esta etapa se identifica como `avance-2`. El **Modelo A** conserva la inferencia directa mediante reglas; el **Modelo B** aplica encadenamiento hacia adelante con hechos derivados; el **Modelo C** reutiliza el cierre de B y resuelve la prioridad de hipótesis mediante criterios simbólicos de evidencia. Los tres permanecen disponibles y funcionales. C fue seleccionado para la interfaz gráfica de la entrega final; A sigue siendo el modelo predeterminado en la consola por compatibilidad.

En los **55 casos elegibles de desarrollo**, A, B y C obtuvieron **87,3 % de exactitud de conjunto**, **89,3 % de precisión micro**, **98,0 % de recall micro** y **93,5 % de F1 micro**. En los diez casos con prioridad principal justificada, el acierto fue **2/10 en A**, **2/10 en B** y **4/10 en C**. C conserva el razonamiento multinivel de B y mejoró la priorización observada en ese subconjunto; su selección no demuestra superioridad estadística general ni mayor exactitud de conjunto. Son resultados de viñetas académicas de desarrollo, no de la evaluación final ni de computadoras reales.

En el cierre, `python verificar_seleccion.py` confirmó la coincidencia de las **44 huellas SHA-256**; `python validar_conocimiento.py` terminó correctamente; pasaron **68 pruebas funcionales seguras** y **10 pruebas de auditoría**, sin fallos. Los motores A, B y C, el conocimiento, los resultados experimentales y los archivos protegidos mantuvieron su integridad. No se modificaron los manifiestos congelados. La batería global y `validar_casos.py` permanecen pendientes porque leen la reserva final.

La consolidación integró la información vigente en los documentos técnicos principales y conservó el registro histórico de la revisión 4.1 en su ruta protegida. Los **20 casos finales** permanecen reservados: no se abrieron ni ejecutaron durante este cierre, no se incluirán en GitHub y se evaluarán únicamente en la fase autorizada de la entrega final.
