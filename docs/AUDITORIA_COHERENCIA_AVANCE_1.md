# Auditoría de coherencia del cuestionario — Avance 1

**Estado vigente: I-01, I-02, I-03 y O-01 corregidas técnicamente; pendiente de revisión manual.** Las secciones 1–8 conservan la línea base de la auditoría anterior, cuyo veredicto fue **REQUIERE CORRECCIONES**. La sección 9 registra los cambios autorizados, recorridos posteriores y verificaciones. El cierre del Avance 1 no está autorizado.

## 1. Resumen ejecutivo

El inventario real es de **7 categorías, 30 hechos de tipo síntoma, 30 preguntas, 38 reglas directas y 18 diagnósticos**. El grafo selecciona preguntas; `GestorPreguntas` transforma respuestas en hechos trivalentes; `ModeloA` activa las reglas y produce hipótesis. Las seis rutas específicas se exploraron con las tres respuestas en cada pregunta alcanzable: **2.776 trayectorias terminales**. Se agregaron **361 trayectorias acotadas** de la ruta general: **3.137 en total**. Ninguna de las trayectorias exploradas presentó ciclos, preguntas repetidas, cambio automático de categoría o una regla activada por una condición omitida/desconocida.

La cobertura de ejecución no demuestra adecuación semántica. En video, una imagen breve de inicio conduce a un bloqueo que afirma que ya aparece imagen. En conectividad, abrir una página en ese instante cierra la consulta pese a posibles fallas parciales o intermitentes. En sistema operativo, tres respuestas negativas cierran una consulta por errores distintos de pantalla azul y errores de acceso a archivos. Son casos contemplados por los nombres de las categorías y no investigados por las preguntas actuales.

## 2. Arquitectura y alcance comprobados

| Capa | Archivos | Papel observado |
| --- | --- | --- |
| Conocimiento | `data/conocimiento/{hechos,reglas,diagnosticos}.json` | 30 hechos, 38 reglas SI–ENTONCES, 18 hipótesis y recomendaciones. |
| Preguntas y rutas | `data/interfaz/{preguntas,rutas}.json` | Mapeos explícitos Sí/No/No estoy seguro y siete grafos con destinos condicionados. |
| Adquisición | `src/diagnostico_pc/{rutas,gestor_preguntas,coherencia}.py` | Valida el grafo, conserva la categoría y reconstruye hechos del historial; dos incompatibilidades explícitas. |
| Inferencia | `src/diagnostico_pc/modelo_a.py` | Único componente que activa reglas y ordena hipótesis por especificidad, sin estimar probabilidades. |
| Interfaz | `src/diagnostico_pc/consola.py` | Ofrece 1/2/3 y s/n/?, edición, retroceso, finalización y confirmación de cambio de categoría. |

`p07`, `p10`, `p16`, `p18` y `p20` tienen polaridad invertida deliberada: contestar Sí registra como falso el síntoma negativo correspondiente. Se verificó en particular `p10`: Sí a «aparece la unidad» ⇒ `s_unidad_no_detectada=falso`; No ⇒ `verdadero`; duda ⇒ `desconocido`. El validador cubre referencias, tres salidas y ausencia de ciclos. No demuestra que el alcance temporal de una pregunta coincida con el problema del usuario.

La consola confirma el cambio de categoría y reinicia el historial; `GestorPreguntas.cambiar_categoria` es una operación interna sin confirmación propia. Editar elimina la respuesta elegida y las posteriores, de modo que los hechos se reconstruyen. Cuando se elige video pero no hay luces ni ventiladores, la consola termina en `@bloqueo_energia` y **no muestra** la hipótesis de alimentación calculable a partir de los hechos; ofrece iniciar otra consulta. No se observó inferencia desde el grafo.

## 3. Las siete rutas

