# Auditoría integral de rutas y diagnósticos — Avance 1

> **Archivo histórico:** documenta la versión anterior de 26 preguntas, hechos y reglas. El rediseño aprobado la sustituyó. Para el grafo y las cantidades vigentes, consultar `REDISENO_RUTAS_AVANCE_1.md` y `AVANCE_1.md`. Las pruebas actuales de `auditoria/` verifican la versión rediseñada.

**Estado actual:** correcciones A-01 a A-08 verificadas; Avance 1 listo para validación manual, sin autorización de cierre ni tag. Las secciones 1–8 conservan la **línea base histórica previa a la corrección** (clasificación REQUIERE CORRECCIONES). El resultado vigente y las diferencias están en la sección 9. Las pruebas de `auditoria/` siguen separadas de los 80 casos previstos para el Avance 2.

## 1. Resumen ejecutivo y arquitectura examinada

El catálogo real contiene **7 categorías, 24 síntomas, 24 preguntas, 14 diagnósticos y 26 reglas**. `validar_conocimiento.py` acepta sus archivos. Las 31 pruebas de regresión pasan, pero la auditoría encuentra fallos de flujo y una atribución potencialmente errónea en conectividad. El cumplimiento estructural no garantiza que una regla pueda adquirir sus hechos desde la consola ni que su hipótesis sea adecuada para todos los casos.

La interfaz (`consola.py`) muestra preguntas de `data/interfaz/preguntas.json` y traduce Sí/No/No estoy seguro mediante `preguntas.py`. `rutas.json` y `gestor_preguntas.py` eligen preguntas según hechos de la sesión. `coherencia.py` bloquea cuatro combinaciones básicas incompatibles. `modelo_a.py` conserva el diagnóstico: normaliza hechos trivalentes, activa reglas directas, agrupa conclusiones y muestra reglas y condiciones. No se observó inferencia diagnóstica escrita en el gestor de preguntas. La selección del diagnóstico principal usa el máximo número de condiciones de una regla y luego el ID; es orden de presentación, no certeza.

## 2. Resultado por categoría

Los IDs remiten al texto y ayuda de [PREGUNTAS.md](PREGUNTAS.md). La tabla muestra **todas las preguntas configuradas para la ruta mientras permanece activa**; una reorientación automática puede añadir preguntas de otra ruta. El grafo cambia a alimentación al confirmar ausencia de señales, a video al confirmar ausencia de imagen y a sistema si no inicia el sistema operativo. Desde la ruta general puede pasar además a lentitud, conectividad o temperatura.

