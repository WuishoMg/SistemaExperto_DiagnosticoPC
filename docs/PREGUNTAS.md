# Cuestionario visible del Avance 1

Las preguntas y ayudas se cargan de `data/interfaz/preguntas.json`; esta tabla permite revisar su redacción y polaridad. El ID de hecho se muestra **solo en esta documentación técnica**, nunca como pregunta en la consola. `V` significa `verdadero` y `F` significa `falso`. Para las 20 preguntas, **No estoy seguro → `desconocido`**. La respuesta ausente en el archivo JSON técnico también queda desconocida.

| Nº | Hecho interno | Pregunta visible | Ayuda mostrada | Sí → | No → |
| ---: | --- | --- | --- | :---: | :---: |
| 1 | `s_no_enciende` | ¿Notas alguna señal de encendido al presionar el botón de la computadora? | Por ejemplo, una luz que se prende o el sonido de un ventilador. Si no ocurre nada, responde No. | F | V |
| 2 | `s_led_encendido` | ¿Se enciende alguna luz de la computadora cuando presionas el botón de encendido? | Observa las luces de la computadora, no la luz del monitor o del cargador. | V | F |
| 3 | `s_ventiladores_giran` | ¿Escuchas o ves que gira algún ventilador de la computadora al encenderla? | Puede sentirse aire saliendo por una rejilla. No abras el equipo para comprobarlo; si no puedes saberlo, elige No estoy seguro. | V | F |
| 4 | `s_pitidos_ram_post` | ¿Al encenderla escuchas pitidos que el manual del equipo identifica como un problema de memoria? | La memoria guarda datos mientras la computadora trabaja. No cualquier pitido indica esta falla; si no consultaste el manual, elige No estoy seguro. | V | F |
| 5 | `s_error_prueba_ram` | ¿Una prueba de memoria de la computadora mostró errores? | Una prueba de memoria es un programa que revisa esa pieza. Si no ejecutaste una prueba, elige No estoy seguro. | V | F |
| 6 | `s_reinicios_post` | ¿La computadora se reinicia varias veces antes de que aparezca Windows u otro sistema? | Observa si vuelve una y otra vez al logo inicial sin llegar a la pantalla de inicio de sesión. | V | F |
| 7 | `s_sin_imagen` | ¿Aparece alguna imagen en la pantalla principal al encender la computadora? | Cuenta también un logo o un mensaje de inicio. Si la pantalla queda completamente negra, responde No. | F | V |
| 8 | `s_monitor_externo_funciona` | ¿Aparece imagen al conectar la computadora a otra pantalla que sabes que funciona? | Puede ser otro monitor o un televisor conectado con un cable adecuado. Si no hiciste esta prueba, elige No estoy seguro. | V | F |
| 9 | `s_artefactos_video` | ¿Ves líneas, cuadros o colores extraños que permanecen en la imagen? | Busca distorsiones que no sean reflejos ni suciedad sobre la pantalla. | V | F |
| 10 | `s_unidad_no_detectada` | ¿Aparece la unidad donde está instalado el sistema en la configuración inicial de la computadora? | La unidad es el disco o memoria interna. Esa configuración suele llamarse BIOS o UEFI y se abre antes de Windows; si no la revisaste, elige No estoy seguro. | F | V |
| 11 | `s_errores_entrada_salida` | ¿La computadora muestra errores al leer o guardar archivos en la unidad? | Busca mensajes de error de lectura o escritura del disco. Que funcione lento, por sí solo, no cuenta como este error. | V | F |
| 12 | `s_sin_dispositivo_arranque` | ¿Al encenderla aparece un mensaje que dice que no se encontró un dispositivo para iniciar? | Por ejemplo, un mensaje como 'No bootable device' antes de que aparezca Windows. | V | F |
| 13 | `s_temperatura_alta` | ¿Una medición muestra que alguna pieza supera su temperatura recomendada? | Compara una lectura de temperatura con el límite indicado por el fabricante. Sentir caliente la carcasa no basta; si no mediste, elige No estoy seguro. | V | F |
| 14 | `s_apagado_bajo_carga` | ¿La computadora se apaga sola al jugar o usar un programa exigente? | Debe apagarse de golpe mientras trabaja, no entrar en reposo después de estar inactiva. | V | F |
| 15 | `s_ventilador_ruidoso` | ¿Escuchas un ventilador mucho más fuerte de lo habitual mientras usas la computadora? | Busca un ruido de aire o del ventilador, no sonido de los altavoces. | V | F |
| 16 | `s_so_no_inicia` | ¿Windows u otro sistema termina de iniciar y te deja usar la computadora? | Si se queda en el logo o en una pantalla de reparación, responde No. Si ni siquiera enciende, elige No estoy seguro. | F | V |
| 17 | `s_pantalla_azul` | ¿Aparece una pantalla azul con error o un aviso de fallo grave mientras usas la computadora? | Debe ser un aviso de fallo del sistema; un fondo azul normal no cuenta. | V | F |
| 18 | `s_sin_red` | ¿Funciona en esta computadora la conexión a la red que intentas usar? | Prueba abrir una página si usas Internet, o un recurso de tu red local. Si no hiciste la prueba, elige No estoy seguro. | F | V |
| 19 | `s_otros_equipos_conectan` | ¿Otros dispositivos pueden usar la misma red al mismo tiempo? | Por ejemplo, un teléfono conectado a la misma red de casa mientras compruebas la computadora. | V | F |
| 20 | `s_wifi_deshabilitado` | ¿El Wi-Fi de esta computadora está activado y el modo avión apagado? | Wi-Fi es la conexión inalámbrica. Revisa el icono o la configuración de red; si no puedes comprobarlo, elige No estoy seguro. | F | V |

## Criterio de diseño

Seis preguntas (1, 7, 10, 16, 18 y 20) invierten la polaridad lógica del síntoma. El archivo declara `estado_si` y `estado_no` por pregunta; la función `Pregunta.estado_para` traduce las tres respuestas visibles. El motor recibe solo estados internos, por lo que las reglas y los ejemplos JSON mantienen su significado. La validación exige una pregunta por síntoma y rechaza IDs o hechos repetidos, ayudas vacías y mapeos Sí/No que no sean opuestos.
