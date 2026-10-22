# Avance 2 — Etapa 4.1: corrección metodológica del desarrollo

**Alcance:** exclusivamente los 60 casos de desarrollo, antes de inferencia diagnóstica. No se abrió, ejecutó ni modificó el archivo de 20 casos reservados. Esta revisión no estima accuracy, precision, recall ni F1.

El conjunto anterior se conservó, byte a byte, en `data/evaluacion/historico/casos_desarrollo_etapa4_v1.json` (SHA-256 `3aad28d05c955aab1320416bd91653c8b2137ec2a3e9ea7a11f21f3cdf14972a`). La versión revisada de `casos_desarrollo.json` tiene SHA-256 `9f06ba6aad8b61d9d8ecc923c27e364d580e1bf55731d4674aed903019447da9`. Ambas huellas figuran en `data/evaluacion/MANIFIESTO.json`; la entrada de la reserva y su sello externo conservan la huella registrada `7c609c0c614b1955d3fbbacca260b99f8c30f2b54e81473277bbe767f505d364`. Esa concordancia de registros no equivale a recalcular el hash del archivo final, pues no se leyó.

## Cambios controlados

| ID | Problema identificado | Cambio realizado | Justificación técnica | Validación observada |
| --- | --- | --- | --- | --- |
| D010 | Dos recursos altos sin base para ordenar uno primero. | `prioridad_revision=null`; se conservan ambas etiquetas. | Poco espacio y presión de memoria tienen soporte, pero el relato no establece urgencia relativa. | ID, etiquetas y trayecto válidos. |
| D013 | Prioridad de almacenamiento sin razón comparativa explícita. | Se explicitó preservación de datos ante errores de lectura. | El posible riesgo de datos fundamenta revisar unidad/enlace pronto; el proceso exigente sigue como línea aparte. | Prioridad pertenece al conjunto; trayecto válido. |
| D017 | Relato muy cercano al antecedente de la regla de pantalla externa. | Se añadió cronología de traslado, encendido y prueba HDMI; se indicó qué falta revisar. | La prueba comparativa sostiene revisar el panel sin afirmar daño físico. | Estados, etiqueta y trayecto conservados. |
| D027 | Relato casi enumeraba las condiciones de una regla de arranque. | Se situó el episodio en un equipo de laboratorio y se describió la consulta de firmware. | La unidad visible y el fallo posterior al logotipo orientan al arranque sin confirmar archivos dañados. | Estados, etiqueta y trayecto conservados. |
| D030 | Tres etiquetas podían leerse como tres averías; prioridad poco explícita. | Se aclaró que son líneas de distinto alcance que podrían compartir causa y que los errores de E/S motivan proteger datos. | Distingue hipótesis defendible, orden de revisión y causa no confirmada. | Tres etiquetas válidas y trayecto válido. |
| D033 | Prioridad de almacenamiento sin fundamento de urgencia claro. | Se explicitó respaldo de datos antes de reparar inicio. | La unidad visible no demuestra salud del medio ante errores de lectura. | Prioridad válida; trayecto conservado. |
| D037 | Relato térmico demasiado próximo a una lista de condiciones. | Se describió exportación de video, secuencia hasta el apagado y registro de sensor previo. | La medición se compara con el límite de la pieza; ruido y calor son indicios adicionales, no causa confirmada. | Estados, etiquetas y trayecto conservados. |
| D045 | Relato similar a condiciones de Wi-Fi; dos etiquetas podían sugerir dos fallas. | Se contextualizó la comparación en la misma red y se aclaró que las etiquetas expresan niveles de la misma situación. | Adaptador deshabilitado es revisión específica; conectividad local describe el ámbito. | Estados, etiquetas y trayecto conservados. |
| D052 | Cable local y falla en otro equipo, sin orden único defendible. | `prioridad_revision=null`; se conservaron ambas hipótesis. | Las comprobaciones local y compartida son necesarias, pero la evidencia no ordena su urgencia. | Conjunto y trayecto válidos. |
| D055 | Observaciones y etiqueta idénticas a D001; cambiar solo de ruta no aportaba señal nueva al motor. | Se sustituyó por un episodio de pantalla azul tras uso normal, adquirido por la ruta general. | Explora un error crítico con hechos negativos de contexto y sin asignar causa física. | 12 preguntas alcanzables; firma nueva y etiqueta válida. |
| D057 | Observaciones y etiqueta idénticas a D017. | Se sustituyó por temperatura medida alta sin apagado ni ruido, adquirida por la ruta general. | Contrasta medición interna con ausencia de otros signos térmicos, sin identificar la pieza causante. | 11 preguntas alcanzables; firma nueva y etiqueta válida. |
| D059 | Prioridad de almacenamiento carecía de motivo explícito. | Se documentó respaldo temprano de datos y posible causa común con el fallo de arranque. | El error de lectura requiere cautela antes de reparar el inicio. | Prioridad válida; trayecto conservado. |