| Categoría | Preguntas configuradas y dependencias principales | Resultado de auditoría |
| --- | --- | --- |
| 1. No enciende | `p01,p02,p03`. `p02/p03` exigen `s_no_enciende=verdadero` o ausencia de imagen. | Con `p01=No`, verifica luces y ventilador y puede concluir ruta de alimentación. Con `p01=Sí`, reorienta. **Con `p01=No estoy seguro` termina tras una sola pregunta**, aunque `p02/p03` podrían aportar observaciones independientes. `p01` ya incluye luces/ventilador, de modo que `p02/p03` corroboran el mismo fenómeno y no son evidencia completamente independiente. |
| 2. Lenta o se congela | `p01,p07,p16,p21,p22,p23,p24,p13,p14,p15,p11,p05`. Imagen permite `p16`; sistema utilizable permite `p21,p13-p15`; lentitud confirmada habilita `p22-p24,p11,p05`. | Las tres reglas nuevas requieren lentitud más evidencia concreta y no confunden uso alto de memoria con RAM dañada. Si no hay evidencia específica, termina correctamente sin conclusión. Hace varias comprobaciones técnicas aun después de obtener una hipótesis; son pertinentes, aunque largas. Si faltan las respuestas iniciales de encendido/imagen, no intenta verificaciones sencillas adicionales. |
| 3. Enciende sin imagen | `p01,p07,p08,p02,p03,p04,p06,p05`. `p08` exige falta de imagen; `p02/p03` verifican energía; prueba externa positiva omite comprobaciones posteriores. | Pantalla externa positiva activa la hipótesis de pantalla principal en tres preguntas. Si no hay imagen en ambas, puede reunir evidencia para video o RAM. **Con `p01=No estoy seguro` y `p07=No`, pide la prueba externa antes de aclarar luces/ventiladores**, aunque quizá el equipo ni siquiera se energiza. Los artefactos visibles (`p09`) no pertenecen a esta ruta; solo aparecen si `p07=Sí` y se cambia a general. |
| 4. Sistema no inicia o muestra errores | `p01,p07,p16,p12,p10,p11,p17,p04,p06,p05`. Fallo de inicio habilita almacenamiento y POST; sistema utilizable habilita error crítico `p17`. | Arranque con unidad detectada y error crítico pueden generar hipótesis. **`p16=No` registra un hecho cuya definición afirma que POST terminó**, aunque el usuario puede responder No porque reinicia durante POST; en ese caso las preguntas `p04/p06` y una unidad detectada pueden producir hipótesis RAM y arranque, con arranque presentado primero. Un error azul durante el arranque tampoco llega a `p17`, que exige que el sistema ya esté utilizable. |
| 5. Se calienta o apaga | `p01,p07,p16,p14,p13,p15`. Las tres preguntas térmicas requieren inicio del sistema. | Exigir temperatura medida para concluir sobrecalentamiento es prudente. Un apagado o ventilador ruidoso sin medición no produce esa conclusión. Si la información inicial es desconocida, puede terminar sin investigar el síntoma seleccionado. |
| 6. Internet o Wi-Fi | `p01,p07,p16,p18,p19,p20`. Fallo de red habilita comparación con otros equipos y estado del Wi-Fi. | Puede generar dos hipótesis compatibles y explica ambas. **No pregunta si la conexión intentada es Wi-Fi o cable**: un usuario con problema de Ethernet y Wi-Fi desactivado puede recibir `d_wifi_inhabilitado` como hipótesis principal. La respuesta a `p18=Sí` devuelve la consulta a general. |
| 7. No estoy seguro | `p01,p07,p02,p03,p16,p21,p18,p14,p13,p17,p09`. Las posteriores requieren imagen o sistema utilizable; los hechos positivos redirigen a una ruta específica. | La clasificación por señales, imagen, inicio y síntomas funciona en recorridos con datos. Con `p01=?` y `p07=?` **termina sin preguntar por luces ni ventiladores**. `p02/p03` están listadas aquí, pero sus condiciones de activación ya provocan un cambio a alimentación o video, por lo que son pasos inalcanzables *dentro de general*. `p17=Sí` mueve a sistema antes de `p09` y bloquea la combinación de error crítico con artefactos. |

Todas las preguntas usan los estados previstos. Las seis polaridades invertidas son `p01,p07,p10,p16,p18,p20`; Sí se traduce a `falso` y No a `verdadero`. Las otras dieciocho traducen Sí a `verdadero` y No a `falso`. `?` y `3` quedan `desconocido`. No se observó una inversión accidental en el catálogo, pero la validez del mapeo depende de que la pregunta represente correctamente el hecho, como muestra el caso `p16`.

## 3. Escenarios y cobertura ejecutados

Se añadieron pruebas en `auditoria/test_auditoria_avance_1.py` para escenarios claros de alimentación y video; lentitud con dos hipótesis; datos incompletos; categoría equivocada; ausencia de evidencia; contradicción y corrección; retroceso; cambio de categoría; y pantalla externa compatible con pantalla principal sin imagen. Las pruebas principales existentes cubren además consola interactiva, alternativas, polaridad y ejemplos JSON.

Una exploración sistemática varió las tres respuestas posibles de **nueve preguntas que afectan bifurcaciones** (`p01,p07,p08,p16,p21,p18,p14,p13,p17`); las demás recibieron `desconocido`. Recorrió **701 trayectorias terminales**: alimentación 87, lentitud 119, video 171, sistema 19, temperatura 31, conectividad 103 y general 171. Ninguna de esas trayectorias repitió una pregunta, presentó contradicción inadvertida o excedió las 24 preguntas; la mayor tuvo 13. La unión de preguntas visitadas fue de 24 en varias categorías por reorientación, no porque se hicieran 24 en una sesión. Esta es una exploración acotada del grafo, **no** las `3^24` combinaciones ni una evaluación de precisión.

