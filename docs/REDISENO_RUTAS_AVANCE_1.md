# Rediseño de rutas condicionales — Avance 1

**Registro histórico del grafo anterior a I-01, I-02 e I-03.** Los recorridos actuales y sus cambios acotados se documentan en `docs/AUDITORIA_COHERENCIA_AVANCE_1.md`; `data/interfaz/rutas.json` es la fuente vigente de transiciones.

**Estado:** implementado y verificado automáticamente; pendiente de prueba personal y autorización de cierre. El grafo dirige preguntas y nunca concluye diagnósticos. Modelo A evalúa los hechos mediante reglas SI–ENTONCES al finalizar.

## Lectura del grafo

Cada categoría permanece fija. Cada nodo tiene destinos para Sí, No y No estoy seguro. Los destinos condicionales se evalúan en orden con los hechos registrados; el último es el destino por defecto. `@resultado` evalúa los hechos, `@insuficiente` informa que no quedan preguntas útiles y `@bloqueo_*` explica por qué conviene ofrecer un cambio de diagnóstico. En `@bloqueo_energia` de video no se presenta automáticamente una hipótesis de alimentación. El cambio exige confirmación y reinicia el historial. Cualquier pregunta técnica no realizada admite «No estoy seguro».

En alimentación, `p02/p03` distinguen ausencia de señales de energía de energía presente; con energía se pregunta por imagen y, si aparece, por inicio utilizable. En video, esas comprobaciones de energía se hacen solo después de que el usuario confirma falta de imagen. En conectividad no se pregunta de entrada por encendido, pantalla ni sistema. La ruta general reutiliza los tramos pertinentes sin cambiar su categoría.

## Mi computadora no enciende

Inicio: `p02`. La consulta sigue este grafo sin cambiar la categoría.

| Pregunta | Sí | No | No estoy seguro |
| --- | --- | --- | --- |
| `p02` | `p03` | `p03` | `p03` |
| `p03` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@resultado`<br>`s_led_encendido=verdadero` → `p07`<br>`s_ventiladores_giran=verdadero` → `p07`<br>resto → `@insuficiente` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@resultado`<br>`s_led_encendido=verdadero` → `p07`<br>`s_ventiladores_giran=verdadero` → `p07`<br>resto → `@insuficiente` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@resultado`<br>`s_led_encendido=verdadero` → `p07`<br>`s_ventiladores_giran=verdadero` → `p07`<br>resto → `@insuficiente` |
| `p07` | `p16` | `@resultado` | `@insuficiente` |
| `p16` | `@insuficiente` | `@bloqueo_sistema` | `@insuficiente` |

## Mi computadora está lenta o se congela

Inicio: `p21`. La consulta sigue este grafo sin cambiar la categoría.

| Pregunta | Sí | No | No estoy seguro |
| --- | --- | --- | --- |
| `p21` | `p27` | `p27` | `p27` |
| `p27` | `p22` | `s_lentitud_programas=verdadero` → `p22`<br>resto → `@insuficiente` | `s_lentitud_programas=verdadero` → `p22`<br>resto → `@insuficiente` |
| `p22` | `p23` | `p23` | `p23` |
| `p23` | `p24` | `p24` | `p24` |
| `p24` | `p28` | `p28` | `p28` |
| `p28` | `s_congelamientos=verdadero` → `p11`<br>`s_proceso_disco_alto=verdadero` → `p11`<br>resto → `@resultado` | `s_congelamientos=verdadero` → `p11`<br>`s_proceso_disco_alto=verdadero` → `p11`<br>resto → `@resultado` | `s_congelamientos=verdadero` → `p11`<br>`s_proceso_disco_alto=verdadero` → `p11`<br>resto → `@resultado` |
| `p11` | `@resultado` | `s_congelamientos=verdadero` → `p05`<br>resto → `@resultado` | `s_congelamientos=verdadero` → `p05`<br>resto → `@resultado` |
| `p05` | `@resultado` | `@resultado` | `@resultado` |

## Mi computadora enciende, pero no muestra imagen

Inicio: `p07`. La consulta sigue este grafo sin cambiar la categoría.

| Pregunta | Sí | No | No estoy seguro |
| --- | --- | --- | --- |
| `p07` | `p09` | `p02` | `p02` |
| `p09` | `@resultado` | `@bloqueo_imagen` | `@bloqueo_imagen` |
| `p02` | `p03` | `p03` | `p03` |
| `p03` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@bloqueo_energia`<br>`s_sin_imagen=verdadero` ∧ `s_led_encendido=verdadero` → `p08`<br>`s_sin_imagen=verdadero` ∧ `s_ventiladores_giran=verdadero` → `p08`<br>resto → `@insuficiente` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@bloqueo_energia`<br>`s_sin_imagen=verdadero` ∧ `s_led_encendido=verdadero` → `p08`<br>`s_sin_imagen=verdadero` ∧ `s_ventiladores_giran=verdadero` → `p08`<br>resto → `@insuficiente` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@bloqueo_energia`<br>`s_sin_imagen=verdadero` ∧ `s_led_encendido=verdadero` → `p08`<br>`s_sin_imagen=verdadero` ∧ `s_ventiladores_giran=verdadero` → `p08`<br>resto → `@insuficiente` |
| `p08` | `@resultado` | `p04` | `p04` |
| `p04` | `p06` | `p06` | `p06` |
| `p06` | `s_pitidos_ram_post=verdadero` → `@resultado`<br>resto → `p05` | `s_pitidos_ram_post=verdadero` → `@resultado`<br>resto → `p05` | `s_pitidos_ram_post=verdadero` → `@resultado`<br>resto → `p05` |
| `p05` | `@resultado` | `@resultado` | `@resultado` |

