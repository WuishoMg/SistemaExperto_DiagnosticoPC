# Estado del proyecto

**Estado vigente:** Avance 1 finalizado; Avance 2 cerrado por autorización expresa del usuario como versión académica `avance-2`. El Modelo C quedó seleccionado y congelado para la futura aplicación gráfica; A sigue predeterminado en consola. Las cantidades y resultados de secciones anteriores registran estados históricos. Solo se evaluaron 55 casos elegibles de desarrollo; los 20 finales siguen reservados. No se ha medido precisión diagnóstica en equipos reales.

**Lectura documental vigente:** `docs/AVANCE_1.md`, `docs/AVANCE_2.md`, `docs/BASE_CONOCIMIENTOS.md`, `docs/PREGUNTAS.md`, `docs/PROTOCOLO_EVALUACION_AVANCE_2.md` y `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md` son los seis documentos principales. `docs/REVISION_CASOS_ETAPA_4_1.md` permanece como séptimo registro porque su ruta y huella están congeladas. Las menciones posteriores a informes de auditoría del Avance 1 y al informe separado de distribución describen archivos **históricos de su etapa**, ya integrados en los documentos principales; los originales del Avance 1 se recuperan desde el tag `avance-1`. No usar esas menciones como enlaces del árbol actual.

## Fase 1 — Auditoría inicial

- [x] Confirmada carpeta de proyecto vacía y ausencia inicial de repositorio Git.
- [x] Aprobado el plan de trabajo progresivo por el usuario.

## Fase 2 — Base de conocimientos

- [x] Repositorio Git inicializado en `main`.
- [x] Estructura modular y documentación inicial creadas.
- [x] Definidos 20 síntomas, 11 diagnósticos y 23 reglas en JSON.
- [x] Representación de hechos en tres estados sin convertir desconocido en falso.
- [x] Validador de estructura, referencias, IDs y condiciones.
- [x] Pruebas automatizadas de integridad y errores representativos.
- [x] Documentadas decisiones y limitaciones en `docs/BASE_CONOCIMIENTOS.md`.

### Evidencia de ejecución de la Fase 2

- `python validar_conocimiento.py`: **correcto**; 20 hechos, 11 diagnósticos y 23 reglas.
- `python -m unittest discover -s tests -v`: **correcto**; 6 pruebas, 0 fallos.
- Entorno observado: Python 3.14.2, Git 2.52.0 (Windows).
- Incidencia corregida: una prueba intentó escribir en el directorio temporal del sistema, bloqueado por el entorno; se sustituyó por un archivo simulado en memoria y se volvió a ejecutar toda la suite.
- No hay tag `avance-1`; la entrega aún no ha terminado.

## Fase 3 — Motor y Modelo A

- [x] Motor de reglas SI–ENTONCES con recorrido hacia adelante de hechos a diagnósticos directos.
- [x] Memoria de trabajo trivalente, condiciones verificadas y reglas activadas.
- [x] Agrupación de reglas por diagnóstico y orden determinista de hipótesis.
- [x] Explicación con hechos, reglas y recomendaciones, incluso cuando hay varias hipótesis.
- [x] Resultado explícito sin conclusión cuando faltan datos o no coincide una regla.
- [x] Consola interactiva completa y modo con respuestas JSON.
- [x] Pruebas unitarias y funcionales de escenarios distintos.
- [x] Informe académico `docs/AVANCE_1.md` preparado.

### Evidencia de ejecución de la Fase 3

- `python validar_conocimiento.py`: **correcto**; 20 hechos, 11 diagnósticos y 23 reglas; los archivos JSON no se modificaron.
- `python -m unittest discover -s tests -v`: **correcto** en el cierre técnico de Fase 3; 14 pruebas, 0 fallos.
- `python diagnosticar.py --respuestas ejemplos/ram.json`: **correcto**; hipótesis principal de RAM, reglas `r_ram_reinicio_post` y `r_ram_codigo_post`, hechos y recomendaciones impresos.
- Pruebas funcionales en subproceso: consulta interactiva de 20 preguntas, ejemplo RAM y ejemplo sin conclusión; todos terminaron con código 0.
- Incidencia corregida: el subproceso de pruebas emitía texto con la codificación local de Windows; se fijó UTF-8 en la captura de pruebas y se repitió la suite completa.
- [ ] Validación del usuario y autorización expresa para cerrar el Avance 1 y crear `avance-1`.

### Mejora de preguntas previa al cierre del Avance 1

- [x] Redactadas 20 preguntas visibles con ayuda para personas sin conocimientos técnicos.
- [x] Separado el cuestionario en `data/interfaz/preguntas.json` del catálogo lógico de hechos y reglas.
- [x] Mapeo explícito Sí/No por pregunta; seis preguntas invierten la polaridad y No estoy seguro se registra como `desconocido`.
- [x] Consola actualizada para mostrar texto, ayuda y las tres opciones completas.
- [x] Menú `1. Sí`, `2. No`, `3. No estoy seguro` y equivalencia probada entre `1/2/3` y `s/n/?` para preguntas directas e invertidas.
- [x] Validador de cobertura, duplicados y polaridad del cuestionario.
- [x] Pruebas de preguntas positivas e invertidas y regresión de los ejemplos JSON.
- [x] Documentadas las preguntas definitivas en `docs/PREGUNTAS.md` y actualizado `docs/AVANCE_1.md`.

**Evidencia:** `python validar_conocimiento.py` confirmó 20 hechos, 11 diagnósticos, 23 reglas y 20 preguntas. `python -m unittest discover -s tests -v` terminó con **20 pruebas, 0 fallos**; la nueva prueba comprueba los seis valores `1`, `2`, `3`, `s`, `n` y `?` en una pregunta directa y otra invertida. Una demostración por consola con `n` en la pregunta 1, `2` en la 2 y `?` en las demás terminó con código 0, activó `r_alimentacion_led` y mostró la posible falla de alimentación. Los ejemplos `ram.json` y `sin_conclusion.json` siguen produciendo los resultados esperados. Los tres JSON de `data/conocimiento/` no se modificaron. El tag `avance-1` sigue pendiente de autorización de cierre.

### Reestructuración condicional del Avance 1 — Implementada, cierre pendiente

- [x] Auditoría previa del cuestionario, rutas y cobertura; cambio autorizado por el usuario.
- [x] Siete categorías iniciales sin tratarlas como hechos diagnósticos.
- [x] 24 preguntas visibles y requisitos declarativos para hacer solo las aplicables.
- [x] Reorientación de la consulta, respuestas desconocidas, retroceso y cambio de categoría.
- [x] Detección básica de contradicciones del mismo intento de uso, también en JSON técnico.
- [x] Conocimiento para lentitud ampliado a 24 hechos, 14 diagnósticos y 26 reglas, conservando los IDs y las 23 reglas originales.
- [x] Validación de rutas, referencias, condiciones y dependencias circulares.
- [x] Pruebas de recorridos completos, polaridad, corrección, contradicciones y ejemplos anteriores.
- [x] README, catálogo de preguntas, base de conocimientos e informe académico actualizados.
- [ ] Revisión del usuario y autorización expresa del cierre del Avance 1 y del tag `avance-1`.

**Evidencia observada:** `python validar_conocimiento.py` terminó correctamente con 24 hechos, 14 diagnósticos, 26 reglas, 24 preguntas y 7 categorías. `python -m unittest discover -s tests -v` terminó con **31 pruebas, 0 fallos**. La demostración de consola de video terminó con código 0 y activó `r_pantalla_externa`; las pruebas funcionales conservaron los resultados de `ejemplos/ram.json` y `ejemplos/sin_conclusion.json`. No se creó ningún tag ni se publicaron cambios. Las pruebas no establecen precisión diagnóstica en equipos reales.