Trazas relevantes observadas:

| Escenario | Preguntas / hechos decisivos | Resultado |
| --- | --- | --- |
| Alimentación incierta | Categoría alimentación; `p01=?` | `siguiente()=None` después de una pregunta; sin hipótesis. |
| General incierto | `p01=?, p07=?` | Fin tras dos preguntas; luces y ventiladores no se consultan. |
| Pantalla externa | Video; `p01=Sí, p07=No, p08=Sí` | `r_pantalla_externa`; `d_pantalla_principal`. |
| Artefactos más error crítico | General; `p17=Sí` antes de `p09` | Cambia a sistema; `p09` no aparece; `r_video_artefactos_error` no se activa en el cuestionario normal. |
| Encendido incierto y sin imagen | Video; `p01=?, p07=No` | `p08` aparece antes de `p02/p03`; ninguno de esos tres hechos es todavía una señal confirmada de energía. |
| Red posiblemente cableada | Red; `p18=No, p19=Sí, p20=No` | `d_wifi_inhabilitado` principal y `d_conectividad_local` alternativa; no existe dato sobre tipo de conexión. |
| Reinicios durante POST | Sistema; `p16=No, p10=Sí, p04=Sí, p06=Sí` | `d_arranque_so` principal y `d_memoria_ram` alternativa; se usó `s_so_no_inicia` pese al reinicio durante POST. |

## 4. Análisis de las 26 reglas

El validador aprobó estructura, referencias y ausencia de condiciones contradictorias en las 26. La auditoría ejecutó **173 comprobaciones directas de inferencia**: un caso positivo por regla y, para cada una de sus 49 condiciones, la omitió, la convirtió en `desconocido` y le asignó el estado opuesto. Todas se activaron con sus condiciones completas y dejaron de activarse al faltar o cambiar una condición. Esto demuestra ejecución del motor, no pertinencia de la hipótesis ni alcanzabilidad desde preguntas.

En la tabla, **E** significa estructura y ejecución directa correctas para esa regla; **C** indica un testigo de consulta interactiva sin cambio manual de categoría. La columna final expresa el límite técnico principal.