## El sistema operativo no inicia o presenta errores

Inicio: `p16`. La consulta sigue este grafo sin cambiar la categoría.

| Pregunta | Sí | No | No estoy seguro |
| --- | --- | --- | --- |
| `p16` | `p17` | `p06` | `p17` |
| `p06` | `p04` | `p26` | `p26` |
| `p26` | `p12` | `p04` | `p12` |
| `p12` | `s_post_completado=verdadero` → `p10`<br>`s_sin_dispositivo_arranque=verdadero` → `p10`<br>resto → `p04` | `s_post_completado=verdadero` → `p10`<br>`s_sin_dispositivo_arranque=verdadero` → `p10`<br>resto → `p04` | `s_post_completado=verdadero` → `p10`<br>`s_sin_dispositivo_arranque=verdadero` → `p10`<br>resto → `p04` |
| `p10` | `p17` | `p17` | `p17` |
| `p17` | `p09` | `s_so_no_inicia=desconocido` → `@insuficiente`<br>resto → `p11` | `s_so_no_inicia=desconocido` → `@insuficiente`<br>resto → `p11` |
| `p09` | `p11` | `p11` | `p11` |
| `p11` | `@resultado` | `@resultado` | `@resultado` |
| `p04` | `@resultado` | `p05` | `p05` |
| `p05` | `@resultado` | `@resultado` | `@resultado` |

## Mi computadora se calienta o se apaga inesperadamente

Inicio: `p30`. La consulta sigue este grafo sin cambiar la categoría.

| Pregunta | Sí | No | No estoy seguro |
| --- | --- | --- | --- |
| `p30` | `p14` | `p14` | `p14` |
| `p14` | `p15` | `p15` | `p15` |
| `p15` | `s_calor_percibido=verdadero` → `p13`<br>`s_apagado_bajo_carga=verdadero` → `p13`<br>`s_ventilador_ruidoso=verdadero` → `p13`<br>resto → `@insuficiente` | `s_calor_percibido=verdadero` → `p13`<br>`s_apagado_bajo_carga=verdadero` → `p13`<br>`s_ventilador_ruidoso=verdadero` → `p13`<br>resto → `@insuficiente` | `s_calor_percibido=verdadero` → `p13`<br>`s_apagado_bajo_carga=verdadero` → `p13`<br>`s_ventilador_ruidoso=verdadero` → `p13`<br>resto → `@insuficiente` |
| `p13` | `@resultado` | `@resultado` | `@resultado` |

## Tengo problemas con Internet o Wi-Fi

Inicio: `p18`. La consulta sigue este grafo sin cambiar la categoría.

| Pregunta | Sí | No | No estoy seguro |
| --- | --- | --- | --- |
| `p18` | `@insuficiente` | `p25` | `@insuficiente` |
| `p25` | `p20` | `p29` | `p29` |
| `p20` | `p19` | `p19` | `p19` |
| `p29` | `p31` | `p19` | `p19` |
| `p31` | `p19` | `p19` | `p19` |
| `p19` | `@resultado` | `@resultado` | `@resultado` |

## No estoy seguro de cuál es el problema

Inicio: `p02`. La consulta sigue este grafo sin cambiar la categoría.

