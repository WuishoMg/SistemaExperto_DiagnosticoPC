# Protocolo experimental predefinido — Avance 2, etapa 4

**Estado:** diseño y validación estructural. Ninguno de los modelos A, B o C se ejecutó sobre las 80 viñetas. No existen resultados de calidad diagnóstica ni selección de modelo.

## Unidad de análisis y alcance

Los archivos `data/evaluacion/casos_desarrollo.json` y `casos_finales_reservados.json` contienen 60 y 20 **viñetas académicas** hipotéticas. Las etiquetas describen hipótesis defendibles a partir del relato, no causas físicas confirmadas. Cada caso conserva ruta, trayecto de preguntas, hechos trivalentes, conjunto esperado, prioridad cuando hay fundamento, evidencia, faltantes, comprobaciones, justificación y referencias. Un `desconocido` significa que no se obtuvo la información; nunca se convierte en `falso`.

El universo primario de una futura evaluación de extremo a extremo son los casos con `alcance=cuestionario_extremo_a_extremo` o `fuera_catalogo`. El caso fuera de catálogo permite estudiar abstención porque sus observaciones sí son obtenibles. Los siete casos `limitacion_cuestionario` se informarán **aparte** y no entrarán en denominadores de calidad de extremo a extremo: D012 (aplicación específica), D022 (color e impresión), D032 (licencia de aplicación), D043 (ruido mecánico del ventilador), D060 (periférico USB), F011 (autenticación empresarial) y F020 (lápiz digital). Su dato decisivo no es preguntado por la ruta o no tiene diagnóstico representado. La estructura de estos casos se valida ahora, pero no se usarán para atribuir un error de diagnóstico completo a un motor.

La reserva final queda separada y sellada en `data/evaluacion/RESERVA_FINAL.sha256`. Los 20 casos finales del intento previo están expuestos y no forman parte de estos archivos. No se incorporan sus etiquetas ni salidas. La única evaluación final prevista será una vez, tras seleccionar y congelar el modelo en una fase posterior autorizada.

## Protocolo de predicciones para la futura etapa autorizada

Para cada caso elegible, adquirir únicamente las respuestas del `trayecto_preguntas` y sus `observaciones` mediante la ruta indicada, sin inyectar hechos que el cuestionario no alcanzó. Ejecutar A, B y C solo sobre los 60 de desarrollo cuando la evaluación sea autorizada. Registrar por caso y modelo la lista ordenada de IDs diagnósticos sin duplicados, el principal (primer elemento o `null`) y la versión exacta de datos y código. No usar el relato, justificación ni etiquetas como entrada del motor. Separar estrictamente predicción y referencia.

La comparación de **conjuntos** de B y C es también un control funcional: deben ser idénticos por caso, pues C solo cambia el orden de las hipótesis de B. Cualquier diferencia de conjunto se investiga como regresión antes de interpretar métricas. La calidad del orden se calcula por separado. Las pruebas de `unittest` verifican funcionamiento, no precisión diagnóstica.

## Métricas definidas antes de observar predicciones

Sea `R_i` el conjunto de referencia, `P_i` el conjunto predicho y `N` el número de casos elegibles del grupo evaluado.

1. **Accuracy de conjunto exacto:** `(número de casos con P_i = R_i) / N`. Un par de conjuntos vacíos cuenta como acierto exacto; un conjunto vacío frente a uno no vacío es error. Los diagnósticos extra y los omitidos impiden el acierto.
2. **Micro precisión, recall y F1 multietiqueta:** sumar `TP = Σ_i |P_i ∩ R_i|`, `FP = Σ_i |P_i − R_i|` y `FN = Σ_i |R_i − P_i|`. Precisión `TP/(TP+FP)`, recall `TP/(TP+FN)` y F1 `2TP/(2TP+FP+FN)`. Los conjuntos vacíos no generan verdaderos positivos ficticios. Si un denominador es cero en todo el grupo, informar «indefinido» para esa métrica; no convertirlo en 100 %.
3. **Matrices por diagnóstico:** para cada uno de los 18 IDs, contar TP, FP, FN y TN sobre los mismos `N` casos elegibles, en formato 2×2 con filas referencia ausente/presente y columnas predicción ausente/presente. Incluir el denominador y soporte de referencia. No agregar resultados de los casos limitados.
4. **Acierto del principal:** entre casos elegibles con `R_i` no vacío, proporción donde el primer diagnóstico predicho pertenece a `R_i`. La abstención en un caso positivo cuenta como fallo. Los casos de referencia vacía se analizan en abstención.
5. **Priorización:** solo entre casos con al menos dos etiquetas defendibles y `prioridad_revision` justificada, medir proporción cuyo principal coincide con el ID prioritario y rango recíproco `1/r` de ese ID en la lista predicha (cero si ausente). Reportar ambos con su denominador. La referencia no impone un orden total; no evaluar posiciones no justificadas. La prioridad es de revisión técnica, no probabilidad de avería.
6. **Abstención:** en casos elegibles con referencia vacía, contar abstenciones correctas (`P_i` vacío) y salidas espurias (`P_i` no vacío). En casos con referencia no vacía, contar abstenciones incorrectas. Informar tasas y conteos con los denominadores de cada subgrupo. Informar por separado los casos fuera del catálogo.