| Regla | E | C | Evaluación técnica |
| --- | :---: | :---: | --- |
| `r_alimentacion_led` | Sí | Sí | Orienta a alimentación; `p01` y `p02` corroboran señales relacionadas. |
| `r_alimentacion_ventiladores` | Sí | Sí | Orienta a alimentación; no identifica fuente/placa. |
| `r_ram_codigo_post` | Sí | Sí | Exige código de memoria interpretado según manual. |
| `r_ram_prueba` | Sí | Sí | Requiere prueba de memoria con errores. |
| `r_ram_reinicio_post` | Sí | Sí | Añade reinicios al código POST; no debe confundirse con arranque del SO. |
| `r_pantalla_externa` | Sí | Sí | Buena localización de pantalla/trayecto, con otras causas aún posibles. |
| `r_video_artefactos` | Sí | Sí | Artefactos justifican revisar video, sin confirmar GPU. |
| `r_video_artefactos_error` | Sí | **No** | `p17=Sí` cambia a sistema antes de `p09`; sí se activa por JSON técnico. |
| `r_video_sin_salida` | Sí | Sí | Cuatro condiciones; sin salida en dos pantallas también admite causas POST/RAM. |
| `r_almacenamiento_firmware` | Sí | Sí | Unidad realmente ausente en firmware, no solo sistema operativo. |
| `r_almacenamiento_sin_arranque` | Sí | Sí | Refuerza la ausencia de unidad con mensaje de arranque. |
| `r_almacenamiento_errores_io` | Sí | Sí | Motiva proteger datos; unidad o enlace siguen sin aislar. |
| `r_almacenamiento_errores_arranque` | Sí | Sí | Refuerza errores de E/S con fallo de inicio. |
| `r_temperatura_medida` | Sí | Sí | Requiere medición anormal. |
| `r_temperatura_apagado` | Sí | Sí | Apagado solo refuerza medición; no prueba causa térmica. |
| `r_temperatura_ventilador` | Sí | Sí | Ruido solo refuerza medición; no prueba ventilador averiado. |
| `r_so_no_inicia_unidad_presente` | Sí | Sí | Alcanzable, pero `p16` puede registrar incorrectamente un fallo de POST como arranque del SO. |
| `r_so_mensaje_unidad_presente` | Sí | Sí | Mensaje de arranque y unidad detectada apoyan revisión de configuración. |
| `r_so_error_critico` | Sí | Sí | Clasifica el error sin atribuir causa; excluye errores durante el arranque en consola. |
| `r_wifi_sin_red` | Sí | Sí | **Puede atribuir problema de Ethernet a Wi-Fi deshabilitado**. |
| `r_wifi_otros_conectan` | Sí | Sí | Mismo riesgo; añade comparación con otros equipos. |
| `r_red_otros_conectan` | Sí | Sí | Localiza el problema en equipo/enlace, no en componente concreto. |
| `r_red_wifi_habilitado` | Sí | Sí | Wi-Fi habilitado puede ser irrelevante en una conexión por cable. |
| `r_lentitud_espacio` | Sí | Sí | Lentitud más aviso de poco espacio; causalidad queda por comprobar. |
| `r_lentitud_memoria` | Sí | Sí | Indica presión de memoria, no RAM dañada. |
| `r_lentitud_proceso` | Sí | Sí | Señala programa exigente, sin asumir malware. |

Ocho pares comparten diagnóstico y una regla contiene todas las condiciones de otra: `r_ram_codigo_post`/`r_ram_reinicio_post`; `r_video_artefactos`/`r_video_artefactos_error`; `r_almacenamiento_firmware`/`r_almacenamiento_sin_arranque`; `r_almacenamiento_errores_io`/`r_almacenamiento_errores_arranque`; `r_temperatura_medida`/`r_temperatura_apagado`; `r_temperatura_medida`/`r_temperatura_ventilador`; `r_wifi_sin_red`/`r_wifi_otros_conectan`; `r_red_otros_conectan`/`r_red_wifi_habilitado`. Son solapamientos de evidencia, no necesariamente reglas incorrectas; no deben contarse como probabilidades independientes.

## 5. Análisis de los 14 diagnósticos

**Todos los 14 tienen al menos una regla alcanzable desde el cuestionario** y una explicación con ID de regla y hechos verificados. Las recomendaciones están presentes y son, en términos generales, proporcionales a hipótesis de revisión. La tabla distingue las reservas específicas; «alcanzable» no significa «siempre acertado».

