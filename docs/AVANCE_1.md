# Informe académico — Avance 1: fundamentos de IA simbólica

**Estado:** componentes y pruebas del Avance 1 preparados; revisión y cierre de la entrega pendientes. Este informe describe únicamente lo implementado hasta la Fase 3. No existe todavía el tag `avance-1`.

## 1. Introducción y objetivo

Una falla de computadora puede producir síntomas similares a los de otras fallas. El proyecto busca orientar el diagnóstico mediante conocimiento técnico explícito y dejar visible por qué se propone cada hipótesis. El objetivo de este avance es construir una base de conocimientos verificable y un primer modelo funcional de inferencia directa, que pueda usarse desde la consola.

## 2. Componentes desarrollados

- Base JSON validada con 20 síntomas, 11 diagnósticos y 23 reglas de producción, descrita en [BASE_CONOCIMIENTOS.md](BASE_CONOCIMIENTOS.md).
- Representación de observaciones con tres estados: `verdadero`, `falso` y `desconocido`.
- Validador de archivos, identificadores, referencias, condiciones y conclusiones.
- Memoria de trabajo, motor de reglas directas, Modelo A y explicación de resultados.
- Consulta interactiva por consola, lectura opcional de respuestas JSON y pruebas automáticas.

## 3. Fundamentos de IA utilizados

La base de conocimientos conserva síntomas, reglas SI–ENTONCES, posibles diagnósticos y recomendaciones. La base de hechos de cada consulta registra las respuestas del usuario; una respuesta omitida permanece desconocida, sin convertirse en falsa. El motor compara las condiciones de cada regla con esos hechos. Si todas se cumplen, la regla se activa y añade su conclusión diagnóstica a la memoria de trabajo. Esta secuencia de **hechos hacia conclusiones** constituye el encadenamiento hacia adelante básico del Modelo A.

El conocimiento es simbólico y no fue aprendido de datos. Ni el número de reglas activadas ni la especificidad de una regla son probabilidades de falla.

## 4. Arquitectura y funcionamiento

El flujo es: respuestas de consola o JSON → normalización trivalente → memoria de trabajo → evaluación de reglas directas → agrupación de conclusiones → orden de presentación → explicación y recomendaciones. `hechos.py` maneja estados; `validacion.py` garantiza que la base tenga estructura válida; `modelo_a.py` evalúa reglas; `consola.py` presenta la interacción. La interfaz no contiene las condiciones técnicas del diagnóstico.

Cada regla activa aporta su ID, explicación y lista de hechos verificados. Si varias reglas concluyen el mismo diagnóstico, se muestran como evidencias de una sola hipótesis. Si aparecen diagnósticos distintos, el principal es el que tenga una regla activada con más condiciones; en un empate se usa el ID de diagnóstico en orden alfabético. Los demás se muestran como alternativas. Este criterio es determinista y sencillo de explicar, pero no mide certeza. Si ninguna regla coincide, el sistema informa que no hay diagnóstico concluyente y distingue entre ausencia total de observaciones y observaciones sin coincidencia.

## 5. Implementaciones y uso

Desde la raíz del proyecto, `python diagnosticar.py` inicia 20 preguntas. `s` significa verdadero, `n` falso y `?` o Enter desconocido. Para una consulta repetible, `python diagnosticar.py --respuestas ejemplos/ram.json` lee un objeto JSON que puede incluir solo los síntomas observados. `python diagnosticar.py --respuestas ejemplos/sin_conclusion.json` muestra una consulta sin conclusión. La lista completa de símbolos y reglas está en el documento de la base de conocimientos.

Los archivos de conocimiento de la Fase 2 se integraron sin cambiar su contenido. Se añadió una función de lectura reutilizable al validador para que el Modelo A valide los documentos antes de usarlos.

## 6. Pruebas ejecutadas y resultados reales

Se ejecutó `python validar_conocimiento.py`: **válido**, con 20 hechos, 11 diagnósticos y 23 reglas. Después, `python -m unittest discover -s tests -v` terminó con **14 pruebas correctas y 0 fallos** en Python 3.14.2 sobre Windows.

Las pruebas del Modelo A cubren: activación de dos reglas para una sola hipótesis de sobrecalentamiento; obligación de confirmar explícitamente una condición falsa de detección de unidad; respuesta sin conclusión con hechos desconocidos o insuficientes; coexistencia de hipótesis de video y error crítico; desempate determinista entre RAM y video; preguntas de consola con respuestas desconocidas; consulta interactiva completa de 20 preguntas; y ejecución real en subproceso de los ejemplos de RAM y sin conclusión.

La ejecución de `python diagnosticar.py --respuestas ejemplos/ram.json` terminó correctamente y mostró una hipótesis principal de RAM, las reglas `r_ram_reinicio_post` y `r_ram_codigo_post`, los hechos observados y recomendaciones. La prueba funcional del ejemplo sin conclusión comprobó su mensaje y código de salida 0. La suite se repitió completa tras corregir una diferencia de codificación en la captura del subproceso de Windows.

## 7. Evidencias técnicas disponibles

El catálogo JSON, el validador, el código del Modelo A, las pruebas y los dos archivos de ejemplo permiten repetir estas verificaciones sin paquetes externos. `CHECKLIST.md` conserva los comandos y resultados observados. El código de salida 0 de las consultas indica que el programa se ejecutó; **no** confirma que una hipótesis sea la causa física real.

## 8. Limitaciones y problemas pendientes

El Modelo A solo concluye diagnósticos directamente desde observaciones. Recorre una vez las reglas porque sus conclusiones no generan hechos intermedios usados por otras reglas. No resuelve contradicciones semánticas entre síntomas distintos ni asigna grados de certeza. Cuando faltan datos, puede no concluir; cuando varias reglas coinciden, conserva hipótesis alternativas sin decidir cuál es verdadera. La base aún no se ha evaluado con 80 casos ni revisado mediante un protocolo independiente; no es posible reportar precisión, cobertura o matriz de confusión.

## 9. Conclusiones

El avance dispone de un sistema simbólico ejecutable desde consola y capaz de explicar diagnósticos directos. Las pruebas demuestran el comportamiento del software para los escenarios indicados y la integridad del catálogo actual. Su rendimiento diagnóstico en casos reales sigue sin establecerse.

## 10. Próximas implementaciones previstas

Tras la validación y cierre autorizado de este avance, el Avance 2 podrá incorporar hechos intermedios, los Modelos B y C, un criterio de conflictos más elaborado y la evaluación comparativa con casos de referencia. La preparación de 80 casos, las métricas y la selección de modelo pertenecen a fases posteriores y no forman parte de esta entrega.