| Ruta y objetivo | Primera pregunta | Ramas Sí / No / duda y evaluación contextual | Trayectorias |
| --- | --- | --- | ---: |
| **Alimentación**: distinguir falta total de señales de energía presente sin inicio útil. | `p02`, luz del equipo. | Las tres llevan a `p03`. Dos negaciones dan hipótesis de alimentación; una señal positiva lleva a `p07` y, si hay imagen, a `p16`. La duda no se trata como negación. Las cuatro preguntas son pertinentes. | 29 |
| **Lentitud/congelamiento**: distinguir almacenamiento lleno, presión de memoria, proceso exigente y errores de unidad/RAM. | `p21`, apertura lenta de programas. | `p27` complementa congelamientos; si ambos son negativos o dudosos, se cierra. Si existe uno de los síntomas, `p22`–`p28` comprueban causas diferenciables; `p11`/`p05` aparecen solo cuando pueden aportar otra causa. No se observó repetición; varias comprobaciones técnicas se resuelven con duda. | 1.975 |
| **Video**: investigar imagen principal, monitor externo y señales de POST/RAM. | `p07`, cualquier imagen al encender. | Sí lleva a `p09`; No o duda revisan energía y eventualmente monitor externo, pitidos y prueba RAM. El caso de imagen solo transitoria queda mal clasificado (I-01). | 231 |
| **Sistema**: separar POST, detección de unidad, arranque y errores del sistema. | `p16`, sistema utilizable. | No lleva a comprobaciones POST/firmware; Sí lleva a pantalla azul y error de acceso a archivos. `p10` conserva la polaridad correcta. Los errores de otra clase quedan sin investigación (I-03). | 435 |
| **Temperatura/apagado**: separar medición alta de indicios observables. | `p30`, calor percibido. | `p14` y `p15` exploran apagado y ventilación; `p13` exige medición para la hipótesis de temperatura alta. Los indicios solos producen una hipótesis distinta. Una duda sobre medición no se transforma en medición alta. | 65 |
| **Conectividad**: diferenciar Wi-Fi, cable, falla local o red compartida. | `p18`, abrir una página ahora. | No lleva a tipo de enlace y comparación con otro dispositivo; Sí o duda cierran. Sí puede ocultar una falla parcial o intermitente (I-02). | 41 |
| **General**: orientarse sin categoría conocida. | `p02`, señales de energía. | Reutiliza preguntas de ramas pertinentes según observaciones, sin cambiar el identificador `general`. Se muestrearon tres respuestas en nueve nodos de bifurcación y duda en los demás; no es enumeración exhaustiva. | 361 |

Las ayudas de las 30 preguntas se inspeccionaron: definen términos como POST mediante una observación de inicio, explican pruebas y ofrecen «No estoy seguro» cuando la medición o comprobación no se hizo. Cada pregunta codifica un hecho observable; no se encontró una pregunta que exija simultáneamente dos fallas independientes. `p07` presenta una **ambigüedad temporal**, no dos hechos combinados. Una pregunta compartida entre rutas es pertinente cuando el trayecto necesita esa observación (por ejemplo, `p11` en lentitud y sistema). El problema principal es la cobertura de situaciones incluidas en los títulos amplios de tres categorías.

## 4. Cobertura de trayectorias y perfiles

| Ruta | Terminales `@resultado` | `@insuficiente` | Bloqueos | Máximo de preguntas | Preguntas observadas |
| --- | ---: | ---: | ---: | ---: | ---: |
| Alimentación | 6 | 18 | 5 sistema | 4 | 4/4 |
| Lentitud | 1.971 | 4 | 0 | 8 | 8/8 |
| Video | 216 | 11 | 2 imagen, 2 energía | 7 | 8/8 |
| Sistema | 433 | 2 | 0 | 8 | 10/10 |
| Temperatura | 57 | 8 | 0 | 4 | 4/4 |
| Conectividad | 39 | 2 | 0 | 5 | 6/6 |
| General, muestra | 350 | 11 | 0 | 12 | 28/30 |

Las cifras cuentan secuencias de respuestas, incluso cuando varias llevan al mismo terminal. La exploración de seis rutas específicas fue exhaustiva respecto de las tres opciones en **cada pregunta efectivamente visitada**. En la general se usaron como pivotes `p02,p03,p07,p16,p21,p27,p18,p25,p30`, con duda en las restantes. No se enumeraron las `3^30` combinaciones globales. La unión de las seis rutas específicas activó las **38 reglas y los 18 diagnósticos** en el cálculo bruto del Modelo A; la prueba de testigos existente comprobó también cada uno por cuestionario. Esto incluye `d_ruta_alimentacion` en un recorrido equivocado de video, que la consola bloquea como se explica arriba. La alcanzabilidad del motor no implica que toda salida sea adecuada para cada usuario.