| Diagnóstico | Reglas que lo sustentan | Alcanzable | Evaluación de explicación y recomendaciones |
| --- | --- | :---: | --- |
| `d_ruta_alimentacion` | `r_alimentacion_led`, `r_alimentacion_ventiladores` | Sí | Revisar alimentación y conexiones es pertinente; no se confirma fuente averiada. |
| `d_memoria_ram` | `r_ram_codigo_post`, `r_ram_prueba`, `r_ram_reinicio_post` | Sí | Manual y prueba de memoria justifican revisión; no basta un pitido genérico. |
| `d_pantalla_principal` | `r_pantalla_externa` | Sí | Pantalla externa funcional justifica comprobar panel, brillo y trayecto. |
| `d_subsistema_video` | `r_video_artefactos`, `r_video_artefactos_error`, `r_video_sin_salida` | Sí | Mantiene posibilidades de cable, monitor, controlador o GPU; el refuerzo por error crítico no es adquirible en la consola. |
| `d_deteccion_almacenamiento` | `r_almacenamiento_firmware`, `r_almacenamiento_sin_arranque` | Sí | Unidad ausente en firmware motiva revisión y protección de datos. |
| `d_salud_almacenamiento` | `r_almacenamiento_errores_io`, `r_almacenamiento_errores_arranque` | Sí | Respaldar datos y revisar unidad/enlace es prudente. |
| `d_sobrecalentamiento` | `r_temperatura_medida`, `r_temperatura_apagado`, `r_temperatura_ventilador` | Sí | Medición requerida; no se atribuye apagado aislado a temperatura. |
| `d_arranque_so` | `r_so_no_inicia_unidad_presente`, `r_so_mensaje_unidad_presente` | Sí | Configuración/archivos son posibles, pero el mapeo `p16` permite priorizarlo ante reinicios POST. |
| `d_error_critico_so` | `r_so_error_critico` | Sí | Advierte que la causa sigue pendiente; no cubre bien error azul durante arranque. |
| `d_wifi_inhabilitado` | `r_wifi_sin_red`, `r_wifi_otros_conectan` | Sí | Habilitar Wi-Fi es útil **solo si esa era la conexión intentada**. |
| `d_conectividad_local` | `r_red_otros_conectan`, `r_red_wifi_habilitado` | Sí | Localiza pruebas en equipo/enlace sin adjudicar componente. |
| `d_espacio_insuficiente` | `r_lentitud_espacio` | Sí | Liberar espacio de forma segura es prueba reversible; no hay causalidad confirmada. |
| `d_presion_memoria` | `r_lentitud_memoria` | Sí | Distingue uso alto de RAM de avería física. |
| `d_proceso_exigente` | `r_lentitud_proceso` | Sí | Invita a identificar programa y tarea; no asume infección. |

## 6. Incidencias reproducibles

| ID / severidad | Componente | Problema | Pasos para reproducir | Esperado | Observado | Corrección recomendada |
| --- | --- | --- | --- | --- | --- | --- |
| A-01 / **alta** | Ruta alimentación | Fin prematuro con estado desconocido. | Elegir 1; responder `3` a `p01`. | Preguntar por luces/ventilador o una comprobación básica antes de concluir falta de datos. | `siguiente()` devuelve `None` tras una pregunta. | Permitir `p02/p03` cuando `p01` es desconocido; verificar que no se infiere falsedad. |
| A-02 / **alta** | Rutas general/sistema/video | `r_video_artefactos_error` inaccesible por cuestionario normal. | Elegir 7; confirmar imagen y sistema utilizable; responder Sí al error crítico `p17`. | Poder registrar también artefactos `p09` si son observables. | Salta a sistema y nunca presenta `p09`. | Permitir completar evidencia transversal sin depender de un orden que la excluye; añadir test de alcanzabilidad por regla. |
| A-03 / **alta** | Conectividad | Hipótesis Wi-Fi puede ser ajena a conexión por cable. | Elegir 6; indicar fallo de red, otros equipos conectan y Wi-Fi desactivado mientras se intenta usar Ethernet. | Preguntar tipo de enlace y evitar atribución Wi-Fi si no se usa. | `d_wifi_inhabilitado` aparece como principal. | Adquirir explícitamente tipo de conexión y condicionar la ruta o regla al enlace intentado. |
| A-04 / **alta** | Pregunta `p16`, hecho `s_so_no_inicia`, orden de Modelo A | Un reinicio durante POST puede registrarse como fallo tras POST. | Elegir 4; `p16=No`, unidad detectada, código RAM y reinicios antes de Windows. | Distinguir etapa POST de etapa de arranque del SO y no priorizar archivos de arranque sin esa distinción. | `d_arranque_so` principal, `d_memoria_ram` alternativa. | Separar/precisar hechos de etapa de arranque y revisar la adquisición de `p16`; probar el orden de hipótesis con evidencia específica. |
| A-05 / **media** | Ruta general | Fin prematuro con dos respuestas desconocidas. | Elegir 7; `p01=?`, `p07=?`. | Ofrecer comprobaciones simples de energía u otro triaje seguro. | Termina sin `p02/p03` ni otra pregunta. | Permitir preguntas independientes con requisitos de conocimiento desconocido. |
| A-06 / **media** | Ruta video | Prueba externa antes de aclarar energía. | Elegir 3; `p01=?`, `p07=No`. | Aclarar señales básicas de encendido antes de pedir otra pantalla. | Pregunta `p08` antes de `p02/p03`. | Reordenar o condicionar la prueba externa a energía confirmada. |
| A-07 / **media** | Validador de rutas | Validez sintáctica no detecta reglas inaccesibles por cambios de categoría. | Ejecutar validador y luego el test de alcanzabilidad de auditoría. | Informe separado de integridad y alcanzabilidad dinámica. | Validador aprueba siete rutas pese a A-02. | Incorporar comprobación de testigos de adquisición en controles de calidad, sin confundirla con validación JSON. |
| A-08 / **baja** | Consola | Muestra IDs internos al explicar contradicciones. | Elegir 1; `p01=No`, `p02=Sí`. | Identificar las dos respuestas por texto comprensible. | Muestra `(p01, p02)`. | Presentar resúmenes visibles de preguntas, dejando IDs para registros técnicos. |

