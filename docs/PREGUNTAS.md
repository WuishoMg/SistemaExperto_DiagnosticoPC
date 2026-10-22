# Preguntas visibles del Avance 1

El catálogo JSON es la fuente de texto, ayuda y polaridad. La ruta elige solo preguntas relacionadas con la categoría y con respuestas anteriores; las correcciones posteriores al rediseño se documentan en `AUDITORIA_COHERENCIA_AVANCE_1.md`. La consola acepta `1/2/3` o `s/n/?`. En todas las preguntas, «No estoy seguro» registra `desconocido`.

| ID | Hecho interno | Pregunta visible | Ayuda mostrada | Sí → | No → |
| --- | --- | --- | --- | :---: | :---: |
| `p02` | `s_led_encendido` | ¿Se enciende alguna luz de la computadora al pulsar el botón de encendido? | Mira el equipo, no la luz del monitor. | verdadero | falso |
| `p03` | `s_ventiladores_giran` | ¿Gira algún ventilador de la computadora al intentar encenderla? | Puedes escuchar el giro o sentir aire; no abras el equipo. | verdadero | falso |
| `p04` | `s_pitidos_ram_post` | ¿El manual del equipo identifica los pitidos de inicio como un problema de memoria? | Si no consultaste el significado de los pitidos, responde No estoy seguro. | verdadero | falso |
| `p05` | `s_error_prueba_ram` | ¿Una prueba de memoria de la computadora mostró errores? | Una prueba de memoria es un programa que revisa esa pieza. Si no ejecutaste una prueba, elige No estoy seguro. | verdadero | falso |
| `p06` | `s_reinicios_post` | ¿La computadora se reinicia repetidamente antes de mostrar el inicio del sistema? | Observa si vuelve a empezar antes del logotipo de Windows u otro sistema. | verdadero | falso |
| `p07` | `s_sin_imagen` | ¿La pantalla principal muestra alguna imagen al encender la computadora? | También cuenta un logotipo o mensaje de inicio. | falso | verdadero |
| `p08` | `s_monitor_externo_funciona` | ¿La imagen permanece visible al probar con otra pantalla que sabes que funciona? | Obsérvala también después del logotipo inicial. Si no hiciste la prueba, responde No estoy seguro. | verdadero | falso |
| `p09` | `s_artefactos_video` | ¿Ves distorsiones que permanecen en la imagen? | Por ejemplo, líneas o cuadros que no sean suciedad de la pantalla. | verdadero | falso |
| `p10` | `s_unidad_no_detectada` | ¿Aparece la unidad del sistema en la configuración inicial de la computadora? | Es el disco interno; si no revisaste esa pantalla, responde No estoy seguro. | falso | verdadero |
| `p11` | `s_errores_entrada_salida` | ¿Aparece algún error de acceso a los archivos de la unidad? | Por ejemplo, un aviso de que no se pudo leer un archivo. | verdadero | falso |
| `p12` | `s_sin_dispositivo_arranque` | ¿Aparece un mensaje que dice que no se encontró un dispositivo para iniciar? | Puede decir No bootable device. | verdadero | falso |
| `p13` | `s_temperatura_alta` | ¿Una medición supera el límite de temperatura indicado para alguna pieza? | Si no mediste ni conoces el límite, responde No estoy seguro. | verdadero | falso |
| `p14` | `s_apagado_bajo_carga` | ¿La computadora se apaga de golpe mientras ejecutas una tarea exigente? | Por ejemplo, durante un juego; el reposo normal no cuenta. | verdadero | falso |
| `p15` | `s_ventilador_ruidoso` | ¿Un ventilador suena mucho más fuerte de lo habitual durante el uso? | Piensa en ruido de aire, no de los altavoces. | verdadero | falso |
| `p16` | `s_so_no_inicia` | ¿El sistema termina de iniciar y te deja usar la computadora? | Si queda en el inicio o reparación, responde No. | falso | verdadero |
| `p17` | `s_pantalla_azul` | ¿Aparece una pantalla azul con un código de error? | Puede aparecer al iniciar o mientras usas el equipo. | verdadero | falso |
| `p18` | `s_sin_red` | ¿Puedes abrir una página web desde esta computadora ahora? | Prueba una página que normalmente funciona. | falso | verdadero |
| `p19` | `s_otros_equipos_conectan` | ¿Otro dispositivo de la misma red puede abrir esa página ahora? | Prueba, por ejemplo, un teléfono conectado a tu red de casa. | verdadero | falso |
| `p20` | `s_wifi_deshabilitado` | ¿Está encendido el Wi-Fi de esta computadora? | Mira el control de Wi-Fi; si no lo encuentras, responde No estoy seguro. | falso | verdadero |
| `p21` | `s_lentitud_programas` | ¿Tu computadora tarda demasiado en abrir programas? | Compáralo con su funcionamiento habitual. | verdadero | falso |
| `p22` | `s_espacio_sistema_bajo` | ¿El sistema te avisa que queda muy poco espacio en la unidad principal? | Es la unidad donde está instalado el sistema. Si no viste un aviso ni revisaste el espacio, elige No estoy seguro. | verdadero | falso |
| `p23` | `s_uso_memoria_alto` | ¿El uso de memoria se mantiene casi lleno mientras ocurre el problema? | Puedes verlo en el administrador de tareas; si no lo revisaste, responde No estoy seguro. | verdadero | falso |
| `p24` | `s_proceso_cpu_alto` | ¿Un programa mantiene casi al máximo el uso del procesador mientras ocurre el problema? | El administrador de tareas muestra el uso de cada programa. | verdadero | falso |
| `p25` | `s_conexion_wifi_intentada` | ¿Estás intentando conectar esta computadora mediante Wi-Fi? | Wi-Fi es la conexión inalámbrica. | verdadero | falso |
| `p26` | `s_post_completado` | ¿La computadora pasa de la pantalla inicial de la marca a otra pantalla de inicio? | Puede aparecer el inicio del sistema o un mensaje de arranque. | verdadero | falso |
| `p27` | `s_congelamientos` | ¿La computadora deja de responder mientras la utilizas? | Por ejemplo, no responde al ratón durante un rato. | verdadero | falso |
| `p28` | `s_proceso_disco_alto` | ¿Un programa mantiene casi al máximo el uso del disco mientras ocurre el problema? | Si no revisaste el uso del disco, responde No estoy seguro. | verdadero | falso |
| `p29` | `s_conexion_cable_intentada` | ¿Hay un cable de red conectado a esta computadora para usar Internet? | Es el cable que va al router o a una toma de red. | verdadero | falso |
| `p30` | `s_calor_percibido` | ¿La carcasa se siente mucho más caliente de lo habitual durante el uso? | Describe lo que notas al tocarla; no equivale a una temperatura medida. | verdadero | falso |
| `p31` | `s_aviso_cable_desconectado` | ¿La computadora muestra un aviso de que el cable de red está desconectado? | Si no puedes ver el estado de la conexión, responde No estoy seguro. | verdadero | falso |
| `p32` | `s_imagen_desaparece_tras_inicio` | ¿La imagen de la pantalla principal desaparece después del logotipo o mensaje inicial? | Responde Sí si viste una imagen breve y después la pantalla quedó sin imagen. Si permanece visible, responde No. | verdadero | falso |
| `p33` | `s_red_intermitente` | ¿La conexión de esta computadora deja de funcionar por momentos? | Piensa en cortes mientras usas Internet, aunque la página de prueba haya abierto ahora. | verdadero | falso |
| `p34` | `s_pagina_especifica_falla` | ¿Una página web concreta que necesitas usar falla ahora en esta computadora? | Prueba la página que motivó tu consulta. Si no la probaste ahora, responde No estoy seguro. | verdadero | falso |
| `p35` | `s_error_durante_uso` | ¿Aparece otro mensaje de error mientras usas el sistema después de iniciar? | Piensa en un mensaje diferente de la pantalla azul o del aviso de acceso a archivos ya preguntados. | verdadero | falso |
| `p36` | `s_otros_equipos_fallan_al_mismo_tiempo` | ¿Otro dispositivo de la misma red pierde la conexión al mismo tiempo? | Compáralos durante un corte real; si no lo observaste, responde No estoy seguro. | verdadero | falso |
| `p37` | `s_pagina_fallida_abre_en_otro` | ¿La página que falla aquí sí abre en otro dispositivo de la misma red? | Prueba la misma página en ambos equipos; si no hiciste la prueba, responde No estoy seguro. | verdadero | falso |

**Polaridad invertida:** `p07`, `p10`, `p16`, `p18` y `p20`. En particular, responder Sí a `p10` significa que la unidad **sí aparece** y por eso `s_unidad_no_detectada=falso`.

`p01` se retiró porque mezclaba señales distintas de encendido. Los IDs conservados mantienen su número. `p32–p37` registran las observaciones mínimas para I-01 a I-03; `p35` solo orienta un cierre sin causa inferida. Cada pregunta corresponde a un único hecho observable. Las comprobaciones no realizadas se contestan como desconocidas.