Se ejecutaron los siguientes perfiles con respuestas reales al `GestorPreguntas` o a la consola:

| Perfil | Recorrido observado | Resultado |
| --- | --- | --- |
| Muy poca experiencia, todas las respuestas dudosas | Video: `p07=?, p02=?, p03=?` | `@insuficiente`, sin hipótesis. |
| Síntomas básicos | Video: `p07=No,p02=Sí,p03=Sí,p08=Sí` | Pantalla principal y revisión general de inicio como alternativa. |
| Sin medición técnica | Temperatura: `p30=Sí,p14=Sí,p15=?,p13=?` | Solo indicios térmicos. |
| Categoría correcta | Conectividad: `p18=No,p25=Sí,p20=No,p19=Sí` | Wi-Fi inhabilitado y conectividad local como alternativa. |
| Categoría equivocada | Video: `p07=No,p02=No,p03=No` | `@bloqueo_energia`; la interfaz no presenta diagnóstico de otra categoría. |
| Respuesta parcial | Sistema: `p16=No`, luego `f` | Termina sin conclusión; el resto permanece desconocido. |
| Corrección y cambio confirmado | Pruebas existentes de consola y gestor: edición en conectividad, cambio cancelado y confirmado a video | La edición borra hechos dependientes; el cambio cancelado conserva y el confirmado reinicia. |
| Síntomas de varias causas | Lentitud: `p21,p27,p22,p23,p24,p28,p11=Sí` | Cuatro hipótesis compatibles: espacio, memoria, proceso y salud de almacenamiento. |

## 5. Revisión de reglas y diagnósticos

Los identificadores de preguntas siguientes son la procedencia de cada condición; `v` y `f` son los estados requeridos, **no** botones de respuesta. Esta tabla incluye las **38 reglas** y los **18 diagnósticos**. Para cada condición se comprobó en la auditoría previa y en la suite actual que omitirla, sustituirla por desconocido o invertirla impide activar esa regla. Cada regla posee un testigo alcanzable mediante cuestionario. Las explicaciones de diagnóstico se leyeron frente a esas condiciones y las recomendaciones son comprobaciones, no sustituciones de piezas basadas solo en un síntoma.

