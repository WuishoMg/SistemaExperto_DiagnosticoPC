# Informe académico — Avance 1: fundamentos de IA simbólica

**Estado:** componentes, pruebas y mejora de preguntas del Avance 1 preparados; revisión y cierre de la entrega pendientes. Este informe describe únicamente lo implementado hasta la Fase 3 y su mejora de usabilidad. No existe todavía el tag `avance-1`.

## 1. Introducción y objetivo

Una falla de computadora puede producir síntomas similares a los de otras fallas. El proyecto busca orientar el diagnóstico mediante conocimiento técnico explícito y dejar visible por qué se propone cada hipótesis. El objetivo de este avance es construir una base de conocimientos verificable y un primer modelo funcional de inferencia directa, que pueda usarse desde la consola.

## 2. Componentes desarrollados

- Base JSON validada con 20 síntomas, 11 diagnósticos y 23 reglas de producción, descrita en [BASE_CONOCIMIENTOS.md](BASE_CONOCIMIENTOS.md).
- Representación de observaciones con tres estados: `verdadero`, `falso` y `desconocido`.
- Validador de archivos, identificadores, referencias, condiciones y conclusiones.
- Memoria de trabajo, motor de reglas directas, Modelo A y explicación de resultados.
- Consulta interactiva por consola con 20 preguntas claras y ayuda contextual, lectura opcional de respuestas JSON y pruebas automáticas.

## 3. Fundamentos de IA utilizados

La base de conocimientos conserva síntomas, reglas SI–ENTONCES, posibles diagnósticos y recomendaciones. La base de hechos de cada consulta registra las respuestas del usuario; una respuesta omitida permanece desconocida, sin convertirse en falsa. El motor compara las condiciones de cada regla con esos hechos. Si todas se cumplen, la regla se activa y añade su conclusión diagnóstica a la memoria de trabajo. Esta secuencia de **hechos hacia conclusiones** constituye el encadenamiento hacia adelante básico del Modelo A.

El conocimiento es simbólico y no fue aprendido de datos. Ni el número de reglas activadas ni la especificidad de una regla son probabilidades de falla.

## 4. Arquitectura y funcionamiento

El flujo es: respuestas visibles → mapeo de polaridad de cada pregunta → hechos trivalentes → memoria de trabajo → evaluación de reglas directas → agrupación de conclusiones → orden de presentación → explicación y recomendaciones. Las respuestas JSON técnicas entran directamente como hechos trivalentes. `hechos.py` maneja estados; `validacion.py` garantiza que la base tenga estructura válida; `preguntas.py` valida y traduce el cuestionario; `modelo_a.py` evalúa reglas; `consola.py` presenta la interacción. La interfaz no contiene las condiciones técnicas del diagnóstico.

Las preguntas y ayudas están en [PREGUNTAS.md](PREGUNTAS.md) y en `data/interfaz/preguntas.json`. Cada pregunta declara por separado qué estado significa Sí y qué estado significa No. Seis están redactadas con la polaridad opuesta al nombre del síntoma interno; por ejemplo, responder Sí a «¿Aparece alguna imagen en la pantalla principal?» registra `s_sin_imagen = falso`. No estoy seguro siempre registra `desconocido`. Este catálogo puede alimentar otra interfaz sin cambiar el motor ni las 23 reglas.

Cada regla activa aporta su ID, explicación y lista de hechos verificados. Si varias reglas concluyen el mismo diagnóstico, se muestran como evidencias de una sola hipótesis. Si aparecen diagnósticos distintos, el principal es el que tenga una regla activada con más condiciones; en un empate se usa el ID de diagnóstico en orden alfabético. Los demás se muestran como alternativas. Este criterio es determinista y sencillo de explicar, pero no mide certeza. Si ninguna regla coincide, el sistema informa que no hay diagnóstico concluyente y distingue entre ausencia total de observaciones y observaciones sin coincidencia.

## 5. Implementaciones y uso

