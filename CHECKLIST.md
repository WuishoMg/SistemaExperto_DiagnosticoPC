# Estado del proyecto

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
- `python -m unittest discover -s tests -v`: **correcto**; 14 pruebas, 0 fallos.
- `python diagnosticar.py --respuestas ejemplos/ram.json`: **correcto**; hipótesis principal de RAM, reglas `r_ram_reinicio_post` y `r_ram_codigo_post`, hechos y recomendaciones impresos.
- Pruebas funcionales en subproceso: consulta interactiva de 20 preguntas, ejemplo RAM y ejemplo sin conclusión; todos terminaron con código 0.
- Incidencia corregida: el subproceso de pruebas emitía texto con la codificación local de Windows; se fijó UTF-8 en la captura de pruebas y se repitió la suite completa.
- [ ] Validación del usuario y autorización expresa para cerrar el Avance 1 y crear `avance-1`.

## Fases siguientes — Pendientes de autorización

- [ ] Fases 4–6: Modelos B y C, 80 casos, comparación de 60 casos e informe del Avance 2.
- [ ] Fases 7–8: evaluación final reservada, interfaz e informe final.