### Auditoría integral de rutas y diagnósticos — Línea base previa a correcciones

- [x] Inspeccionadas las siete categorías, 24 preguntas, 26 reglas y 14 diagnósticos.
- [x] Creadas pruebas separadas en `auditoria/` y un informe histórico de rutas, recuperable en `avance-1` y sintetizado ahora en `docs/AVANCE_1.md`.
- [x] Verificadas 173 condiciones de activación/omisión de reglas y exploradas 701 trayectorias acotadas de preguntas.
- [x] Confirmado que los 14 diagnósticos tienen al menos una ruta de cuestionario y que 25 de las 26 reglas tienen testigo interactivo normal.
- [x] Repetidos validador, 31 pruebas de regresión y ambos ejemplos JSON; todos correctos.
- [x] Corregidas las incidencias A-01 a A-04: fin prematuro con respuesta desconocida, una regla inaccesible, confusión Wi-Fi/cable y etapa POST/arranque.
- [x] Corregidas las incidencias A-05 a A-08 y repetidas las verificaciones.

**Resultado de auditoría:** 7 pruebas independientes, **2 fallos que reproducen A-01 y A-02**; estado **REQUIERE CORRECCIONES**. No se modificaron reglas, diagnósticos ni implementación durante esta auditoría. No se creó `avance-1`.

### Corrección de incidencias A-01 a A-08 — Verificada, cierre pendiente

- [x] Catálogo actual: 26 hechos y preguntas, 14 diagnósticos, 26 reglas y 7 categorías.
- [x] `p02/p03` siguen a respuestas desconocidas en alimentación y general; no se convierten en negaciones diagnósticas.
- [x] `r_video_artefactos_error` activable desde consola mediante `p17` y `p09`.
- [x] Conexión por cable no atribuye una falla al Wi-Fi deshabilitado.
- [x] Reinicios antes del sistema se distinguen de la etapa de arranque del sistema.
- [x] Señales de energía preceden la prueba con pantalla externa en video.
- [x] El control dinámico de alcanzabilidad se ejecuta en la suite separada de auditoría.
- [x] Las contradicciones se explican con texto de preguntas, no IDs internos.
- [x] Se verificaron retroceso, cambio de categoría, contradicciones y respuestas desconocidas.
- [x] Actualizados entonces el informe histórico de rutas, `docs/AVANCE_1.md`, `docs/BASE_CONOCIMIENTOS.md`, `docs/PREGUNTAS.md`, `README.md` y el cierre técnico histórico; ambos informes se recuperan desde `avance-1`.
- [ ] Validación manual y autorización expresa del cierre del Avance 1 y del tag `avance-1`.

**Evidencia posterior a la corrección:** `python validar_conocimiento.py` terminó con código 0 y confirmó 26 hechos, 14 diagnósticos, 26 reglas, 26 preguntas y 7 categorías. `python -m unittest discover -s tests -v`: **31 pruebas, 0 fallos**. `python -m unittest discover -s auditoria -v`: **7 pruebas, 0 fallos**; 26/26 reglas y 14/14 diagnósticos con testigos de cuestionario, 185 comprobaciones directas y 781 trayectorias terminales acotadas sin ciclos. Ambos ejemplos JSON terminaron con código 0 y conservaron sus resultados. Una consulta de consola por cable terminó con código 0 y mostró solo `d_conectividad_local`. No se creó tag ni se publicaron cambios.

### Rediseño de rutas independientes — Implementado, pendiente de prueba personal

- [x] Etapa 1: revisados hechos y reglas; retirados tres hechos compuestos; catálogo actual de 30 hechos/preguntas, 18 diagnósticos y 38 reglas.
- [x] Etapa 2: siete grafos con transiciones Sí, No y desconocido; categoría fija y preguntas reutilizadas solo donde corresponden.
- [x] Etapa 3: consola con cambio confirmado y sesión nueva, retroceso, edición, finalización y explicación de bloqueos.
- [x] Etapa 4: pruebas de 21 recorridos completos, polaridad de `p10`, POST frente a arranque, temperatura medida frente a indicios, condiciones de reglas y alcanzabilidad.
- [x] Documentados el catálogo, los grafos, las limitaciones y la compatibilidad de JSON técnico.
- [ ] Prueba personal del usuario y autorización expresa para cerrar el Avance 1.
- [ ] Tag `avance-1`: no creado.

**Evidencia observada antes de la prueba personal:** `python validar_conocimiento.py` terminó con código 0 y confirmó 30 hechos, 18 diagnósticos, 38 reglas, 30 preguntas y siete rutas. `python -m unittest discover -s tests -v` terminó con **31 pruebas, 0 fallos**; `python -m unittest discover -s auditoria -v` con **3 pruebas, 0 fallos** y testigos interactivos para **38/38 reglas y 18/18 diagnósticos**. Ambos ejemplos JSON terminaron con código 0. `git diff --check` terminó con código 0 y `git tag --list avance-1` no devolvió ningún tag. Las pruebas de software no miden precisión en equipos reales.

**Archivos del rediseño:** catálogos JSON de conocimiento y preguntas, grafo JSON de rutas, representación de hechos, validador y gestor de rutas, consola, pruebas habituales y auditoría, `README.md`, `CHECKLIST.md`, `docs/AVANCE_1.md`, `docs/BASE_CONOCIMIENTOS.md`, `docs/PREGUNTAS.md` y un registro histórico del grafo, recuperable en `avance-1` y resumido ahora en `docs/PREGUNTAS.md`. Los informes de auditoría y cierre técnico anteriores quedaron marcados como históricos. El archivo `modelo_a.py` no se modificó en este rediseño.

### Corrección de coherencia I-01, I-02, I-03 y O-01 — Pendiente de revisión manual

- [x] I-01: registrada la desaparición de imagen después del logotipo; la prueba con otra pantalla requiere imagen sostenida y el caso transitorio continúa en video.
- [x] I-02: registrados cortes intermitentes y fallas de página concreta; las nuevas reglas de red exigen comparación pertinente con otro dispositivo. La evidencia desconocida no activa una causa.
- [x] I-03: registrado un error durante el uso después de un inicio utilizable; el sistema comunica causa no determinada y no añade una regla causal.
- [x] O-01: la consola integra evidencia general de energía en el resultado de pantalla principal sin alterar el Modelo A ni omitir las reglas activadas.
- [x] Agregadas cuatro regresiones habituales y actualizada la auditoría independiente con recorridos anteriores y posteriores.
- [x] Comprobadas las siete rutas: 2.854 trayectorias exhaustivas en las seis específicas y 361 trayectorias acotadas en general; 42/42 reglas y 18/18 diagnósticos alcanzables.
- [x] Actualizados entonces el informe histórico de coherencia, `docs/AVANCE_1.md`, este checklist y los catálogos técnicos pertinentes; el informe se recupera desde `avance-1` y su síntesis vigente está en `docs/AVANCE_1.md`.
- [ ] Prueba personal del usuario y autorización expresa para cerrar el Avance 1.
- [ ] Tag `avance-1`: no creado.

**Evidencia observada:** `python validar_conocimiento.py` terminó con código 0 (36 hechos, 36 preguntas, 42 reglas, 18 diagnósticos, siete categorías). `python -m unittest discover -s tests -v` pasó con **35 pruebas**; `python -m unittest discover -s auditoria -v` pasó con **10 pruebas**. Ambos ejemplos JSON terminaron con código 0; `ram.json` conservó la hipótesis de RAM y `sin_conclusion.json` no produjo diagnóstico. La unión de rutas específicas activó **42/42 reglas y 18/18 diagnósticos**. `git diff --check` terminó con código 0 y `git tag --list avance-1` no devolvió resultados. La exploración verificó ausencia de ciclos, preguntas nuevas en contexto y desconocido distinto de falso. La precisión en computadoras reales y la prueba personal siguen pendientes. `src/diagnostico_pc/modelo_a.py` no se modificó.