| Diagnóstico | Reglas y condiciones observables | Juicio |
| --- | --- | --- |
| `d_ruta_alimentacion` | `r_alimentacion_sin_senales` (`p02=f,p03=f`) | Hipótesis proporcional; consola la oculta si el usuario sigue en video. |
| `d_memoria_ram` | `r_ram_codigo_post` (`p04=v`); `r_ram_prueba` (`p05=v`); `r_ram_reinicio_post` (`p06=v,p04=v`) | Pitidos interpretados por manual o prueba; no presupone avería confirmada. |
| `d_pantalla_principal` | `r_pantalla_externa` (`p07=v,p08=v`) | Segunda pantalla aporta contraste; pertinente. |
| `d_subsistema_video` | `r_video_artefactos` (`p09=v`); `r_video_artefactos_error` (`p09=v,p17=v`); `r_video_sin_salida` (`p07=v,p08=f,p02=v,p03=v`) | Orienta a pruebas diferenciales; no asegura GPU averiada. |
| `d_deteccion_almacenamiento` | `r_almacenamiento_firmware` (`p10=v`); `r_almacenamiento_sin_arranque` (`p10=v,p12=v`) | `p10=No` satisface el hecho positivo; confirmado el mapeo. |
| `d_salud_almacenamiento` | `r_almacenamiento_errores_io` (`p11=v`); `r_almacenamiento_errores_arranque` (`p11=v,p16=v`) | Errores observables, causa abierta. |
| `d_sobrecalentamiento` | `r_temperatura_medida` (`p13=v`); `r_temperatura_apagado` (`p13=v,p14=v`); `r_temperatura_ventilador` (`p13=v,p15=v`) | Requiere medición frente a límite conocido. |
| `d_arranque_so` | `r_so_no_inicia_unidad_presente` (`p16=v,p26=v,p10=f`); `r_so_mensaje_unidad_presente` (`p12=v,p10=f`) | Incluye prueba de etapa posterior a POST o mensaje de arranque y unidad presente. |
| `d_error_critico_so` | `r_so_error_critico` (`p17=v`) | Causa pendiente; no atribuye origen concreto a pantalla azul. |
| `d_wifi_inhabilitado` | `r_wifi_sin_red` (`p18=v,p25=v,p20=v`); `r_wifi_otros_conectan` (+`p19=v`) | `p20=No` activa el síntoma de Wi-Fi deshabilitado. |
| `d_conectividad_local` | `r_red_otros_conectan` (`p18=v,p19=v`); `r_red_wifi_habilitado` (+`p25=v,p20=f`) | Comparación útil; origen aún sin identificar. |
| `d_espacio_insuficiente` | `r_lentitud_espacio` (`p21=v,p22=v`); `r_congelamiento_espacio` (`p27=v,p22=v`) | Aviso explícito de espacio. |
| `d_presion_memoria` | `r_lentitud_memoria` (`p21=v,p23=v`); `r_congelamiento_memoria` (`p27=v,p23=v`) | Uso alto de memoria; no se confunde con RAM dañada. |
| `d_proceso_exigente` | `r_lentitud_cpu` (`p21=v,p24=v`); `r_lentitud_disco` (`p21=v,p28=v`); `r_congelamiento_cpu` (`p27=v,p24=v`); `r_congelamiento_disco` (`p27=v,p28=v`) | Requiere proceso observado durante el problema. |
| `d_revision_inicio_energia` | `r_inicio_energia_luz` (`p02=v,p07=v`); `r_inicio_energia_ventilador` (`p03=v,p07=v`); `r_inicio_so_luz` (`p02=v,p07=f,p16=v`); `r_inicio_so_ventilador` (`p03=v,p07=f,p16=v`) | Hipótesis general válida, pero puede ser una alternativa poco informativa tras una prueba de monitor externo positiva. |
| `d_indicios_termicos` | `r_indicios_termicos_ventilador` (`p30=v,p15=v`); `r_indicios_termicos_apagado` (`p30=v,p14=v`) | Se declara explícitamente como indicio, no medición. |
| `d_red_compartida` | `r_red_compartida` (`p18=v,p19=f`) | Compara dos equipos; no presume fallo del proveedor. |
| `d_enlace_cable` | `r_red_cable_desconectado` (`p18=v,p29=v,p31=v`) | El aviso de cable apoya revisar enlace físico. |

Las reglas de video o RAM pueden aparecer como hipótesis alternativas en la ruta sistema cuando el usuario confirmó artefactos o código POST. Esa diferencia de categoría es explicable por hechos adicionales; no se detectó una asignación automática de la ruta. La salida bruta del motor sobre la ruta equivocada de video también puede inferir alimentación, pero la interfaz la bloquea como se indicó.

## 6. Incidencias reproducibles

### I-01 — Alta — Imagen transitoria interpretada como imagen actual

- **Situación:** la pantalla muestra el logotipo inicial y después queda negra; el usuario elige «Mi computadora enciende, pero no muestra imagen».
- **Recorrido exacto:** categoría 3 (video), `p07=1` (Sí, vio el logotipo), `p09=2` (No, no hay distorsiones persistentes), Enter para terminar. La prueba de caracterización obtiene preguntas `[p07,p09]`, terminal `@bloqueo_imagen` y ningún diagnóstico.
- **Pregunta problemática:** `p07` pregunta si hubo *alguna* imagen al encender y su ayuda cuenta el logotipo. No comprueba si la imagen permanece cuando ocurre el problema.
- **Esperado:** distinguir imagen estable de imagen únicamente transitoria, o indicar que no hay evidencia suficiente sin afirmar que «ahora aparece imagen».
- **Observado:** el terminal muestra «Ahora aparece imagen y no se observó una distorsión» y ofrece otra categoría. La afirmación temporal no se deduce de las respuestas.
- **Corrección propuesta:** acotar temporalmente la pregunta o agregar una observación específica sobre cuándo desaparece la imagen y conectar esa respuesta con video/arranque. Mantener cada pregunta en un solo hecho y revisar las reglas afectadas antes de cambiar el grafo.

### I-02 — Media — Una página accesible cierra un problema de conectividad