Un caso con varias etiquetas cuenta como un solo caso en accuracy exacto y principal, pero aporta una decisión binaria por diagnóstico a las métricas micro y matrices. Ninguna métrica se calcula en esta etapa. Reportar en la futura evaluación conteos y denominadores, además de porcentajes, sin buscar un intervalo predeterminado.

## Análisis y control de calidad

En la futura evaluación, tabular errores por ruta y `tipo_escenario`: omisión de una hipótesis, hipótesis extra, abstención indebida, falta de abstención y prioridad no justificada. Examinar relatos y trazas después de congelar predicciones para evitar cambiar etiquetas en función de una salida. Si una etiqueta resulta discutible, registrar desacuerdo y razonamiento, preservar la versión inicial y decidir una revisión documentada **solo con desarrollo**. No ajustar reglas, escoger modelos ni revisar casos a partir de la reserva final.

El control interno de esta etapa verificó IDs, estados, polaridad, secuencia alcanzable, separación de archivos, duplicados exactos de firma entre grupos, referencias, evidencia conocida y huella. Se revisaron manualmente las viñetas para que la historia no contradiga hechos codificados, el conjunto esperado no copie una salida de A/B/C y las prioridades respondan a una acción técnica. Este control no equivale a una revisión independiente por técnicos especializados. El validador no puede demostrar por sí solo plausibilidad física ni independencia semántica; esos límites se conservan para revisión académica.

## Reproducibilidad y custodia

Desde la raíz: `python validar_casos.py`, `python validar_conocimiento.py` y `python -m unittest discover -s tests -v`. El primer comando solo carga JSON, catálogo y grafo de preguntas; no importa ni ejecuta motores de inferencia. La huella SHA-256 verifica los bytes de la reserva; si se autoriza una corrección editorial de esa reserva, registrar motivo, nueva versión y nueva huella antes de toda evaluación. Los cambios de conocimiento, preguntas o rutas invalidan la compatibilidad registrada y exigen una revisión explícita del protocolo.

El manifiesto de archivos y huellas de esta preparación está en `data/evaluacion/MANIFIESTO.json`. El repositorio conserva cambios locales sin commit ni tag de entrega de esta etapa. El procedimiento futuro debe archivar configuración, hashes, código, predicciones brutas y resumen de métricas de cada ejecución autorizada. El archivo de reserva nunca se suministrará al evaluador de Avance 2 ni se imprimirá con predicciones antes de la entrega final.

## Fuentes de diseño

El catálogo completo y el uso concreto de cada fuente están en `data/evaluacion/fuentes.json`. Se consultaron guías primarias de [Dell sobre energía, POST, video y arranque](https://www.dell.com/support/kbdoc/en-us/000125609/resolve-no-power-no-post-no-boot-or-no-video-issues-with-your-dell-computer), [Dell sobre memoria](https://www.dell.com/support/kbdoc/en-us/000126066/how-to-diagnose-and-resolve-common-memory-issues-on-a-dell-notebook-pc) y [Dell sobre unidades](https://www.dell.com/support/contents/en-bs/article/product-support/self-support-knowledgebase/data-storage-backup-and-recovery/hard-drive-ssd-issues); [Microsoft sobre reparación de inicio](https://support.microsoft.com/en-us/windows/experience/startup-boot/startup-repair), [pantallas azules](https://support.microsoft.com/en-US/windows/resolving-blue-screen-errors-in-windows-60b01860-58f2-be66-7516-5c45a66ae3c6), [rendimiento](https://support.microsoft.com/en-us/windows/experience/performance-optimization/tips-to-improve-pc-performance-in-windows), [Wi-Fi](https://support.microsoft.com/en-us/windows/fix-wi-fi-connection-issues-in-windows-9424a1f7-6a3b-65a6-4d78-7f07eee84d2c) y [Ethernet](https://support.microsoft.com/en-us/windows/experience/connectivity-networking/fix-ethernet-connection-problems-in-windows); e [Intel sobre límites térmicos](https://www.intel.com/content/www/us/en/support/articles/000088048/processors.html). Las guías informan criterios de revisión, pero no confirman causas en estas viñetas hipotéticas.