## Cierre oficial del Avance 1 — Verificación final

- [x] Cierre autorizado expresamente por el usuario; rama principal local `main` comprobada.
- [x] Revisados los cambios y las exclusiones de `.gitignore`; los archivos pendientes corresponden a código, catálogos, pruebas y documentación del Avance 1. No se detectaron credenciales, entornos virtuales, cachés ni archivos temporales para incluir.
- [x] `python validar_conocimiento.py`: código 0; **36 hechos, 36 preguntas, 42 reglas, 18 diagnósticos y siete rutas**.
- [x] `python -m unittest discover -s tests -v`: **35 pruebas, 0 fallos**.
- [x] `python -m unittest discover -s auditoria -v`: **10 pruebas, 0 fallos**; testigos para 42/42 reglas y 18/18 diagnósticos; 2.854 trayectorias de seis rutas específicas y 361 trayectorias acotadas de la general.
- [x] `python diagnosticar.py --respuestas ejemplos/ram.json`: código 0, hipótesis de RAM respaldada por dos reglas.
- [x] `python diagnosticar.py --respuestas ejemplos/sin_conclusion.json`: código 0, sin diagnóstico concluyente.
- [x] Incluidos `README.md`, `docs/AVANCE_1.md` y todos los informes técnicos y de auditoría, conservando los resultados históricos.

**Alcance del cierre:** prototipo académico de IA simbólica con Modelo A y cuestionario condicional; la precisión diagnóstica en computadoras reales no está medida. El tag anotado `avance-1` identifica el commit de cierre. La publicación en GitHub se verifica por separado de las pruebas locales.

## Entregas posteriores — Pendientes de autorización

- [x] Etapa 5 del Avance 2: evaluados 55 casos elegibles de desarrollo; resultados e informe creados y revisados por el usuario.
- [x] Etapa 6 del Avance 2: C seleccionado y congelado mediante manifiesto; cierre autorizado por el usuario.
- [ ] Fases 7–8: evaluación final reservada, interfaz e informe final.

## Avance 2 — Etapa 1: preparación de arquitectura

- [x] Verificada la línea base antes de editar: `main` limpio, `HEAD` en `avance-1` (`0907b6220eac500aee5fb1eb5542df5862ddb385`), sin diferencias frente al tag ni motores B/C activos.
- [x] Ejecutados antes de editar el validador, 35 pruebas habituales y 10 de auditoría; todos correctos.
- [x] Agregados contrato estructural de modelo y resultado y selector de A/B/C; A sigue predeterminado, B/C comunican «no implementado».
- [x] Adaptada la consola al selector sin cambiar `modelo_a.py`, catálogos JSON, preguntas ni siete rutas.
- [x] Añadidas seis pruebas de arquitectura y compatibilidad.
- [x] Registrado en `docs/AVANCE_2.md` el plan de 60 viñetas de desarrollo y 20 finales independientes, las métricas previstas y el control de filtraciones; no se generaron ni evaluaron casos.
- [x] Verificación posterior: `python validar_conocimiento.py` correcto (36 hechos, 18 diagnósticos, 42 reglas, 36 preguntas y siete rutas); `python -m unittest discover -s tests -v` **41 pruebas, 0 fallos**; `python -m unittest discover -s auditoria -v` **10 pruebas, 0 fallos**.
- [x] Las salidas estándar de `ram.json` y `sin_conclusion.json` conservaron exactamente los hashes SHA-256 de la línea base; A predeterminado y A explícito produjeron las mismas salidas.
- [x] Etapa 1 revisada y aprobada expresamente por el usuario al autorizar la etapa 2.

**Archivos creados:** `src/diagnostico_pc/contratos.py`, `src/diagnostico_pc/selector.py`, `tests/test_arquitectura_avance_2.py`, `docs/AVANCE_2.md`. **Modificados:** `src/diagnostico_pc/consola.py`, `README.md`, `CHECKLIST.md`. Limitación: solo A infiere; no hay resultados comparativos ni medición de calidad diagnóstica real. No se modificó `avance-1`, no se creó `avance-2` y no se publicó nada.

## Avance 2 — Etapa 2: Modelo B multinivel

- [x] Autorizada la etapa 2 después de la aprobación de la etapa 1; verificada la línea base local de 41 pruebas habituales, 10 de auditoría y validador correctos.
- [x] Ampliación independiente `data/conocimiento_avance2/` con **2 hechos derivados y 4 reglas nuevas** de arranque; ningún diagnóstico nuevo.
- [x] Motor B con rondas hasta punto fijo, reglas activadas una sola vez, estados trivalentes, soportes alternativos y trazas por nivel.
- [x] Validador de ampliación y rechazo de ciclos; contradicciones de conclusiones opuestas detectadas durante la evaluación.
- [x] Selector con A predeterminado, B disponible y C explícitamente no implementado; presentación de cadenas de B sin cambiar la salida de A.
- [x] Ejemplo reproducible `ejemplos/arranque_multinivel_b.json`: **3 rondas**, 2 hechos derivados y diagnóstico existente `d_arranque_so` respaldado por reglas directas y una cadena de tres niveles.
- [x] Verificación posterior: `python validar_conocimiento.py` correcto; `python -m unittest discover -s tests -v` **50 pruebas, 0 fallos**; `python -m unittest discover -s auditoria -v` **10 pruebas, 0 fallos**.
- [x] Probadas las siete rutas con B y los ejemplos JSON existentes; A conserva la salida previa en los ejemplos y sigue predeterminado.
- [x] Actualizados `docs/AVANCE_2.md`, `README.md` y este checklist con límites y resultados observados.
- [x] Revisión y aprobación de la etapa 2 confirmadas por el usuario al autorizar la etapa 4.

**Archivos creados en etapa 2:** `data/conocimiento_avance2/hechos.json`, `data/conocimiento_avance2/reglas.json`, `src/diagnostico_pc/conocimiento_b.py`, `src/diagnostico_pc/modelo_b.py`, `tests/test_modelo_b.py`, `ejemplos/arranque_multinivel_b.json`. **Modificados:** `src/diagnostico_pc/selector.py`, `src/diagnostico_pc/consola.py`, `validar_conocimiento.py`, `tests/test_arquitectura_avance_2.py`, `README.md`, `CHECKLIST.md`, `docs/AVANCE_2.md`. Limitación: la demostración multinivel está acotada al arranque y no hay evaluación diagnóstica independiente. Se preservaron A, la base original, las preguntas, rutas y `avance-1`; no se creó tag nuevo ni se publicó nada.

## Avance 2 — Etapa 3: Modelo C simbólico