Desde la raíz del proyecto, `python diagnosticar.py` inicia 20 preguntas. Las opciones visibles son Sí (`1`), No (`2`) y No estoy seguro (`3` o Enter). El programa muestra una explicación de qué observar en cada pregunta. Para una consulta repetible, `python diagnosticar.py --respuestas ejemplos/ram.json` lee un objeto JSON con estados **internos** que puede incluir solo los síntomas observados. `python diagnosticar.py --respuestas ejemplos/sin_conclusion.json` muestra una consulta sin conclusión. La lista completa de símbolos y reglas está en el documento de la base de conocimientos.

Los archivos de conocimiento de la Fase 2 se integraron sin cambiar su contenido. Se añadió una función de lectura reutilizable al validador para que el Modelo A valide los documentos antes de usarlos.

## 6. Pruebas ejecutadas y resultados reales

Se ejecutó `python validar_conocimiento.py`: **válido**, con 20 hechos, 11 diagnósticos, 23 reglas y 20 preguntas. Después, `python -m unittest discover -s tests -v` terminó con **19 pruebas correctas y 0 fallos** en Python 3.14.2 sobre Windows.

Las pruebas del Modelo A cubren: activación de dos reglas para una sola hipótesis de sobrecalentamiento; obligación de confirmar explícitamente una condición falsa de detección de unidad; respuesta sin conclusión con hechos desconocidos o insuficientes; coexistencia de hipótesis de video y error crítico; desempate determinista entre RAM y video; preguntas de consola con respuestas desconocidas; consulta interactiva completa de 20 preguntas; y ejecución real en subproceso de los ejemplos de RAM y sin conclusión. Las pruebas de usabilidad verifican la ayuda y las tres opciones, las polaridades de las 20 preguntas, reglas activadas por respuestas invertidas y el rechazo de preguntas duplicadas o mal definidas.

La ejecución de `python diagnosticar.py --respuestas ejemplos/ram.json` terminó correctamente y mostró una hipótesis principal de RAM, las reglas `r_ram_reinicio_post` y `r_ram_codigo_post`, los hechos observados y recomendaciones. La prueba funcional del ejemplo sin conclusión comprobó su mensaje y código de salida 0. La suite se repitió completa tras corregir una diferencia de codificación en la captura del subproceso de Windows.

En una demostración interactiva posterior, se respondió No a las preguntas 1 y 2 y No estoy seguro a las otras 18. La consola terminó con código 0 y mostró la hipótesis de ruta de alimentación, activada por `r_alimentacion_led`. La explicación confirmó el mapeo `s_no_enciende = verdadero` y `s_led_encendido = falso`, sin alterar las reglas existentes.

## 7. Evidencias técnicas disponibles

El catálogo JSON de conocimiento, el cuestionario independiente, los validadores, el código del Modelo A, las pruebas y los dos archivos de ejemplo permiten repetir estas verificaciones sin paquetes externos. `CHECKLIST.md` conserva los comandos y resultados observados. El código de salida 0 de las consultas indica que el programa se ejecutó; **no** confirma que una hipótesis sea la causa física real.

## 8. Limitaciones y problemas pendientes

El Modelo A solo concluye diagnósticos directamente desde observaciones. Recorre una vez las reglas porque sus conclusiones no generan hechos intermedios usados por otras reglas. No resuelve contradicciones semánticas entre síntomas distintos ni asigna grados de certeza. Cuando faltan datos, puede no concluir; cuando varias reglas coinciden, conserva hipótesis alternativas sin decidir cuál es verdadera. La base aún no se ha evaluado con 80 casos ni revisado mediante un protocolo independiente; no es posible reportar precisión, cobertura o matriz de confusión.

## 9. Conclusiones

El avance dispone de un sistema simbólico ejecutable desde consola y capaz de explicar diagnósticos directos. Las pruebas demuestran el comportamiento del software para los escenarios indicados y la integridad del catálogo actual. Su rendimiento diagnóstico en casos reales sigue sin establecerse.

## 10. Próximas implementaciones previstas

Tras la validación y cierre autorizado de este avance, el Avance 2 podrá incorporar hechos intermedios, los Modelos B y C, un criterio de conflictos más elaborado y la evaluación comparativa con casos de referencia. La preparación de 80 casos, las métricas y la selección de modelo pertenecen a fases posteriores y no forman parte de esta entrega.
