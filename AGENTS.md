# Reglas de desarrollo del proyecto

1. Trabajar solo en la fase autorizada por el usuario. No iniciar fases posteriores ni crear tags de entrega antes del cierre expresamente autorizado.
2. Mantener separados conocimiento JSON, representación de hechos, inferencia, evaluación e interfaz.
3. Preservar la distinción entre `verdadero`, `falso` y `desconocido`. La falta de respuesta nunca equivale a una negación.
4. Formular conclusiones proporcionales a la evidencia; una regla puede producir una hipótesis, no una confirmación clínica o física de una pieza.
5. No presentar prioridades de reglas como probabilidades ni describir refinamientos simbólicos como aprendizaje automático.
6. Validar todo cambio de conocimiento con `python validar_conocimiento.py` y ejecutar `python -m unittest discover -s tests -v` cuando esté autorizado el acceso a los casos finales. Si la reserva no puede leerse, ejecutar solo pruebas que no la carguen y registrar que la batería global queda pendiente.
7. Añadir pruebas para correcciones importantes. No cambiar expectativas de pruebas para ocultar errores ni inventar ejecuciones o métricas.
8. Actualizar `CHECKLIST.md` y la documentación de la fase con resultados realmente observados, archivos modificados y limitaciones.
9. Proteger los 20 casos finales reservados: no abrirlos, inspeccionarlos, ejecutarlos ni usarlos para ajustar reglas o seleccionar modelos durante el desarrollo. Mantener su archivo fuera de Git y GitHub.
10. Mantener los tags de entrega inmutables y no publicar commits o tags en un remoto sin autorización.

## Estado y documentación vigente

- El Avance 1 está cerrado. El usuario autorizó el cierre del Avance 2 como versión académica `avance-2`: se implementaron y compararon A, B y C, y el Modelo C quedó seleccionado y congelado para la entrega final. La consola todavía usa A como modelo predeterminado.
- Los seis documentos principales son `docs/AVANCE_1.md`, `docs/AVANCE_2.md`, `docs/BASE_CONOCIMIENTOS.md`, `docs/PREGUNTAS.md`, `docs/PROTOCOLO_EVALUACION_AVANCE_2.md` y `docs/RESULTADOS_EXPERIMENTALES_AVANCE_2.md`.
- `docs/REVISION_CASOS_ETAPA_4_1.md` es el séptimo documento y debe permanecer en esa ruta: su contenido y su ruta están protegidos por los manifiestos de la evaluación y la selección.

## Congelación y reserva final

- `data/evaluacion/MANIFIESTO_SELECCION.json` fija las huellas de 44 archivos. No modificar ni mover archivos protegidos, resultados experimentales, manifiestos o huellas durante la consolidación documental. `python verificar_seleccion.py` comprueba la selección sin leer los casos finales.
- El archivo `data/evaluacion/casos_finales_reservados.json` está excluido mediante `.gitignore`. No ejecutar `validar_casos.py`, la batería global de pruebas ni otros comandos que lo carguen mientras siga vigente la prohibición de acceso; documentar las pruebas seguras que sí se ejecuten.
- Mantener separada la evaluación de desarrollo de la evaluación final y no publicar la rama experimental de respaldo sin autorización expresa.