- [x] Etapas 1 y 2 aprobadas por el usuario; implementada exclusivamente la etapa 3.
- [x] C reutiliza una ejecución completa de B: mismos hechos, reglas activadas, trazas e hipótesis; ordena principal y alternativas por calidad ordinal, observaciones originales distintas, prioridad técnica ordinal e ID estable.
- [x] Metadatos independientes `criterios_c.json` para 36 observaciones y 18 diagnósticos, con justificación y validación estricta.
- [x] C explica soportes originales, hechos derivados, cadenas, criterios aplicados y motivo de cada posición; muestra todas las alternativas.
- [x] Ejemplo térmico reproducible: B prioriza `d_indicios_termicos` por especificidad de regla e ID; C prioriza `d_sobrecalentamiento` por temperatura medida, conserva la alternativa.
- [x] `python validar_conocimiento.py`: código 0; base original 36 hechos, 18 diagnósticos y 42 reglas; ampliación B 2 hechos y 4 reglas; criterios C completos.
- [x] `python -m unittest discover -s tests -v`: **60 pruebas, 0 fallos**; A/B sin regresiones en las pruebas existentes, diez pruebas nuevas de C.
- [x] `python -m unittest discover -s auditoria -v`: **10 pruebas, 0 fallos**.
- [x] Revisión y aprobación de la etapa 3 confirmadas por el usuario al autorizar la etapa 4.

**Archivos creados en etapa 3:** `data/conocimiento_avance2/criterios_c.json`, `src/diagnostico_pc/conocimiento_c.py`, `src/diagnostico_pc/modelo_c.py`, `tests/test_modelo_c.py`, `ejemplos/hipotesis_termicas_c.json`. **Modificados:** `src/diagnostico_pc/selector.py`, `src/diagnostico_pc/consola.py`, `validar_conocimiento.py`, `tests/test_arquitectura_avance_2.py`, `tests/test_modelo_b.py` (solo nombre de una prueba), `README.md`, `CHECKLIST.md` y `docs/AVANCE_2.md`. Limitaciones: criterios ordinales sin calibración estadística; la calidad diagnóstica aún no se evaluó mediante los 80 casos independientes. No hay casos experimentales, métricas, modelo elegido, interfaz gráfica, commits ni nuevo tag.

## Avance 2 — Etapa 4: casos y protocolo experimental

- [x] Etapas 1, 2 y 3 aprobadas; se trabajó exclusivamente en el diseño y validación de casos de etapa 4.
- [x] Definidas 60 viñetas académicas de desarrollo y 20 nuevas para reserva final en archivos separados; los 20 casos del intento anterior permanecen expuestos y no se reutilizaron.
- [x] Las siete rutas están cubiertas; cada viñeta documenta relato, trayecto alcanzable, estados trivalentes, etiquetas defendibles, prioridad justificada cuando corresponde, evidencia, faltantes, comprobaciones, razón técnica y fuentes.
- [x] Definido antes de evaluar el protocolo para conjuntos exactos, métricas micro multietiqueta, matrices por diagnóstico, principal, priorización y abstención; B y C deben conservar el mismo conjunto.
- [x] Identificados siete casos con información fuera del cuestionario para análisis cualitativo separado; un caso adicional fuera del catálogo es codificable.
- [x] Reserva final sellada con SHA-256 `7c609c0c614b1955d3fbbacca260b99f8c30f2b54e81473277bbe767f505d364`; manifiesto de versiones y fuentes registrado.
- [x] `python validar_casos.py`: código 0; 60/20, siete rutas, estados, trayectos, referencias, firma no duplicada entre grupos y huella comprobados.
- [x] `python validar_conocimiento.py`: código 0; base, preguntas, rutas, ampliación B y criterios C válidos.
- [x] `python -m unittest discover -s tests -v`: **65 pruebas, 0 fallos**; cinco nuevas pruebas verifican el validador sin ejecutar modelos sobre las 80 viñetas.
- [x] `python -m unittest discover -s auditoria -v`: **10 pruebas, 0 fallos**; `git diff --check`: código 0.
- [x] Actualizados `README.md`, `docs/AVANCE_2.md` y este checklist con resultados observados, distribución y límites.
- [x] Revisión y autorización expresa del usuario para corregir desarrollo en la etapa 4.1 y después evaluar solo la etapa 5.

**Archivos creados en etapa 4:** `data/evaluacion/casos_desarrollo.json`, `casos_finales_reservados.json`, `fuentes.json`, `RESERVA_FINAL.sha256`, `MANIFIESTO.json`, `validar_casos.py`, `tests/test_validacion_casos.py` y `docs/PROTOCOLO_EVALUACION_AVANCE_2.md`; la distribución antes separada se integró en `docs/AVANCE_2.md`. **Modificados entonces:** `README.md`, `CHECKLIST.md`, `docs/AVANCE_2.md`. Limitaciones: siete casos requieren observaciones que el cuestionario no puede obtener o representan causas fuera del catálogo; la revisión técnica fue interna y no confirma fallas reales. No se calcularon métricas ni se seleccionó modelo en esa etapa; tampoco se creó commit, tag ni publicación.

## Avance 2 — Etapa 4.1: corrección del desarrollo

- [x] Conservada copia exacta de los 60 casos originales en `data/evaluacion/historico/casos_desarrollo_etapa4_v1.json`; hash original y revisado registrados en `MANIFIESTO.json`.
- [x] Sustituidos D055 y D057, que repetían exactamente observaciones y etiquetas de D001 y D017; el conjunto sigue teniendo 60 casos y siete rutas.
- [x] Conservados como contrastes D004–D005, D017–D023 y D037–D044 por su cambio verificable de LED o ventilador.
- [x] Revisada la redacción de D017, D027, D037 y D045 sin usar predicciones ni modificar sus etiquetas.
- [x] Retiradas prioridades no fundamentadas de D010 y D052; aclaradas prioridades por preservación de datos y la diferencia entre hipótesis, orden y causa confirmada.
- [x] Validación aislada de desarrollo: 60/60 casos con IDs y estados válidos, trayectos alcanzables y observaciones coherentes; sin duplicados exactos de firma.
- [x] Registradas distribución, similitudes restantes, fuentes y límites en `docs/REVISION_CASOS_ETAPA_4_1.md`.
- [x] Revisión y aprobación de la etapa 4.1; autorización expresa para iniciar la Etapa 5.

**Archivos de etapa 4.1:** creado `data/evaluacion/historico/casos_desarrollo_etapa4_v1.json` y `docs/REVISION_CASOS_ETAPA_4_1.md`; modificados `data/evaluacion/casos_desarrollo.json`, `data/evaluacion/MANIFIESTO.json`, `docs/AVANCE_2.md` y `CHECKLIST.md`. La huella final registrada permaneció intacta. No se abrió la reserva ni se ejecutaron motores sobre viñetas. La batería completa no se ejecutó porque su prueba de casos abre el archivo reservado; se aplicó validación aislada de los 60 casos.

## Avance 2 — Etapa 5: evaluación experimental de desarrollo

- [x] Comprobados 60 casos de desarrollo, 55 elegibles y cinco excluidos; 38 referencias positivas, 17 vacías y diez prioridades justificadas. Huellas del desarrollo original y revisado, catálogos y código registradas.
- [x] Capturadas primero las predicciones brutas de A, B y C con las mismas observaciones reproducidas mediante el gestor de preguntas; etiquetas y justificaciones no llegaron a los motores.
- [x] Confirmada la igualdad de conjuntos B/C en 55/55 casos. A/B también coincidieron en los conjuntos; B activó hechos derivados en seis casos y C cambió el orden en cuatro.
- [x] Calculadas métricas, matrices 2×2 para los 18 diagnósticos por modelo, abstenciones, errores por ruta/escenario y prioridad para A/B/C sobre los mismos diez casos.
- [x] Accuracy exacto A/B/C: **48/55 (87,3 %)**. Prioridad del principal: **A 2/10, B 2/10, C 4/10**. Resultados completos en `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md`.
- [x] `python validar_conocimiento.py`: código 0. Pruebas funcionales seguras: **65, sin fallos**; auditoría: **10, sin fallos**. Reproducción: **12 archivos deterministas idénticos** en una segunda ejecución.
- [x] Conservadas las huellas de casos, conocimiento y motores tras la evaluación; reserva final sin abrir ni ejecutar.
- [x] Documentada la omisión de `validar_casos.py` y `python -m unittest discover -s tests -v`: ambos recorridos vigentes abren la reserva final.
- [x] Revisión de resultados de la etapa 5 y autorización expresa de la etapa 6 por el usuario.

