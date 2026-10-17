# Reglas de desarrollo del proyecto

1. Trabajar solo en la fase autorizada por el usuario. No iniciar fases posteriores ni crear tags de entrega antes del cierre expresamente autorizado.
2. Mantener separados conocimiento JSON, representación de hechos, inferencia, evaluación e interfaz.
3. Preservar la distinción entre `verdadero`, `falso` y `desconocido`. La falta de respuesta nunca equivale a una negación.
4. Formular conclusiones proporcionales a la evidencia; una regla puede producir una hipótesis, no una confirmación clínica o física de una pieza.
5. No presentar prioridades de reglas como probabilidades ni describir refinamientos simbólicos como aprendizaje automático.
6. Validar todo cambio de conocimiento con `python validar_conocimiento.py` y ejecutar `python -m unittest discover -s tests -v`.
7. Añadir pruebas para correcciones importantes. No cambiar expectativas de pruebas para ocultar errores ni inventar ejecuciones o métricas.
8. Actualizar `CHECKLIST.md` y la documentación de la fase con resultados realmente observados, archivos modificados y limitaciones.
9. Proteger los 20 casos finales cuando se creen: no usarlos para ajustar reglas ni seleccionar modelos.
10. Mantener los tags de entrega inmutables y no publicar commits o tags en un remoto sin autorización.
