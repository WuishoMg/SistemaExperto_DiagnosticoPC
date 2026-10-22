# Avance 1 — Sistema experto simbólico para diagnóstico de PC

**Estado:** Avance 1 finalizado por autorización expresa del usuario como versión académica reproducible. Las correcciones I-01 a I-03 y O-01 forman parte del cierre; el tag anotado `avance-1` identifica el commit de entrega. La precisión diagnóstica en computadoras reales todavía no ha sido evaluada.

## Objetivo y arquitectura

El proyecto orienta la revisión de fallas mediante observaciones trivalentes y reglas de producción SI–ENTONCES. El menú fija uno de siete problemas o la orientación general. Un grafo JSON escoge preguntas con tres transiciones por nodo; el gestor mantiene historial y hechos; el Modelo A evalúa las reglas directas; la consola presenta hipótesis, evidencias y recomendaciones. El grafo **no** concluye diagnósticos ni cambia la categoría por una respuesta.

El catálogo actual tiene **36 hechos y preguntas, 42 reglas y 18 diagnósticos**. El Modelo A conserva su implementación previa: un recorrido directo de reglas, memoria de trabajo y orden determinista por especificidad. El orden no representa probabilidad. La consola presenta una temperatura alta medida antes que los indicios subjetivos si ambos aparecen; no cambia la inferencia. Los hechos omitidos o respondidos «No estoy seguro» quedan `desconocido` y no satisfacen condiciones que requieren `falso`.

## Rediseño dentro del Avance 1

- **Alimentación:** luz y ventilador se preguntan por separado. La ausencia comprobada de ambas orienta a alimentación; su presencia conduce a comprobar imagen y, si la hay, inicio utilizable. Energía presente nunca significa funcionamiento correcto.
- **Lentitud y congelamientos:** se separaron en hechos distintos. Espacio, memoria ocupada, consumo de procesador o disco, errores de acceso y prueba de memoria solo se consultan cuando pueden aportar una diferencia; una prueba no realizada admite desconocido.
- **Video:** comienza por imagen. Las señales de energía solo se comprueban si falta imagen; una segunda pantalla ayuda a distinguir pantalla principal, video y fallas de inicio.
- **Sistema:** comienza por inicio utilizable. Los reinicios previos a mostrar el sistema no se tratan como fallos de archivos de arranque. `p10=Sí` registra unidad detectada (`s_unidad_no_detectada=falso`); `p10=No` registra unidad ausente.
- **Temperatura:** temperatura alta **medida** y meros indicios de calor/ventilación son diagnósticos diferentes. Un apagado o ruido aislado no confirma sobrecalentamiento.
- **Conectividad:** empieza por una prueba web. Wi-Fi, cable y enlace no identificado tienen ramas separadas; responder No a Wi-Fi no confirma Ethernet. No se inicia con preguntas de encendido, imagen o sistema.
- **General:** utiliza observaciones de orientación y luego un tramo pertinente sin cambiar la categoría mostrada.

## Corrección acotada de la auditoría de coherencia

- **I-01, imagen transitoria:** `p32` distingue imagen que desaparece tras el logotipo de imagen que permanece. La prueba externa `p08` exige imagen sostenida; una comparación positiva activa una regla adicional hacia la hipótesis de pantalla principal. Una respuesta incierta no provoca el bloqueo que afirmaba que «ahora aparece imagen».
- **I-02, conexión intermitente o parcial:** tras una página que sí abre, `p33/p36` comparan cortes simultáneos con otro dispositivo y `p34/p37` comparan una página fallida en ambos equipos. Solo comparaciones observadas activan tres reglas nuevas hacia hipótesis local o compartida. Si no hay comparación suficiente, se registra el patrón sin atribuir causa.
- **I-03, error durante el uso:** `p35` solo aparece después de un arranque utilizable sin pantalla azul ni error de archivos confirmado. Su respuesta se guarda como hecho y puede cerrar con una explicación de causa aún desconocida; no se añadió una regla causal para ese hecho.
- **O-01, presentación:** si otra pantalla mantiene imagen, las reglas generales de energía se muestran como evidencia complementaria de la hipótesis de pantalla principal. El Modelo A conserva las dos hipótesis en memoria; la consola evita repetir una hipótesis general como alternativa separada.