**Archivos creados en etapa 5:** `evaluar_desarrollo.py`, `tests/test_evaluacion_desarrollo.py`, `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md` y `data/evaluacion/resultados_etapa5/`. **Modificados:** `docs/AVANCE_2.md` y este checklist. No se modificaron motores, reglas, casos, etiquetas ni conocimiento; no hubo commit, tag ni publicación. La concordancia se limita a viñetas académicas.

## Avance 2 — Etapa 6: selección y cierre técnico

- [x] Reconfirmadas las 26 huellas de código, conocimiento y desarrollo de la etapa 5, además de la huella de predicciones brutas, antes de seleccionar: todas coincidieron.
- [x] Seleccionado C como motor propuesto para la aplicación gráfica final por prioridad de revisión y explicabilidad: **4/10** y rango recíproco **0,700**, frente a **2/10** y **0,567** para A/B.
- [x] Documentado que A/B/C obtuvieron idénticos conjuntos, accuracy **48/55**, precisión micro **89,3 %**, recall micro **98,0 %**, F1 micro **93,5 %** y principal **35/38**; C no mejoró el accuracy.
- [x] Creado manifiesto de selección con versión, procedencia y SHA-256 de **44 archivos**; el verificador usa una lista cerrada sin el archivo final reservado.
- [x] Los registros de la etapa 6 mencionan un informe académico independiente, ausente del árbol al iniciar la consolidación; arquitectura, metodología, selección y límites se consultan en `docs/AVANCE_2.md`, y tablas, matrices, gráficas y errores en `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md`.
- [x] Conservado A como predeterminado actual; documentado C como predeterminado futuro de la aplicación gráfica y selección explícita de A/B/C para demostración.
- [x] `python validar_conocimiento.py`: código 0. Pruebas seguras: **68, sin fallos**; auditoría: **10, sin fallos**. Verificador: **44 archivos coincidentes**.
- [x] Repetida captura y análisis de desarrollo en carpeta temporal: **12 archivos deterministas idénticos**, 55 elegibles, cinco excluidos y B/C con conjuntos iguales.
- [x] Ejecutados A, B y C por separado con `ejemplos/ram.json`: código 0; el modo predeterminado produjo la misma salida que A explícito.
- [x] `git diff --check`: código 0. Se omitieron `validar_casos.py` y la batería global porque leen la reserva final.
- [x] Revisión del usuario y autorización expresa para cerrar el Avance 2 en Git y publicar `main` y el tag `avance-2`.

**Archivos creados:** `data/evaluacion/MANIFIESTO_SELECCION.json`, `verificar_seleccion.py` y `tests/test_seleccion_modelo.py`; el informe académico independiente mencionado en el registro original ya no estaba en el árbol al iniciar esta consolidación. Su función documental queda cubierta por `docs/AVANCE_2.md` y el informe de resultados. **Modificados entonces:** `docs/AVANCE_2.md` y este checklist. **Límites:** diez prioridades justificadas son una muestra pequeña; las viñetas no verifican fallas físicas ni rendimiento en equipos reales. No se modificaron motores, reglas, prioridades, etiquetas, selector ni consola; tampoco se abrió ni ejecutó la reserva final.

## Consolidación documental previa al cierre del Avance 2

- [x] Integradas en `docs/AVANCE_1.md`, `docs/BASE_CONOCIMIENTOS.md` y `docs/PREGUNTAS.md` las conclusiones vigentes de las auditorías, el rediseño de las siete rutas y las capas simbólicas B/C.
- [x] Integrada en `docs/AVANCE_2.md` la distribución inicial de 60 casos de desarrollo y 20 reservados, sus criterios de etiquetado y los límites; la revisión 4.1 continúa en su ruta protegida.
- [x] Actualizados `README.md` y las referencias vigentes de este checklist; README ya no recomienda ejecutar comandos que abren la reserva final.
- [x] Añadida a `.gitignore` una exclusión específica para `data/evaluacion/casos_finales_reservados.json`; el archivo sigue disponible localmente y fuera del seguimiento Git.
- [x] Retirados cinco documentos no protegidos después de trasladar su contenido relevante: auditorías de rutas y coherencia, cierre técnico de correcciones, rediseño de rutas e informe separado de distribución.
- [x] Revisado `AGENTS.md`: no contenía referencias a los cinco documentos retirados; se actualizó el estado de selección y congelación de C, el índice de siete documentos y la protección de los casos finales ya existentes. Se conservan las reglas de desarrollo y se condiciona la batería global a la autorización para leer la reserva.
- [x] Comprobación posterior: `python validar_conocimiento.py` terminó con código 0; `python verificar_seleccion.py` confirmó **44 archivos**; **68 pruebas funcionales seleccionadas** y **10 pruebas de auditoría** pasaron sin fallos.
- [x] Revisión de la consolidación y autorización separada del cierre en Git; la rama de respaldo permanece fuera de la publicación.

**Archivos modificados en esta consolidación:** `.gitignore`, `AGENTS.md`, `README.md`, `CHECKLIST.md`, `docs/AVANCE_1.md`, `docs/AVANCE_2.md`, `docs/BASE_CONOCIMIENTOS.md` y `docs/PREGUNTAS.md`. **Archivos retirados:** `docs/AUDITORIA_RUTAS_AVANCE_1.md`, `docs/CIERRE_CORRECCIONES_AVANCE_1.md`, `docs/REDISENO_RUTAS_AVANCE_1.md`, `docs/AUDITORIA_COHERENCIA_AVANCE_1.md` y `docs/DISTRIBUCION_CASOS_ETAPA_4.md`. **Limitaciones:** la carpeta `docs/` conserva siete archivos por la huella de revisión 4.1; `validar_casos.py` y la batería global siguen leyendo la reserva final y no se ejecutaron. Los resultados congelados y los 20 casos finales permanecen fuera de esta consolidación.

## Cierre definitivo del Avance 2

- [x] Cierre y publicación de `main` y `avance-2` autorizados expresamente por el usuario; versión académica identificada en `docs/AVANCE_2.md`.
- [x] `python verificar_seleccion.py`: **44 huellas SHA-256 coincidentes**. `python validar_conocimiento.py`: código 0. Pruebas funcionales seguras: **68, sin fallos**; auditorías: **10, sin fallos**.
- [x] `.gitignore` contiene `data/evaluacion/casos_finales_reservados.json`; `git check-ignore` confirmó su exclusión y `git ls-files` confirmó que no está rastreado. No se abrió ni ejecutó la reserva.
- [x] Los motores, catálogos, resultados experimentales y manifiestos congelados conservaron sus huellas. La documentación se consolidó sin modificar archivos protegidos.
- [ ] Evaluación de los 20 casos finales en la fase autorizada de la entrega final. `validar_casos.py` y la batería global siguen pendientes porque cargan esa reserva.

**Archivos del cierre documental:** `docs/AVANCE_2.md`, `AGENTS.md`, `README.md` y `CHECKLIST.md`. **Limitaciones:** las métricas proceden de 55 viñetas elegibles de desarrollo, la priorización se comparó en diez casos y no hay validación en equipos reales. La reserva final y la rama experimental no forman parte de esta entrega.

## Entrega final — Interfaz gráfica