La comprobación de coherencia detectó `s_no_enciende=verdadero` con luz encendida y permitió corregir la última respuesta. No bloqueó la combinación compatible «sin imagen principal» + «imagen en monitor externo». Solo cubre cuatro pares definidos; no prueba que todas las contradicciones semánticas estén contempladas. La permanencia de un diagnóstico alternativo no debe confundirse con confirmación de dos fallas simultáneas.

## 7. Comandos y resultados reales

| Comando | Resultado observado |
| --- | --- |
| `python validar_conocimiento.py` | Código 0; 24 hechos, 14 diagnósticos, 26 reglas, 24 preguntas y 7 categorías válidas. |
| `python -m unittest discover -s tests -v` | **31 pruebas, 0 fallos**. |
| `python -m unittest discover -s auditoria -v` | **7 pruebas de auditoría; 2 fallos** esperados como evidencia de A-01 y A-02; el chequeo de las 26 reglas directas, diagnósticos, escenarios y exploración acotada pasó. |
| `python diagnosticar.py --respuestas ejemplos/ram.json` | Código 0; hipótesis RAM, `r_ram_reinicio_post` y `r_ram_codigo_post`, hechos y recomendaciones. |
| `python diagnosticar.py --respuestas ejemplos/sin_conclusion.json` | Código 0; sin conclusión y mensaje de evidencia insuficiente. |

Se usó `PYTHONDONTWRITEBYTECODE=1` en las verificaciones de auditoría. El modo JSON puede activar la regla A-02 porque acepta hechos internos directamente; eso no demuestra que el cuestionario pueda reunirlos. Las 173 comprobaciones de motor, los 25 testigos de reglas interactivas y las 701 trayectorias acotadas son **pruebas de software**, no métricas diagnósticas ni los casos de evaluación reservados.

## 8. Limitaciones, acciones y decisión de cierre

No se probaron todas las combinaciones de 24 respuestas, hardware real, intermitencias entre intentos ni exactitud estadística. Los testigos de reglas son recorridos representativos sin cambios manuales de categoría; la inaccesibilidad de `r_video_artefactos_error` se corrobora por el orden `p17` antes de `p09`, el cambio automático a sistema y la ausencia de `p09` en esa ruta. Las recomendaciones técnicas se revisaron contra las condiciones declaradas, no contra una muestra clínica o de laboratorio.

Antes de cerrar el Avance 1 conviene corregir A-01 a A-04 y repetir la suite de regresión y la auditoría. A-05 a A-08 pueden resolverse en la misma revisión para mejorar el triaje y la explicación. No se deben cambiar expectativas de pruebas para ocultar fallos ni alterar los 20 casos finales reservados cuando existan. **La clasificación es REQUIERE CORRECCIONES; el tag `avance-1` y el cierre permanecen pendientes de autorización posterior.**

## 9. Revisión posterior a las correcciones autorizadas (resultado vigente)