## Contrastes conservados y similitud restante

- D004–D005: LED encendido frente a apagado con ventilador y pantalla negra. La diferencia prueba si se da demasiado peso a un indicador aislado.
- D017–D023: la pantalla externa funciona en ambos; cambia el LED. Sirve para comprobar que el LED apagado no anula esa comparación.
- D037–D044: ambos tienen temperatura medida alta; cambia el ruido del ventilador. Comprueba que la ausencia de ruido no invalida la medición.

No quedan firmas de observaciones exactamente duplicadas entre los 60 casos. La comparación de relatos no encontró pares casi literales con el umbral interno usado; esto no demuestra independencia semántica completa. Persisten patrones próximos, especialmente D033–D059 (arranque con unidad visible y error de lectura, en rutas distintas), D022–D026 (sin etiqueta, pero uno fuera del cuestionario y otro incierto) y D002–D056 (abstención con distinto grado de información). Se conservaron porque cambian contexto, alcance o disponibilidad de datos; D033–D059 seguirá siendo una posible dependencia al interpretar resultados.

## Distribución revisada

| Ruta | Casos | Escenario | Casos |
| --- | ---: | --- | ---: |
| Alimentación | 6 | Evidencia suficiente | 20 |
| Lentitud | 10 | Parcial | 8 |
| Video | 10 | Ambigua | 6 |
| Sistema | 10 | Simultánea | 7 |
| Temperatura | 8 | Tensión aparente | 6 |
| Conectividad | 10 | Comprobación adicional | 6 |
| General | 6 | Insuficiente | 1 |
| | | Fuera de cobertura | 6 |
| **Total** | **60** | **Total** | **60** |

Hay **22 conjuntos esperados vacíos**, **26 con una hipótesis**, **11 con dos** y **1 con tres**. Son elegibles **55** casos para la evaluación principal: 54 de extremo a extremo y D050, fuera de catálogo pero codificable. Los cinco excluidos por límites del cuestionario son D012, D022, D032, D043 y D060. No se redujeron abstenciones para alterar métricas futuras. Todos los 18 diagnósticos aparecen al menos una vez, pero `d_ruta_alimentacion`, `d_deteccion_almacenamiento`, `d_subsistema_video` y `d_wifi_inhabilitado` aparecen solo una vez cada uno. Esta baja representación limita cualquier análisis individual por diagnóstico; no se añadieron casos para forzar equilibrio.

## Control y límites

Se validaron los 60 registros contra catálogos de hechos, diagnósticos, preguntas, rutas y referencias. Sus estados conservan `verdadero`, `falso` y `desconocido`. El gestor de preguntas reprodujo **60/60 trayectos** hasta un terminal válido, con observaciones exactamente iguales a las codificadas. Los dos reemplazos conservan relato, evidencia, faltantes y justificación coherentes con sus respuestas. La revisión de similitud combinó firmas de observaciones y semejanza textual; una revisión humana sigue siendo necesaria para semejanza causal profunda.

La proximidad entre algunas etiquetas y condiciones de reglas persiste porque ambos usan el mismo catálogo y las mismas preguntas. Se redujo la redacción artificial de D017, D027, D037 y D045, sin usar salidas de motores. Las etiquetas de varios niveles, como D030 y D045, no se interpretan como averías simultáneas. Las prioridades conservadas expresan el orden de comprobación por especificidad o preservación de datos, nunca probabilidad ni confirmación de una pieza.

No se ejecutó `validar_casos.py` ni la batería completa `unittest discover`, porque ambos leen el archivo final reservado en la implementación vigente y esta autorización prohíbe inspeccionarlo. La validación estructural de desarrollo se ejecutó de forma aislada usando las mismas funciones de caso y el gestor de preguntas, sin cargar la reserva ni importar motores. No se cambiaron reglas, diagnósticos, preguntas, rutas ni motores.