- [x] Añadida una aplicación PySide6/Qt Quick independiente de la consola; C es su motor principal y A/B/C están disponibles para comparación académica.
- [x] Reutilizados el gestor, las siete rutas, el catálogo de preguntas y los motores sin modificarlos; respuestas desconocidas, edición, contradicciones, terminales y resultados se exponen mediante el adaptador.
- [x] Añadidas vistas de bienvenida, categorías, cuestionario, análisis, resultados y razonamiento; exportación PDF local e integración opcional de mascota por estado.
- [x] Instalado PySide6 6.12.0 en `.venv` y probada la carga QML en Qt `offscreen` con Python 3.14.2 en Windows 11. El PDF de prueba se abrió con Qt.
- [x] Pruebas funcionales seguras: 77 sin fallos, incluidas siete nuevas de sesión y dos de Qt/PDF; auditorías: diez sin fallos. `python validar_conocimiento.py` correcto; `python verificar_seleccion.py`: 44 huellas coincidentes.
- [ ] Prueba manual en ventana visible, recursos definitivos de la mascota y empaquetado Windows.
- [ ] Batería global y `validar_casos.py`, pendientes porque leen la reserva final prohibida.

**Archivos nuevos:** `interfaz_grafica.py`, `requirements-gui.txt`, `src/diagnostico_pc/gui/`, `tests/test_interfaz_grafica.py`, `tests/test_gui_qt.py` y `docs/ENTREGA_FINAL_INTERFAZ.md`. **Modificado:** `CHECKLIST.md`. Los motores, los catálogos, los manifiestos y los resultados experimentales permanecieron intactos.

## Entrega final — Pulido visual de la interfaz

- [x] Bienvenida sin avance automático, con entrada animada, barra visual finita y fondo exclusivo de iconos SVG en mosaico continuo.
- [x] Tarjetas, encabezados, estados, navegación y resultados reorganizados; trazas desplegables y SVG locales de Font Awesome Free 6.7.2 con licencia y atribución.
- [x] Mascota opcional: PNG transparente `mascota-saludando.png` antes de JPG; otras poses y animaciones admitidas por estado, sin sustituto.
- [x] Revisión Qt `offscreen` en 760×600, 1080×760 y 1440×900 para cuatro pantallas; capturas de resultado positivo y abstención.
- [x] Punto de entrada gráfico en ejecución tras dos segundos `offscreen`, sin mensajes en stderr.
- [x] 81 pruebas funcionales seguras y diez auditorías correctas; `python verificar_seleccion.py` confirmó 44 huellas. PDF, edición de respuestas, despliegue de trazas y cierre visual del mosaico cubiertos por las pruebas seguras.
- [ ] Revisar el ciclo completo del fondo y la interacción en una ventana visible. La mascota definitiva y el empaquetado siguen pendientes.

**Archivos del pulido:** componentes y `Main.qml` en `src/diagnostico_pc/gui/qml/`, `gui/bridge.py`, SVG y licencia en `gui/assets/icons/`, instrucciones en `gui/assets/mascota/README.md`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. No se ejecutaron `validar_casos.py` ni la batería global, que abrirían los 20 casos reservados.

## Entrega final — Corrección del bloqueo de Qt Quick

- [x] Sustituidos `width` y `height` por `Layout.preferredWidth` y `Layout.preferredHeight` en los dos `FaIcon` hijos directos de `RowLayout` que provocaban `possible QQuickItem::polish() loop`.
- [x] Prueba de regresión Windows en proceso separado con límite de tiempo: 6,8 segundos, al menos 12 pulsos de temporizador, siete tarjetas QML y clics reales de bienvenida, categoría y respuesta. Pasó con backend predeterminado y `QSG_RHI_BACKEND=software`, sin bucles `polish()`.
- [x] 82 pruebas funcionales seguras y diez auditorías sin fallos; `python verificar_seleccion.py` confirmó 44 huellas; `git diff --check` correcto.
- [ ] Revisión manual de la ventana visible en el equipo del usuario. Persisten advertencias de `implicitWidth` del diálogo y estilo nativo que no impidieron la interacción en la prueba.

**Archivos de la corrección:** `src/diagnostico_pc/gui/qml/Main.qml`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. La primera ejecución de pruebas seguras dio dos errores por permisos del directorio temporal del entorno aislado; la repetición con `TEMP` y `TMP` en `.venv/tmp_gui` pasó completa. No se ejecutaron la batería global ni `validar_casos.py` porque leen la reserva final.

## Entrega final — Botones y microanimaciones

- [x] `ActionButton.qml` unifica centrado de icono y texto, separación de 10 px, fondo personalizado, foco violeta por teclado y contraste de controles deshabilitados; eliminado el borde azul que aparecía al hover con el `Button` nativo.
- [x] Hover a 103 % y pulsación a 97 % en 180 ms con transformación visual, sin cambiar `width` ni `height` del layout; acciones de mouse y teclado sin duplicados.
- [x] Prueba Windows de alineación, hover, clic, Tab, Enter y `polish() loop`; capturas de cuestionario y resultados a 760×600 revisadas.
- [x] 83 pruebas funcionales seguras y diez auditorías correctas; `python verificar_seleccion.py` confirmó 44 huellas; `git diff --check` correcto.
- [ ] Revisión visual final en la ventana del usuario.

**Archivos de este ajuste:** `src/diagnostico_pc/gui/qml/ActionButton.qml`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. Las tarjetas de categoría, el fondo, el puente y el dominio permanecieron intactos. La batería global y `validar_casos.py` siguen pendientes por la reserva final.

## Entrega final — Mascotas y transición visual

- [x] Integradas las cinco poses PNG proporcionadas en bienvenida, categorías, preguntas, análisis e idea/resultados; recurso ausente oculto sin detener la interfaz.
- [x] Mascotas de categorías y preguntas superpuestas a la hero card sin tapar texto; entrada suave de la card y la mascota, con flotación ligera donde corresponde. Bienvenida con botón visible a 760×600 y sin avance automático.
- [x] Secuencia QML de 2500 ms de análisis y 800 ms de idea antes de llamar al mismo resultado C; navegar a categorías cancela los temporizadores.
- [x] Capturas Windows de las cinco vistas y transición revisadas; prueba de carga y respuesta prolongada sin `polish() loop`.
- [x] Centrada la columna previa al resultado: poses y etiquetas en el mismo eje; análisis 190×190 px e idea 214×214 px en un contenedor fijo. Capturas Windows a 760×600 y prueba Qt correctas.
- [x] 85 pruebas funcionales seguras y diez auditorías correctas; `python verificar_seleccion.py` confirmó 44 huellas; `git diff --check` correcto.
- [ ] Ajuste fino visual final en la ventana del usuario.

**Archivos de esta integración:** `src/diagnostico_pc/gui/bridge.py`, `gui/qml/Mascota.qml`, `gui/qml/HeroCard.qml`, `gui/qml/Main.qml`, `gui/assets/mascota/README.md`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. No se crearon imágenes nuevas ni se modificaron motores, conocimiento o inferencia. La batería global y `validar_casos.py` continúan pendientes por la reserva final.

## Entrega final — Hero cards animadas