La línea base anterior se conserva para hacer reproducibles los problemas originales. El catálogo vigente tiene **7 categorías, 26 síntomas, 26 preguntas, 14 diagnósticos y 26 reglas**. Se añadieron únicamente `s_conexion_wifi_intentada`/`p25` y `s_post_completado`/`p26`; ningún diagnóstico o regla nueva. El motor y el criterio de orden de Modelo A permanecen iguales. Cuatro reglas existentes ganaron una condición: `r_wifi_sin_red`, `r_wifi_otros_conectan` y `r_red_wifi_habilitado` exigen Wi-Fi como enlace intentado; `r_so_no_inicia_unidad_presente` exige que se alcanzó la etapa de arranque del sistema. Por eso, entradas JSON antiguas que omitan esos hechos **ya no activan esas cuatro reglas**. Los dos ejemplos distribuidos no dependen de ellas y mantienen sus resultados.

### 9.1 Incidencias: causa, cambio y comprobación

| ID | Problema original y causa | Corrección implementada | Prueba y resultado observado |
| --- | --- | --- | --- |
| A-01 alta | `p01=?` cerraba alimentación porque `p02/p03` exigían una observación afirmativa. | La aplicabilidad admite explícitamente `s_no_enciende=desconocido` para pedir luces y ventilador; ninguna regla diagnóstica interpreta ese estado como falso. | `test_no_enciende_desconocido_pide_otra_comprobacion`: tras `p01=?` aparece `p02` y luego `p03`; pasa. |
| A-02 alta | `p17=Sí` cambiaba a sistema y ocultaba `p09`, dejando inaccesible `r_video_artefactos_error`. | `p09` también figura en la ruta sistema después de `p17`; se permite registrar el síntoma visual después del cambio automático. | `test_escenarios_completos_representativos` comprueba `p09` y activación de `r_video_artefactos_error`; `test_cada_regla_es_alcanzable_en_cuestionario_normal` confirma 26/26; pasan. |
| A-03 alta | No se conocía si el enlace fallido era Wi-Fi o cable; `p20` y tres reglas Wi-Fi podían atribuir Ethernet al adaptador inalámbrico. | `p25` identifica el enlace; `p20` solo se pregunta si se intenta Wi-Fi; tres reglas exigen ese hecho verdadero. | Escenarios Wi-Fi y cable completos, más evaluación directa con cable y Wi-Fi desactivado: cable produce `d_conectividad_local`, no `d_wifi_inhabilitado`; pasan. |
| A-04 alta | La definición de `s_so_no_inicia` suponía POST completado aunque `p16=No` también cubría reinicios durante POST. | Definición corregida; `p06` precisa reinicio antes del logotipo del sistema; `p26` comprueba etapa alcanzada; la regla de arranque exige ese hecho; el flujo pregunta POST antes de disco y omite preguntas de arranque incompatibles con reinicio POST confirmado. Se añadió la contradicción explícita entre reinicio antes del sistema y haberlo mostrado en el mismo intento. | Escenario de reinicio POST con código RAM: `d_memoria_ram` principal, sin `d_arranque_so`; prueba de regla con `s_post_completado=desconocido` no se activa; pasan. |
| A-05 media | General con `p01=?,p07=?` terminaba antes de comprobar energía; misma restricción que A-01. | `p02/p03` pueden formularse pese a incertidumbre inicial. | `test_no_enciende_desconocido_pide_otra_comprobacion`: en general la siguiente es `p02`; pasa. |
| A-06 media | Video pedía otra pantalla antes de comprobar señales básicas de energía. | Orden de video cambiado a `p01,p07,p02,p03,p08,...`. | Pruebas de ruta externa y retroceso exigen el nuevo orden; pasan. La prueba externa positiva sigue concluyendo `d_pantalla_principal`. |
| A-07 media | La validación JSON no detectaba inaccesibilidad causada por cambios dinámicos de ruta. | La suite separada de auditoría mantiene un testigo interactivo por cada regla como control de calidad obligatorio; el validador sigue encargado de integridad estática. | `test_cada_regla_es_alcanzable_en_cuestionario_normal`: 26/26 reglas, 14/14 diagnósticos; pasa. |
| A-08 baja | La consola mostraba `(p01, p02)` en una contradicción. | Muestra los textos de las preguntas afectadas, sin IDs internos. | `test_consola_vuelve_ante_contradiccion_y_conserva_polaridad`: contradicción visible, corrección exitosa y ausencia de `(p01, p02)`; pasa. |