| Pregunta | Sí | No | No estoy seguro |
| --- | --- | --- | --- |
| `p02` | `p03` | `p03` | `p03` |
| `p03` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@resultado`<br>resto → `p07` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@resultado`<br>resto → `p07` | `s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@resultado`<br>resto → `p07` |
| `p07` | `p16` | `s_led_encendido=verdadero` → `p08`<br>`s_ventiladores_giran=verdadero` → `p08`<br>`s_led_encendido=falso` ∧ `s_ventiladores_giran=falso` → `@bloqueo_energia`<br>resto → `@insuficiente` | `@insuficiente` |
| `p08` | `@resultado` | `p06` | `p06` |
| `p16` | `p21` | `p06` | `p17` |
| `p06` | `p04` | `s_sin_imagen=verdadero` → `p04`<br>resto → `p26` | `s_sin_imagen=verdadero` → `p04`<br>resto → `p26` |
| `p26` | `p12` | `p04` | `p12` |
| `p12` | `s_post_completado=verdadero` → `p10`<br>`s_sin_dispositivo_arranque=verdadero` → `p10`<br>resto → `p04` | `s_post_completado=verdadero` → `p10`<br>`s_sin_dispositivo_arranque=verdadero` → `p10`<br>resto → `p04` | `s_post_completado=verdadero` → `p10`<br>`s_sin_dispositivo_arranque=verdadero` → `p10`<br>resto → `p04` |
| `p10` | `p17` | `p17` | `p17` |
| `p04` | `@resultado` | `p05` | `p05` |
| `p05` | `@resultado` | `@resultado` | `@resultado` |
| `p17` | `p09` | `s_so_no_inicia=verdadero` → `p11`<br>resto → `p09` | `s_so_no_inicia=verdadero` → `p11`<br>resto → `p09` |
| `p09` | `s_pantalla_azul=verdadero` → `p11`<br>resto → `@resultado` | `s_pantalla_azul=verdadero` → `p11`<br>resto → `@resultado` | `s_pantalla_azul=verdadero` → `p11`<br>resto → `@resultado` |
| `p21` | `p27` | `p27` | `p27` |
| `p27` | `p22` | `s_lentitud_programas=verdadero` → `p22`<br>resto → `p18` | `s_lentitud_programas=verdadero` → `p22`<br>resto → `p18` |
| `p22` | `p23` | `p23` | `p23` |
| `p23` | `p24` | `p24` | `p24` |
| `p24` | `p28` | `p28` | `p28` |
| `p28` | `s_congelamientos=verdadero` → `p11`<br>`s_proceso_disco_alto=verdadero` → `p11`<br>resto → `@resultado` | `s_congelamientos=verdadero` → `p11`<br>`s_proceso_disco_alto=verdadero` → `p11`<br>resto → `@resultado` | `s_congelamientos=verdadero` → `p11`<br>`s_proceso_disco_alto=verdadero` → `p11`<br>resto → `@resultado` |
| `p11` | `@resultado` | `s_congelamientos=verdadero` → `p05`<br>resto → `@resultado` | `s_congelamientos=verdadero` → `p05`<br>resto → `@resultado` |
| `p18` | `p30` | `p25` | `p30` |
| `p25` | `p20` | `p29` | `p29` |
| `p20` | `p19` | `p19` | `p19` |
| `p29` | `p31` | `p19` | `p19` |
| `p31` | `p19` | `p19` | `p19` |
| `p19` | `@resultado` | `@resultado` | `@resultado` |
| `p30` | `p14` | `p14` | `p14` |
| `p14` | `s_calor_percibido=verdadero` → `p15`<br>`s_apagado_bajo_carga=verdadero` → `p15`<br>resto → `p17` | `s_calor_percibido=verdadero` → `p15`<br>`s_apagado_bajo_carga=verdadero` → `p15`<br>resto → `p17` | `s_calor_percibido=verdadero` → `p15`<br>`s_apagado_bajo_carga=verdadero` → `p15`<br>resto → `p17` |
| `p15` | `s_calor_percibido=verdadero` → `p13`<br>`s_apagado_bajo_carga=verdadero` → `p13`<br>`s_ventilador_ruidoso=verdadero` → `p13`<br>resto → `p17` | `s_calor_percibido=verdadero` → `p13`<br>`s_apagado_bajo_carga=verdadero` → `p13`<br>`s_ventilador_ruidoso=verdadero` → `p13`<br>resto → `p17` | `s_calor_percibido=verdadero` → `p13`<br>`s_apagado_bajo_carga=verdadero` → `p13`<br>`s_ventilador_ruidoso=verdadero` → `p13`<br>resto → `p17` |
| `p13` | `@resultado` | `@resultado` | `@resultado` |

## Recorridos y aceptación

Las pruebas de `tests/test_rutas.py` ejecutan tres recorridos terminales por categoría, incluidos datos desconocidos, y casos adicionales de energía sin funcionamiento correcto, etapa POST, polaridad de `p10`, edición y cambio confirmado. La auditoría separada comprueba testigos interactivos para todas las reglas y diagnósticos y verifica que omisión o desconocido no satisfacen condiciones diagnósticas. Esto no equivale a precisión clínica ni a prueba con hardware real.

## Límites de fase

No hay selección heurística de preguntas, modelos B/C, inferencia multinivel ni comparación con 80 casos. La interfaz gráfica, visualización del razonamiento, PDF y evaluación final independiente siguen pendientes.