Se añadieron seis hechos/preguntas y cuatro reglas; no se añadieron diagnósticos ni se modificó `modelo_a.py`. Cada observación nueva representa un hecho específico. Las rutas de alimentación, lentitud, temperatura y la orientación general no cambiaron.

### Incidencias corregidas y criterio de verificación

La primera auditoría separó la integridad de los JSON de la **alcanzabilidad desde una consulta normal**: una regla podía ser válida y activarse con JSON técnico sin que el cuestionario reuniera sus condiciones. La corrección A-01–A-08 resolvió el fin prematuro ante respuestas desconocidas, el acceso a artefactos de video junto con error crítico, la atribución de Wi-Fi a un problema de cable, la confusión entre POST e inicio del sistema, el orden de comprobación de energía y pantalla externa, y la exposición de IDs internos al explicar contradicciones. Se mantuvieron pruebas de testigos interactivos por regla como control separado del validador estructural. En particular, `p25` explicita el enlace intentado y `p26` la etapa alcanzada; si faltan, el hecho permanece desconocido y no satisface una condición negativa.

La revisión posterior I-01–I-03 y O-01 corrigió la interpretación de imagen transitoria, la comparación de problemas de red intermitentes o de una página concreta, el registro de errores genéricos durante el uso y la presentación de una hipótesis amplia de energía junto con la hipótesis de pantalla principal. Las comprobaciones que no se realizaron no se convierten en negaciones. La sección siguiente recoge la cobertura observada; los recorridos y tablas extensas anteriores al cierre permanecen recuperables en el tag inmutable `avance-1`.

El usuario puede contestar `1/2/3` o `s/n/?`, volver con `v`, editar una respuesta anterior con `e`, finalizar con `f` o solicitar un cambio con `c`. Un cambio requiere confirmación y crea una sesión sin hechos anteriores. Las respuestas posteriores a una edición se descartan porque su aplicabilidad pudo cambiar. Las contradicciones detectadas del mismo intento detienen el resultado hasta corregirse.

## Evidencia y límites

La validación estructural comprobó **36 hechos, 36 preguntas, 42 reglas, 18 diagnósticos y siete grafos**. La suite habitual cubre 21 recorridos terminales —tres por categoría— y cuatro regresiones específicas, además de polaridad, cambio confirmado, edición, etapa POST, ejemplos JSON y regresión del Modelo A. En la verificación final, `python -m unittest discover -s tests -v` pasó **35 pruebas** y `python -m unittest discover -s auditoria -v` pasó **10 pruebas**. Ambos ejemplos JSON terminaron con código 0. La auditoría separada comprueba activación exacta de cada condición y testigos interactivos para **42/42 reglas y 18/18 diagnósticos**. Se exploraron **3.215 trayectorias**: todas las ramas de las seis rutas específicas y una muestra acotada de la general. Los comandos y resultados finales también se registran en `CHECKLIST.md`.

Esta cobertura prueba el programa dentro de los escenarios definidos; no mide precisión con computadoras reales. Algunas rutas concluyen «sin evidencia suficiente», especialmente si las comprobaciones relevantes son desconocidas. La detección de contradicciones es deliberadamente limitada al mismo intento y no modela todas las fallas intermitentes. El cuestionario tampoco identifica la causa de un error genérico durante el uso ni de un patrón de red sin comparación fiable; no se exploraron todas las `3^36` combinaciones globales.

**Perspectiva al cerrar el Avance 1:** los modelos B y C, la inferencia multinivel y la comparación experimental eran trabajo posterior. El Avance 2 ya implementó y comparó esos modelos y seleccionó C; sus resultados están en `AVANCE_2.md` y `RESULTADOS_EXPERIMENTALES_AVANCE_2.md`. La entrega final aún reserva interfaz gráfica, visualización, PDF y evaluación independiente. Los 20 casos finales no se usaron para ajustar este conocimiento.