### 9.2 Siete categorías, rutas y cobertura vigente

| Categoría inicial | Preguntas configuradas en orden | Comportamiento comprobado |
| --- | --- | --- |
| Alimentación | `p01,p02,p03` | `p01=?` ya conduce a las dos comprobaciones simples; una contradicción de señales se detiene hasta corregirse. |
| Lentitud | `p01,p07,p16,p21,p22,p23,p24,p13,p14,p15,p11,p05` | Lentitud sin evidencia específica termina sin hipótesis; espacio, memoria ocupada o proceso exigente producen hipótesis distintas. |
| Video | `p01,p07,p02,p03,p08,p04,p06,p05` | Señales de energía preceden prueba externa; la imagen en otra pantalla conserva la hipótesis de pantalla principal. |
| Sistema | `p01,p07,p16,p06,p04,p26,p12,p10,p11,p17,p09,p05` | Se diferencia reinicio POST de arranque del sistema; el error crítico puede observarse al iniciar y coexistir con artefactos. |
| Temperatura | `p01,p07,p16,p14,p13,p15` | Una medición alta sigue siendo requisito para concluir sobrecalentamiento. |
| Conectividad | `p01,p07,p16,p18,p25,p19,p20` | El tipo de enlace precede la pregunta sobre Wi-Fi; si es cable, `p20` no aparece. |
| General | `p01,p07,p02,p03,p16,p21,p18,p14,p13,p17,p09` | Con `p01=?,p07=?` se consultan señales de energía; los cambios de categoría mantienen las respuestas previas. |

Los 26 identificadores de regla se evaluaron con sus 53 condiciones: **185 comprobaciones directas** (26 activaciones y, por cada condición, omisión, desconocido y estado contrario), todas correctas. Los testigos interactivos alcanzaron **26/26 reglas** y **14/14 diagnósticos**. La exploración acotada varió las tres respuestas en 11 bifurcaciones y registró **781 trayectorias terminales**: alimentación 95, lentitud 131, video 187, sistema 27, temperatura 39, conectividad 115, general 187. No observó ciclos ni repeticiones; máximo 13 preguntas en una trayectoria. Las siete categorías también tienen recorridos completos representativos en la suite, con casos ambiguos, incompletos, categoría equivocada, retroceso, cambio de categoría y contradicción.

### 9.3 Verificación, límites y decisión

| Ejecución posterior a la corrección | Resultado real |
| --- | --- |
| `python validar_conocimiento.py` | Código 0; 26 hechos, 14 diagnósticos, 26 reglas, 26 preguntas, 7 categorías. |
| `python -m unittest discover -s tests -v` | 31 pruebas, 0 fallos. |
| `python -m unittest discover -s auditoria -v` | 7 pruebas, 0 fallos; las dos fallidas de la línea base ahora pasan. |
| `python diagnosticar.py --respuestas ejemplos/ram.json` | Código 0; RAM, `r_ram_reinicio_post` y `r_ram_codigo_post`. |
| `python diagnosticar.py --respuestas ejemplos/sin_conclusion.json` | Código 0; sin conclusión. |
| Consulta de consola por cable | Código 0; `d_conectividad_local` sin hipótesis Wi-Fi. |

La cobertura es de pruebas de software y testigos construidos, no precisión en equipos reales ni exploración de `3^26` combinaciones. La validación manual de lenguaje, casos intermitentes y hardware real sigue pendiente. **Decisión vigente: APROBADO CON OBSERVACIONES para validación manual**, sin incidencia bloqueante reproducida dentro de esta cobertura. No se autoriza por ello el cierre, el tag `avance-1` ni el Avance 2.