- **Situación:** la conexión se corta a ratos o falla una aplicación/sitio, pero la página de prueba abre en ese momento.
- **Recorrido exacto:** categoría 6 (conectividad), `p18=1` (Sí), Enter. Se visita solo `[p18]`, terminal `@insuficiente`, sin hipótesis.
- **Pregunta problemática:** `p18` delimita «ahora» y una sola página; su resultado no equivale a ausencia de todo problema de Internet o Wi-Fi.
- **Esperado:** continuar solo con observaciones pertinentes a intermitencia o alcance parcial, o declarar explícitamente que la ruta actual cubre pérdida total de acceso web.
- **Observado:** el cuestionario se cierra sin preguntar si el fallo es intermitente o afecta otro servicio. `@insuficiente` atribuye el cierre a falta de observaciones, no al alcance restringido.
- **Corrección propuesta:** delimitar la categoría o agregar una pregunta concreta sobre el fallo que motivó la selección; evitar diagnosticar una causa a partir de una sola página funcional.

### I-03 — Media — Errores de sistema distintos de pantalla azul y acceso a archivos

- **Situación:** el sistema inicia y se puede usar, pero presenta errores reproducibles de otro tipo; el usuario eligió la categoría que explícitamente dice «o presenta errores».
- **Recorrido exacto:** categoría 4 (sistema), `p16=1` (Sí inicia), `p17=2` (No hay pantalla azul), `p11=2` (No hay error de acceso a archivos), Enter. Preguntas `[p16,p17,p11]`, terminal `@resultado`, sin hipótesis.
- **Pregunta problemática:** tras `p17` y `p11` negativos no se pregunta qué otro error observable motivó la consulta.
- **Esperado:** señalar el alcance de las comprobaciones o recoger un hecho específico útil antes de declarar completada la ruta; no inventar un diagnóstico para errores sin evidencia.
- **Observado:** «Se completaron las comprobaciones útiles de esta ruta» pese a que el problema elegido sigue sin caracterizar.
- **Corrección propuesta:** distinguir en la entrada errores de inicio y errores durante el uso, o agregar observaciones atómicas y reglas proporcionadas. Si no se amplía el conocimiento en Avance 1, ofrecer un cierre que explique qué tipos de error cubre la ruta.

**Observación menor O-01:** `p07=No,p02=Sí,p03=Sí,p08=Sí` en video activa `d_pantalla_principal` y también `d_revision_inicio_energia`. La segunda hipótesis está respaldada por ausencia de imagen en la pantalla principal y energía presente, pero aporta poca diferenciación después de que otra pantalla sí funciona. Revisar su orden o presentación en una corrección autorizada; no se considera activación injustificada.

## 7. Pruebas ejecutadas

| Comando | Resultado observado |
| --- | --- |
| `python validar_conocimiento.py` | Correcto: 30 hechos, 18 diagnósticos, 38 reglas; 30 preguntas y 7 rutas válidas. |
| `python -m unittest discover -s tests -v` | 31 pruebas, todas correctas. |
| `python -m unittest discover -s auditoria -v` | 10 pruebas, todas correctas. Incluye la nueva exploración y pruebas de caracterización de I-01 a I-03. |

Las pruebas de caracterización verifican el **comportamiento observado** de cierres cuestionables; su éxito no equivale a aceptación semántica. Se inspeccionaron además las preguntas, las 38 condiciones de reglas, las 18 descripciones y recomendaciones, las salidas de la consola y los perfiles indicados. No se crearon casos del Avance 2.

## 8. Recomendaciones, límites y veredicto

1. Resolver I-01 antes del cierre: su mensaje final contradice una situación posible bajo la propia ayuda de `p07`.
2. Precisar el alcance de conectividad y errores de sistema o ampliar sus observaciones atómicas; en ambos casos asegurar que el cierre describa la evidencia realmente obtenida.
3. Volver a ejecutar validador, suites y recorridos personales tras cualquier corrección autorizada; verificar que nuevas preguntas no activen reglas sin evidencia.

No se probó hardware real, precisión diagnóstica, accesibilidad con usuarios externos ni el universo de todos los perfiles y secuencias posibles. Los 361 recorridos de la ruta general son muestra acotada; 28/30 preguntas aparecieron en ella. La alcanzabilidad de reglas en pruebas construidas no mide prevalencia de fallas ni probabilidad. No se implementaron modelos B/C, heurísticas, interfaz gráfica, casos de evaluación ni tag.