- [x] Bienvenida, categorías, cuestionario y resultados usan tarjetas horizontales blancas y lavanda con entrada de 390 ms; el fondo decorativo común combina manchas, curvas e iconos SVG locales de Font Awesome Free en movimiento lento.
- [x] Las mascotas originales sobresalen de las tarjetas con sombra violeta. La composición mantiene texto y acciones a la izquierda y reserva espacio para la mascota a la derecha. Se respetan las poses existentes; no se generaron imágenes sustitutas.
- [x] Las animaciones de fondos se detienen cuando su pantalla está oculta y atienden la preferencia de movimiento reducido cuando Qt la expone. La bienvenida sigue esperando el botón «Empezar diagnóstico».
- [x] Capturas Windows revisadas en 760×600, 1080×760 y 1440×900. Una prueba nueva comprobó las cuatro tarjetas en esos tamaños, el solapamiento superior de la mascota, el movimiento del fondo y la ausencia de `polish() loop`.
- [x] Un ciclo completo de la mancha principal se midió durante 17 segundos en ventana Windows: 85 muestras, retorno al origen y desplazamiento máximo de 0,985 px entre muestras de 200 ms, sin salto brusco.
- [x] 86 pruebas funcionales seguras y diez auditorías correctas; `python verificar_seleccion.py` confirmó 44 huellas; `git diff --check` correcto.
- [ ] Revisión visual final en la ventana del usuario. La batería global y `validar_casos.py` permanecen pendientes por la reserva final.

**Archivos de este ajuste:** `src/diagnostico_pc/gui/qml/Main.qml`, `HeroCard.qml`, `HeroBackdrop.qml`, `Mascota.qml`, `FaIcon.qml`, siete SVG lavanda en `gui/assets/icons/lavender/`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. Los motores, el conocimiento, la inferencia y los manifiestos no se modificaron.

## Entrega final — Secuencia análisis → idea

- [x] «Analizando» permanece 2500 ms y después aparece «idea» durante 800 ms antes de solicitar el resultado.
- [x] La pose de idea se mantiene durante el estado `analisis` transitorio del puente; solo se retira al llegar a resultados o al cancelar la consulta. La prueba Qt observó ese estado intermedio sin que reapareciera la pose anterior.
- [x] Pasaron 86 pruebas funcionales seguras, incluida la prueba de secuencia y cancelación. La batería global y `validar_casos.py` siguen pendientes por la reserva final.

**Archivos de la corrección:** `src/diagnostico_pc/gui/qml/Main.qml`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. No se modificó el puente Python ni la inferencia.

## Entrega final — Espaciado y encabezado

- [x] La bienvenida oculta encabezado, icono y línea divisoria. Su hero card queda situada con un margen proporcional a la altura de la ventana; conserva fondo, mascota y botón sin avance automático.
- [x] Categorías, cuestionario y resultados mantienen encabezado, icono, línea y botón «Categorías» donde corresponde. La distancia medida de línea a hero card pasó de 70 px a 32 px mediante márgenes y `spacing` de `ColumnLayout`.
- [x] Capturas Windows revisadas en 760×600, 1080×760 y 1440×900. La prueba Qt comprobó visibilidad del encabezado, separación de 24–36 px, límites horizontales, ausencia de superposición con el botón, fondo animado y cero avisos `polish() loop`.
- [x] 86 pruebas funcionales seguras correctas; `python verificar_seleccion.py` confirmó 44 huellas; `git diff --check` correcto.
- [ ] Revisión visual final en la ventana del usuario. La batería global y `validar_casos.py` siguen pendientes por la reserva final.

**Archivos de este ajuste:** layout de `src/diagnostico_pc/gui/qml/Main.qml`, prueba en `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. No se modificaron mascotas, motores ni datos.

## Entrega final — Efectos de sonido

- [x] `AppAudio.qml` centraliza Qt Multimedia: bienvenida 15 %, análisis 15 %, idea 18 % y pop 15 %, todos con una sola reproducción. La bienvenida se solicita al aparecer la mascota y no vuelve a sonar.
- [x] Los sonidos de análisis e idea siguen los cambios de pose existentes; análisis se detiene al aparecer idea. El audio de idea termina naturalmente sobre resultados, donde permanece la misma pose, y se detiene si se abandona esa pantalla. Los botones y tarjetas de categoría emiten pop solo al hacer clic.
- [x] Generado `button-pop.wav` de 110 ms con `wave` de Python, sin bibliotecas nuevas. Los tres MP3 proporcionados permanecieron intactos; una prueba cargó el componente sin archivos de audio y continuó normalmente.
- [x] En ventana Windows, Qt informó `PlayingState` sin error para los tres MP3 e `isPlaying=True` para el pop. La prueba de interacción comprobó volúmenes, reproducción única, hover silencioso y secuencia de eventos.
- [x] 87 pruebas funcionales seguras y diez auditorías correctas; `python verificar_seleccion.py` confirmó 44 huellas; `git diff --check` correcto.
- [ ] Escucha manual para valorar el volumen y la calidad percibida. La batería global y `validar_casos.py` siguen pendientes por la reserva final.

**Archivos de esta integración:** `src/diagnostico_pc/gui/qml/AppAudio.qml`, `ActionButton.qml`, `Main.qml`, `gui/assets/sounds/button-pop.wav`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. No se añadieron dependencias ni se modificó la inferencia.

## Entrega final — Interfaz simplificada

- [x] Retiradas de las pantallas las etiquetas de modelos y la comparación académica; resultados conserva título, hipótesis, recomendaciones y razonamiento. La consulta gráfica sigue usando C internamente.
- [x] Reporte PDF con texto para usuario final, sin nombres de modelos y con criterios ordinales, recomendaciones, reglas y trazas. QtPdf abrió el archivo generado.
- [x] Prueba QML de bienvenida, categorías, cuestionario y resultados sin referencias visibles a modelos; botones restantes de resultados conservan la prueba de alineación e interacción.
- [x] 87 pruebas funcionales seguras, diez auditorías y 44 huellas SHA-256 correctas; `git diff --check` sin errores.
- [ ] La batería global y `validar_casos.py` siguen pendientes porque leen los 20 casos finales reservados.

**Archivos de este ajuste:** `src/diagnostico_pc/gui/qml/Main.qml`, `src/diagnostico_pc/gui/pdf_export.py`, `tests/test_gui_qt.py`, `README.md`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. El contrato del puente, los motores, los datos y los manifiestos permanecieron intactos.

## Entrega final — Reporte técnico PDF

- [x] Rediseñado el PDF A4 con blanco, lavanda `#F5F3FF`, violeta `#6355FF`, mascota de análisis transparente, tarjetas y pie numerado con «Del síntoma a la solución.».
- [x] Observaciones registradas y hechos derivados conservan `verdadero`, `falso` y `desconocido`, con texto y colores verde, naranja y gris. Las preguntas omitidas no se presentan como observaciones respondidas.
- [x] Conservadas hipótesis, alternativas, recomendaciones, reglas, criterios y trazas; guía imprimible basada exclusivamente en recomendaciones existentes, con casillas y notas.
- [x] Probados PDF sin hipótesis, con hechos derivados, con alternativa y una fixture de paginación de 13 páginas. QtPdf abrió y renderizó todas las páginas, con footer, numeración y franja libre; se revisaron capturas visuales.
- [x] Slot de exportación gráfica comprobado; 87 pruebas funcionales seguras, diez auditorías, 44 huellas SHA-256 y `git diff --check` correctos.
- [ ] Batería global y `validar_casos.py` pendientes por los 20 casos finales reservados.

