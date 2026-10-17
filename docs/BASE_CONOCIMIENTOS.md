# Base de conocimientos — Fase 2

## Objetivo y alcance

Esta base recoge observaciones verificables y reglas SI–ENTONCES para orientar un diagnóstico de fallas en PC. El conocimiento es explícito, revisable y no utiliza aprendizaje automático. En esta fase se **valida** el catálogo; todavía no existe un motor que active reglas ni emita diagnósticos a usuarios.

Los tres archivos de `data/conocimiento/` tienen `"version": 1` y listas denominadas `hechos`, `diagnosticos` y `reglas`. El validador usa únicamente la biblioteca estándar. No se necesitan `scikit-learn` ni Matplotlib hasta la comparación experimental.

## Catálogo

Hay **20 síntomas**, todos de tipo `sintoma`. Por grupos:

| Grupo | Identificadores |
| --- | --- |
| Alimentación y POST | `s_no_enciende`, `s_led_encendido`, `s_ventiladores_giran`, `s_pitidos_ram_post`, `s_error_prueba_ram`, `s_reinicios_post` |
| Video | `s_sin_imagen`, `s_monitor_externo_funciona`, `s_artefactos_video` |
| Almacenamiento | `s_unidad_no_detectada`, `s_errores_entrada_salida`, `s_sin_dispositivo_arranque` |
| Temperatura | `s_temperatura_alta`, `s_apagado_bajo_carga`, `s_ventilador_ruidoso` |
| Sistema operativo | `s_so_no_inicia`, `s_pantalla_azul` |
| Conectividad | `s_sin_red`, `s_otros_equipos_conectan`, `s_wifi_deshabilitado` |

Hay **11 diagnósticos**: ruta de alimentación (`d_ruta_alimentacion`), RAM (`d_memoria_ram`), pantalla principal (`d_pantalla_principal`), subsistema de video (`d_subsistema_video`), detección y salud de almacenamiento (`d_deteccion_almacenamiento`, `d_salud_almacenamiento`), sobrecalentamiento (`d_sobrecalentamiento`), arranque y error crítico del sistema (`d_arranque_so`, `d_error_critico_so`), Wi-Fi inhabilitado y conectividad local (`d_wifi_inhabilitado`, `d_conectividad_local`). Cada uno incluye descripción, categoría y recomendaciones. Los nombres expresan el nivel de certeza disponible: algunos señalan un área de revisión, no una pieza confirmada.

Las **23 reglas** están agrupadas por esas mismas áreas. Algunas condiciones más específicas refuerzan una regla general y pueden llegar a la misma conclusión; esta coincidencia no debe sumarse como probabilidad. La resolución de coincidencias y conflictos se definirá al implementar el motor. Ninguna regla infiere daño de RAM únicamente por reinicios, fallo de almacenamiento únicamente por falta de arranque, ni sobrecalentamiento únicamente por apagados: se exige una señal específica adicional.

## Contrato de datos

Un hecho tiene `id`, `nombre`, `descripcion` y `tipo` (`sintoma` o, para fases futuras, `derivado`). Una observación de un hecho toma exactamente uno de los estados `verdadero`, `falso`, `desconocido`. Los hechos omitidos se normalizan a `desconocido`. `falso` significa que el síntoma se comprobó y no se observó; no significa que no se preguntó.

Cada regla tiene `id`, una lista no vacía de `condiciones`, una `conclusion` y una `explicacion`. Las condiciones son una conjunción: todas deben satisfacerse. Cada condición identifica un hecho y exige `verdadero` o `falso`. Una observación `desconocido` no satisface ninguno de esos requisitos. Las reglas actuales concluyen diagnósticos. El formato admite que reglas futuras concluyan un hecho `derivado` con estado verdadero o falso, lo que permitirá encadenamiento hacia adelante sin alterar el formato de observaciones.

El validador rechaza JSON ilegible, versión no compatible, campos faltantes o extras, tipos incorrectos, textos vacíos, IDs duplicados, referencias no definidas, condiciones repetidas o contradictorias, estados inválidos y conclusiones a síntomas o a la propia condición. Devuelve mensajes con la ubicación del error. La validación es estática: no demuestra que una hipótesis sea correcta en un caso real.

## Decisiones técnicas y límites

- El código POST debe verificarse con el manual del fabricante; un pitido genérico no se etiqueta como fallo de RAM.
- La ausencia de unidad se refiere a BIOS/UEFI, no solo al explorador de archivos. Los errores de E/S motivan preservar datos antes de cambiar hardware.
- La temperatura alta requiere una medición y comparación con el rango del fabricante o evidencia de limitación térmica. Ventilador ruidoso o apagado por sí solos no justifican esa conclusión.
- Que otros equipos conecten a la red localiza las primeras pruebas en este equipo, pero no identifica aún DNS, adaptador, cable o router como causa.
- Los diagnósticos pueden coexistir y las reglas más específicas pueden coincidir con otras generales. El orden, conflicto, trazabilidad de activación y grado de conclusión pertenecen a la Fase 3 y posteriores.
- La base aún no se ha contrastado con los 80 casos ni con técnicos externos. La precisión y cobertura son desconocidas; se medirán solo con casos de referencia independientes en las fases autorizadas.

## Comprobación reproducible

Desde la raíz ejecutar `python validar_conocimiento.py` y `python -m unittest discover -s tests -v`. En la ejecución de la Fase 2 ambos comandos terminaron correctamente: 20 hechos, 11 diagnósticos, 23 reglas y 6 pruebas superadas. Estas pruebas comprueban integridad de datos y manejo de estados; no prueban eficacia diagnóstica.