**Conclusión histórica previa a la corrección:** **REQUIERE CORRECCIONES** por cierres prematuros de tres rutas. La auditoría original no aplicó cambios al sistema.

## 9. Corrección autorizada de I-01, I-02, I-03 y O-01

**Alcance técnico:** seis hechos y sus seis preguntas (`p32`–`p37`), cuatro reglas directas y cambios locales en tres grafos. El catálogo vigente es de **36 hechos, 36 preguntas, 42 reglas y 18 diagnósticos**. Se conservó la polaridad de todas las preguntas anteriores y no se modificó `modelo_a.py`. Los terminales nuevos explican la insuficiencia de evidencia; no infieren diagnósticos. La presentación de O-01 cambia solo en la consola; la memoria de inferencia conserva todas las reglas activadas.

| Incidencia | Recorrido anterior y resultado | Recorrido posterior ejecutado y resultado |
| --- | --- | --- |
| I-01 | Video: `p07=Sí,p09=No` → `[p07,p09]`, `@bloqueo_imagen`; afirmaba que había imagen ahora. | Video con logotipo breve: `p07=Sí,p32=Sí,p08=Sí` → `[p07,p32,p08]`, `@resultado`, `d_pantalla_principal` por imagen sostenida en otra pantalla. Si `p32=?`, `p09=No` → `@insuficiente`, sin afirmación de imagen actual. Imagen que permanece: `p07=Sí,p32=No,p09=No` → `@bloqueo_imagen`. |
| I-02 | Conectividad: `p18=Sí` → `[p18]`, `@insuficiente`, sin examinar el fallo declarado. | Intermitente local: `p18=Sí,p33=Sí,p36=No` → `[p18,p33,p36]`, `d_conectividad_local`. Intermitente sin comparación: `p18=Sí,p33=Sí,p36=?` → `@patron_red_sin_causa`, sin hipótesis. Página concreta fallida: `p18=Sí,p33=No,p34=Sí,p37=Sí` → `d_conectividad_local`; con `p37=?` → `@patron_red_sin_causa`, sin hipótesis. |
| I-03 | Sistema: `p16=Sí,p17=No,p11=No` → `[p16,p17,p11]`, `@resultado`, sin registrar el error declarado. | `p16=Sí,p17=No,p11=No,p35=Sí` → `[p16,p17,p11,p35]`, `@error_uso_sin_causa`; el hecho queda verdadero, sin atribución causal. Un reinicio previo al sistema (`p16=No,p06=Sí`) no visita `p35`. |
| O-01 | Video: `p07=No,p02=Sí,p03=Sí,p08=Sí` mostraba pantalla principal y revisión general de inicio como dos hipótesis separadas. | El Modelo A sigue activando ambas. La consola muestra pantalla principal como hipótesis y las reglas generales `r_inicio_energia_luz`/`r_inicio_energia_ventilador` como evidencia complementaria, con sus condiciones; deja de repetir el diagnóstico general como alternativa. |

### Justificación de los cuatro cambios de conocimiento

- `r_pantalla_externa_tras_imagen_transitoria` exige **desaparición comprobada** de la imagen principal y **imagen sostenida** en otra pantalla antes de orientar a pantalla principal.
- `r_red_intermitente_compartida` y `r_red_intermitente_local` exigen cortes observados en esta computadora y comparación durante el mismo episodio; el segundo requiere que otro dispositivo permanezca conectado. Responder `?` a la comparación no activa ninguna de las dos.
- `r_red_pagina_fallida_local` exige que la página falle aquí y abra en otro dispositivo de la misma red. Cuando falla también allí o la comparación es desconocida, no se atribuye causa local o compartida.
- `s_error_durante_uso` es un registro de síntoma sin regla causal: un mensaje no específico no demuestra fallas de controlador, software, almacenamiento o hardware. El terminal comunica explícitamente esa limitación.

### Exploración posterior de las siete rutas

