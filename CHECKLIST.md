# Estado del proyecto

**Estado vigente:** Avance 1 finalizado por autorización expresa del usuario como versión académica reproducible. Las cantidades, resultados y casillas pendientes de secciones anteriores registran estados históricos; el cierre actual se documenta al final. La precisión diagnóstica en equipos reales no ha sido evaluada.

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
- [x] Creadas pruebas separadas en `auditoria/` y el informe `docs/AUDITORIA_RUTAS_AVANCE_1.md`.
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
- [x] Actualizados `docs/AUDITORIA_RUTAS_AVANCE_1.md`, `docs/AVANCE_1.md`, `docs/BASE_CONOCIMIENTOS.md`, `docs/PREGUNTAS.md`, `README.md` e informe de cierre de correcciones.
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

**Archivos del rediseño:** catálogos JSON de conocimiento y preguntas, grafo JSON de rutas, representación de hechos, validador y gestor de rutas, consola, pruebas habituales y auditoría, `README.md`, `CHECKLIST.md`, `docs/AVANCE_1.md`, `docs/BASE_CONOCIMIENTOS.md`, `docs/PREGUNTAS.md` y `docs/REDISENO_RUTAS_AVANCE_1.md`. Los informes de auditoría y cierre técnico anteriores quedaron marcados como históricos. El archivo `modelo_a.py` no se modificó en este rediseño.

### Corrección de coherencia I-01, I-02, I-03 y O-01 — Pendiente de revisión manual

- [x] I-01: registrada la desaparición de imagen después del logotipo; la prueba con otra pantalla requiere imagen sostenida y el caso transitorio continúa en video.
- [x] I-02: registrados cortes intermitentes y fallas de página concreta; las nuevas reglas de red exigen comparación pertinente con otro dispositivo. La evidencia desconocida no activa una causa.
- [x] I-03: registrado un error durante el uso después de un inicio utilizable; el sistema comunica causa no determinada y no añade una regla causal.
- [x] O-01: la consola integra evidencia general de energía en el resultado de pantalla principal sin alterar el Modelo A ni omitir las reglas activadas.
- [x] Agregadas cuatro regresiones habituales y actualizada la auditoría independiente con recorridos anteriores y posteriores.
- [x] Comprobadas las siete rutas: 2.854 trayectorias exhaustivas en las seis específicas y 361 trayectorias acotadas en general; 42/42 reglas y 18/18 diagnósticos alcanzables.
- [x] Actualizados `docs/AUDITORIA_COHERENCIA_AVANCE_1.md`, `docs/AVANCE_1.md`, este checklist y los catálogos técnicos pertinentes.
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

- [ ] Fases 4–6: Modelos B y C, 80 casos, comparación de 60 casos e informe del Avance 2.
- [ ] Fases 7–8: evaluación final reservada, interfaz e informe final.
