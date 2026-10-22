# Cierre técnico de correcciones del Avance 1

> **Archivo histórico:** este cierre técnico antecede al rediseño de rutas. Su lista de 26 preguntas, hechos y reglas no describe el catálogo vigente; consultar `REDISENO_RUTAS_AVANCE_1.md` y `AVANCE_1.md`. El cierre académico del Avance 1 continúa pendiente.

**Fecha de verificación:** 17 de octubre de 2026. **Estado:** listo para validación manual; cierre académico y tag `avance-1` pendientes de autorización.

## Alcance realizado

Se corrigieron las ocho incidencias A-01 a A-08 del informe [AUDITORIA_RUTAS_AVANCE_1.md](AUDITORIA_RUTAS_AVANCE_1.md). Se conservaron la arquitectura de conocimiento, adquisición e inferencia, el motor de Modelo A, las 26 reglas con sus IDs y los 14 diagnósticos. Dos observaciones nuevas (`s_conexion_wifi_intentada`, `s_post_completado`) permiten distinguir enlaces y etapas de arranque sin introducir diagnósticos ni reglas adicionales.

| Incidencia | Causa original | Corrección | Prueba y resultado real |
| --- | --- | --- | --- |
| A-01 alta | Las preguntas de luces y ventilador requerían `s_no_enciende=verdadero`. | Su aplicabilidad admite desconocido explícito. | Auditoría de alimentación: `p01=?` conduce a `p02,p03`; pasó. |
| A-02 alta | El cambio a sistema tras `p17=Sí` omitía `p09`. | `p09` se ofrece también en sistema. | Escenario artefactos + error: `r_video_artefactos_error` activada; 26/26 reglas alcanzables; pasó. |
| A-03 alta | Se usaba Wi-Fi deshabilitado aun cuando fallaba Ethernet. | `p25` comprueba el enlace; `p20` y tres reglas exigen Wi-Fi intentado. | Recorridos completos Wi-Fi/cable y JSON técnico por cable: sin hipótesis Wi-Fi para cable; pasaron. |
| A-04 alta | `p16=No` se interpretaba como POST completado. | `p26` observa etapa alcanzada; una regla de arranque la exige; POST se pregunta antes que disco. | Reinicio POST con código RAM: RAM principal, sin arranque SO; pasó. |
| A-05 media | General terminaba tras dos respuestas desconocidas. | `p02/p03` se habilitan tras incertidumbre inicial. | General con `p01=?,p07=?`: siguiente `p02`; pasó. |
| A-06 media | Video pedía monitor externo antes de comprobar alimentación. | Se reordenaron `p02,p03` antes de `p08`. | Recorrido de video y retroceso comprueban orden; pasaron. |
| A-07 media | Validez JSON no garantizaba adquisición dinámica de hechos. | El test de testigos por regla se mantiene como puerta de calidad separada. | 26/26 reglas y 14/14 diagnósticos alcanzables; pasó. |
| A-08 baja | La consola mostraba IDs internos ante contradicción. | Muestra el texto de las preguntas. | Prueba de consola detectó contradicción, permitió volver y no imprimió `(p01, p02)`; pasó. |

Las cuatro reglas con condición adicional son `r_wifi_sin_red`, `r_wifi_otros_conectan`, `r_red_wifi_habilitado` y `r_so_no_inicia_unidad_presente`. Su consecuencia deliberada es que una entrada JSON que omita la conexión intentada o la etapa alcanzada ya no puede inferir esas hipótesis. El estado omitido sigue siendo `desconocido`; no se convirtió en `falso`. Los dos ejemplos JSON existentes no activaban estas cuatro reglas y conservan sus resultados.

## Evidencia reproducible

| Comando o recorrido | Resultado observado |
| --- | --- |
| `python validar_conocimiento.py` | Código 0: 26 hechos, 14 diagnósticos, 26 reglas, 26 preguntas, 7 categorías válidas. |
| `python -m unittest discover -s tests -v` | 31 pruebas, 0 fallos. |
| `python -m unittest discover -s auditoria -v` | 7 pruebas, 0 fallos; antes había 2 fallos reproducibles. |
| Auditoría de reglas | 185 comprobaciones directas; 26/26 reglas y 14/14 diagnósticos alcanzables por recorridos normales. |
| Exploración de bifurcaciones | 781 trayectorias terminales acotadas en las siete categorías; ninguna repetición o ciclo observado. |
| `python diagnosticar.py --respuestas ejemplos/ram.json` | Código 0; hipótesis RAM con `r_ram_reinicio_post` y `r_ram_codigo_post`. |
| `python diagnosticar.py --respuestas ejemplos/sin_conclusion.json` | Código 0; sin conclusión. |
| Consola interactiva, conectividad por cable | Código 0; `d_conectividad_local` por `r_red_otros_conectan`, sin preguntar por estado del Wi-Fi. |

Las pruebas verifican comportamiento lógico dentro de sus escenarios y exploración acotada. No sustituyen observación con usuarios, revisión de hardware real ni los 80 casos posteriores. La clasificación actual es **APROBADO CON OBSERVACIONES para validación manual**: no hay incidencia bloqueante reproducida dentro de la cobertura ejecutada. La validación y autorización de cierre corresponden al usuario. No se creó el tag `avance-1` ni se inició el Avance 2.