**Archivos de este rediseño:** `src/diagnostico_pc/gui/pdf_export.py`, nuevo `src/diagnostico_pc/gui/pdf_layout.py`, `src/diagnostico_pc/gui/bridge.py`, `tests/test_gui_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. No se cambiaron motores, conocimiento, QML, manifiestos ni resultados experimentales.

## Entrega final — Ajuste de volumen

- [x] Bajados los niveles de bienvenida y análisis a 15 %, y el de idea a 18 % en `AppAudio.qml`; el pop permanece en 15 %. Los archivos de audio no se modificaron.
- [x] Pasó la prueba focalizada de botones y salidas de audio; `python verificar_seleccion.py` confirmó las 44 huellas y `git diff --check` no mostró errores.
- [ ] Pendiente escucha manual para valorar el volumen percibido. No se ejecutó la batería global por la reserva final.

## Respaldo previo a posibles funcionalidades adicionales

- [x] `main` y `origin/main` coincidían después de `git fetch origin`; `pre-finalizacion` no existía localmente ni en `origin` antes del respaldo. Los tags `avance-1` y `avance-2` se conservaron.
- [x] `python validar_conocimiento.py` correcto; `python verificar_seleccion.py` confirmó las 44 huellas protegidas. Pasaron 87 pruebas funcionales seguras y diez auditorías; la batería global y `validar_casos.py` siguen pendientes por la reserva final.
- [x] Creado y comprobado `data/interfaz/MANIFIESTO_GUI.json` con 109 huellas SHA-256 de código de ejecución, QML, imágenes, iconos y su licencia, sonidos, recurso PDF, configuración y dependencia de la GUI. La reserva final permanece ignorada.

**Archivos de este respaldo:** `data/interfaz/MANIFIESTO_GUI.json`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist, junto con los archivos de la GUI, pruebas y documentación que estaban pendientes de registrar. El manifiesto de selección, los motores y los resultados experimentales no se modificaron.

## Visualizador de razonamiento — implementación local

- [x] Adaptador puro de grafos a partir de trazas y resultado de C; observaciones respondidas trivalentes, reglas activadas, derivados e hipótesis conservan sus relaciones y orden. Reglas inactivas y preguntas no formuladas permanecen separadas de las conexiones causales.
- [x] Pantalla adicional con nodos, conexiones en `Canvas`, detalles, resaltado de soportes, zoom, desplazamiento y regreso al resultado sin repetir inferencia ni cambiar respuestas.
- [x] Posiciones y dimensiones calculadas en Python. Prueba Qt a 760×600, 1080×760 y 1440×900 con capturas no vacías y cero `polish() loop`; las 12 pruebas Qt anteriores pasaron con `TEMP` y `TMP` dirigidos a `.venv/tmp_gui`.
- [x] 94 pruebas funcionales seguras y 10 auditorías correctas. `python validar_conocimiento.py` correcto; `python verificar_seleccion.py`: 44 huellas coincidentes. La primera ejecución Qt usó un directorio temporal sin permisos y se repitió con el temporal del proyecto.
- [x] Manifiesto SHA-256 nuevo con 113 archivos de la GUI ampliada, independiente del respaldo de 109 huellas. El manifiesto anterior y el tag `pre-finalizacion` permanecen intactos.
- [ ] Revisión visual manual en la ventana del usuario. `validar_casos.py` y la batería global siguen pendientes porque leerían los 20 casos finales reservados.

**Archivos creados:** `src/diagnostico_pc/gui/reasoning_graph.py`, `src/diagnostico_pc/gui/qml/ReasoningNode.qml`, `src/diagnostico_pc/gui/qml/ReasoningDetails.qml`, `src/diagnostico_pc/gui/qml/ReasoningGraph.qml`, `tests/test_grafo_razonamiento.py`, `tests/test_grafo_qt.py`, `verificar_gui_razonamiento.py` y `data/interfaz/MANIFIESTO_GUI_RAZONAMIENTO.json`. **Modificados:** `src/diagnostico_pc/gui/session.py`, `src/diagnostico_pc/gui/bridge.py`, `src/diagnostico_pc/gui/qml/Main.qml`, `docs/ENTREGA_FINAL_INTERFAZ.md` y este checklist. Sin commits ni tags nuevos.

## Revisión de diseño del visualizador

- [x] Sustituida la presentación inicial por secciones verticales: observaciones verde suave, reglas lavanda, hechos derivados azul, principal destacada y alternativas secundarias. El panel de detalle muestra datos completos según el tipo de nodo.
- [x] Flechas dibujadas únicamente para condiciones y conclusiones presentes en trazas de C; pruebas con encadenamiento, condición falsa, soportes compartidos, alternativas y ausencia de hipótesis. Las preguntas desconocidas siguen aisladas si ninguna regla las utilizó.
- [x] Tarjetas y secciones posicionadas en Python; prueba Qt en `offscreen` y Windows a 760×600, 1080×760 y 1440×900 sin `polish() loop`, sin títulos truncados ni texto fuera de tarjetas. Capturas Windows revisadas; panel plegable en 760×600.
- [x] 94 pruebas funcionales seguras, 10 auditorías, `python validar_conocimiento.py` y `python verificar_seleccion.py` correctos; 44 huellas de selección intactas.
- [ ] Revisión visual final del usuario. La batería global y `validar_casos.py` continúan pendientes porque abrirían los 20 casos finales reservados.

**Archivos modificados en esta revisión:** `src/diagnostico_pc/gui/reasoning_graph.py`, `src/diagnostico_pc/gui/qml/ReasoningGraph.qml`, `src/diagnostico_pc/gui/qml/ReasoningNode.qml`, `src/diagnostico_pc/gui/qml/ReasoningDetails.qml`, `tests/test_grafo_razonamiento.py`, `tests/test_grafo_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md`, este checklist y el nuevo manifiesto de la GUI para reflejar los bytes finales. Sin cambios en motores, catálogos, resultados experimentales, manifiestos anteriores, sonidos, mascotas ni PDF; sin commits ni tags.

## Visualizador — panel de detalle simplificado

- [x] Quitados de la interfaz la leyenda repetida, «Reglas no activadas», «Mostrar lista» y «Preguntas no formuladas». Los datos internos y las conexiones se conservaron.
- [x] El panel presenta exclusivamente los campos del nodo seleccionado. La prueba Qt recorrió observación, regla, hecho derivado e hipótesis y comprobó encabezados propios y ausencia de secciones ajenas.
- [x] Selección, resaltado, zoom y regreso a resultados comprobados en `offscreen` y Windows a 760×600, 1080×760 y 1440×900; cero avisos `polish() loop`.
- [x] 94 pruebas funcionales seguras, 10 auditorías, `python validar_conocimiento.py` y `python verificar_seleccion.py` correctos; 44 huellas protegidas coincidentes.
- [ ] Revisión visual final del usuario. La batería global y `validar_casos.py` siguen pendientes porque leerían los 20 casos finales reservados.

**Archivos de este ajuste:** `src/diagnostico_pc/gui/qml/ReasoningDetails.qml`, `src/diagnostico_pc/gui/qml/ReasoningGraph.qml`, `tests/test_grafo_qt.py`, `docs/ENTREGA_FINAL_INTERFAZ.md`, este checklist y `data/interfaz/MANIFIESTO_GUI_RAZONAMIENTO.json` actualizado tras las pruebas. Sin commits ni tags.

## README actualizado para la GUI con visualizador

- [x] El README describe la pantalla de razonamiento, sus controles, el reporte PDF, los manifiestos histórico y actual, y un recorrido reproducible que genera dos hechos derivados.
- [x] `python validar_conocimiento.py`, `python verificar_seleccion.py` (44 huellas), `python verificar_gui_razonamiento.py` (113 huellas) y `git diff --check` correctos tras el ajuste documental.
- [ ] La batería global y `validar_casos.py` continúan pendientes porque leen los 20 casos finales reservados. No se repitieron las 94 pruebas funcionales para este cambio solo documental; su último resultado correcto permanece registrado arriba.

**Archivos modificados:** `README.md` y este checklist. Sin cambios de código, conocimiento, manifiestos ni resultados experimentales.