| Ruta | Trayectorias anteriores | Trayectorias posteriores | Cobertura posterior |
| --- | ---: | ---: | --- |
| Alimentación | 29 | 29 | 4/4 preguntas, 5 reglas, 2 diagnósticos. |
| Lentitud | 1.975 | 1.975 | 8/8 preguntas, 10 reglas, 5 diagnósticos. |
| Video | 231 | 277 | 9/9 preguntas, 10 reglas, 5 diagnósticos. |
| Sistema | 435 | 443 | 11/11 preguntas, 12 reglas, 6 diagnósticos. |
| Temperatura | 65 | 65 | 4/4 preguntas, 5 reglas, 2 diagnósticos. |
| Conectividad | 41 | 65 | 10/10 preguntas, 9 reglas, 4 diagnósticos. |
| General, muestra acotada | 361 | 361 | 28 preguntas visitadas; usa el mismo conjunto de nueve pivotes que la línea base. |
| **Total** | **3.137** | **3.215** | **2.854 exhaustivas en rutas específicas y 361 muestreadas en general.** |

La exploración posterior probó Sí, No y duda en cada pregunta visitada de las seis rutas específicas. Verificó en cada paso ausencia de ciclos y repeticiones, categoría constante, y que `p32` solo siga a imagen inicial, `p35` solo a sistema utilizable sin errores específicos confirmados y `p33/p34/p36/p37` solo a las situaciones de red que las justifican. `@insuficiente` no produjo diagnósticos en los recorridos enumerados. La ruta general sigue siendo una muestra, no una enumeración de todas las respuestas posibles. La prueba de testigos interactivos y la exploración específica cubrieron en conjunto **42/42 reglas y 18/18 diagnósticos**; omisión, desconocido o inversión de una condición no activan su regla.

### Verificaciones posteriores observadas

| Comando | Resultado |
| --- | --- |
| `python validar_conocimiento.py` | Correcto: 36 hechos, 18 diagnósticos, 42 reglas, 36 preguntas y siete rutas. |
| `python -m unittest discover -s tests -v` | **35 pruebas, 0 fallos**; cuatro nuevas regresiones para I-01, I-02, I-03 y O-01. |
| `python -m unittest discover -s auditoria -v` | **10 pruebas, 0 fallos**; caracterización posterior, mensajes de consola y exploración de siete rutas. |
| `python diagnosticar.py --respuestas ejemplos/ram.json` | Código 0; conserva la hipótesis de RAM con sus dos reglas registradas. |
| `python diagnosticar.py --respuestas ejemplos/sin_conclusion.json` | Código 0; termina sin diagnóstico concluyente. |
| `git diff --check` y `git tag --list avance-1` | Sin errores de espacios en el diff; sin tag `avance-1`. |

Tres ejecuciones interactivas completas de `diagnosticar.py` con entrada automatizada y UTF-8 terminaron con código 0: I-01 hizo tres preguntas y mostró la hipótesis de pantalla principal; I-02 hizo tres preguntas y explicó el patrón sin diagnóstico; I-03 hizo cuatro preguntas y explicó el error durante el uso sin diagnóstico. Esto verifica el flujo de `main` además de los recorridos directos del gestor.

**Archivos modificados para la corrección:** `data/conocimiento/hechos.json`, `data/conocimiento/reglas.json`, `data/interfaz/preguntas.json`, `data/interfaz/rutas.json`, `src/diagnostico_pc/rutas.py`, `src/diagnostico_pc/consola.py`, `tests/test_conocimiento.py`, `tests/test_modelo_a.py`, `tests/test_preguntas.py`, `tests/test_rutas.py`, `auditoria/test_auditoria_avance_1.py`, `auditoria/test_coherencia_contextual.py`, `README.md`, `CHECKLIST.md`, `docs/AVANCE_1.md`, `docs/BASE_CONOCIMIENTOS.md`, `docs/PREGUNTAS.md`, `docs/REDISENO_RUTAS_AVANCE_1.md` y este informe. El archivo `modelo_a.py` permanece intacto.

**Límites pendientes:** el cuestionario no identifica la causa de un error genérico durante el uso ni de un patrón de red sin comparación fiable. No se probaron equipos reales ni todas las `3^36` respuestas globales. Las correcciones técnicas quedan **pendientes de prueba personal y revisión del usuario**, sin cierre del Avance 1 ni creación de tag.
