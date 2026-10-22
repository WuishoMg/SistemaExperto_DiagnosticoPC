# Base de conocimientos — Avance 1

## Contrato

Los archivos JSON de conocimiento conservan `version: 1`: **36 hechos observables, 18 diagnósticos y 42 reglas**. Cada hecho tiene `verdadero`, `falso` o `desconocido`. Una omisión y «No estoy seguro» quedan desconocidas; ninguna regla diagnóstica exige ese estado. Las condiciones de una regla SI–ENTONCES son conjuntivas y su conclusión es una hipótesis. Modelo A recorre las reglas directas y agrupa las que llegan a un mismo diagnóstico. Su orden por especificidad no es probabilidad; la consola coloca una temperatura alta medida antes que indicios subjetivos cuando ambos se infieren.

El grafo de preguntas y su validador están en la capa de interfaz. Adquieren hechos, pero nunca generan conclusiones diagnósticas. Los 36 hechos tienen una pregunta visible; una pregunta puede aparecer en más de una ruta si es relevante. Los estados y reglas pueden evaluarse también con un JSON técnico, sin usar el cuestionario.

## Revisión del catálogo

| Grupo | Observaciones y decisiones |
| --- | --- |
| Alimentación e inicio | Luz y ventilador son hechos separados. Ausencia comprobada de ambos orienta a alimentación. Su presencia **no** implica funcionamiento correcto: sin imagen o sin sistema utilizable se registra una hipótesis amplia de inicio con energía. |
| Video y memoria | Se distingue imagen breve de imagen que permanece. La segunda pantalla debe mantener imagen después del logotipo para sustentar la hipótesis de pantalla principal. Un código de memoria solo cuenta si se identificó mediante el manual, o si una prueba de memoria informó errores. Sin señal en dos pantallas admite varias causas. |
| Sistema y almacenamiento | Reinicio previo al sistema y etapa de arranque alcanzada son hechos distintos. `p10=Sí` significa **unidad detectada** y registra `s_unidad_no_detectada=falso`; `p10=No` registra `verdadero`. La regla de archivos de arranque requiere etapa alcanzada y unidad presente. |
| Temperatura | `d_sobrecalentamiento` ahora se presenta como «Temperatura anormal medida» y exige una medición alta. `d_indicios_termicos` exige calor percibido más ruido de ventilador o apagado bajo carga; no afirma una medición. |
| Conectividad | Fallo web, tipo de enlace, otros dispositivos, Wi-Fi activo y aviso de cable son observaciones distintas. Si una página abre, se pueden registrar cortes intermitentes o una página concreta que falla. Solo una comparación simultánea o de la misma página en otro dispositivo activa las nuevas reglas de red compartida/local. Un No a «¿intentas usar Wi-Fi?» no confirma Ethernet. |
| Rendimiento | Lentitud al abrir programas y congelamientos se separaron. También se separó consumo del procesador y del disco. Las reglas directas enlazan cada síntoma con espacio, memoria ocupada o consumo observado; memoria ocupada no significa RAM rota. |

Se retiraron los hechos compuestos `s_no_enciende`, `s_lentitud_o_congelamientos` y `s_proceso_consumo_alto`. Un JSON técnico que los use se rechaza con una explicación de los nuevos IDs, pues convertirlos automáticamente inventaría observaciones. Los ejemplos incluidos no dependen de esos hechos.

Los diagnósticos añadidos son `d_revision_inicio_energia`, `d_indicios_termicos`, `d_red_compartida` y `d_enlace_cable`. Sus nombres y explicaciones mantienen abierta la causa física. Los demás diagnósticos siguen representando áreas de revisión; por ejemplo, `d_presion_memoria` no confirma una avería de RAM.

La corrección de coherencia I-01 a I-03 añadió seis hechos atómicos y cuatro reglas directas sin crear diagnósticos nuevos. `s_error_durante_uso` queda deliberadamente fuera de reglas causales: el cuestionario registra ese error y explica que no se identificó causa. La consola integra las reglas generales de energía como evidencia complementaria cuando la prueba sostenida de una segunda pantalla respalda una hipótesis más específica; el Modelo A conserva ambos resultados en su memoria.

## Límites

Las pruebas demuestran integridad, activación de reglas y alcanzabilidad dentro del cuestionario. No miden precisión en equipos reales. El Avance 1 conserva inferencia directa y no emplea aprendizaje automático, modelos B/C ni heurísticas de selección. Los 20 casos finales reservados y los 80 casos previstos no se usaron para ajustar reglas.
