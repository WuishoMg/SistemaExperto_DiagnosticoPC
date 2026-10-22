# Sistema experto de diagnóstico de fallas en PC

Proyecto universitario de IA simbólica. **Avance 1 finalizado como versión académica reproducible.** El Modelo A obtiene hipótesis mediante reglas SI–ENTONCES y muestra las observaciones que las activaron. Su precisión diagnóstica en computadoras reales todavía no ha sido evaluada. No existen todavía los modelos B y C.

## Probar el cuestionario

Se requiere Python 3.11 o posterior; no hay paquetes externos. Desde la raíz del proyecto:

```powershell
python diagnosticar.py
```

Elige uno de los siete problemas. Cada ruta comienza con una pregunta relacionada con esa elección. La categoría permanece fija; cuando una respuesta impide seguir, la consola lo explica y ofrece iniciar otra consulta. Cambiar de categoría requiere confirmación y descarta las respuestas anteriores.

Responde con **1. Sí**, **2. No**, **3. No estoy seguro** o con `s/n/?`. Enter también equivale a «No estoy seguro» mientras se pregunta. Usa `v` para volver, `e` para editar una respuesta anterior, `c` para solicitar un cambio de categoría y `f` para finalizar con la evidencia disponible. Editar una respuesta descarta las posteriores porque el camino puede cambiar. Al terminar una ruta, Enter muestra el resultado disponible. Si video queda bloqueado por ausencia de señales de energía, se ofrece iniciar alimentación y no se presenta automáticamente un diagnóstico de otra ruta.

Una comprobación técnica que no realizaste puede contestarse «No estoy seguro». Esto registra `desconocido`, nunca `falso`. Las conclusiones son hipótesis o áreas de revisión; no identifican automáticamente una pieza averiada. El orden usual por especificidad de reglas no expresa probabilidad. Si hay temperatura alta medida, la consola presenta ese hallazgo antes que los indicios subjetivos.

La ruta de video diferencia un logotipo breve de imagen que permanece. En conectividad puedes indicar cortes intermitentes o una página concreta que falla aunque la página de prueba abra. En sistema puedes registrar un error ocurrido durante el uso; si no hay observaciones para identificar su causa, el resultado lo dirá explícitamente.

## Validación y ejemplos

```powershell
python validar_conocimiento.py
python -m unittest discover -s tests -v
python -m unittest discover -s auditoria -v
python diagnosticar.py --respuestas ejemplos/ram.json
python diagnosticar.py --respuestas ejemplos/sin_conclusion.json
```

`--respuestas` acepta un objeto JSON con IDs de hechos y estados internos `verdadero`, `falso` o `desconocido`; los omitidos quedan desconocidos. Los antiguos hechos compuestos `s_no_enciende`, `s_lentitud_o_congelamientos` y `s_proceso_consumo_alto` se retiraron: el programa indica los IDs separados que deben registrarse. No los convierte automáticamente, porque una respuesta compuesta no determina las dos observaciones individuales.

## Organización

- `data/conocimiento/`: 36 hechos, 18 diagnósticos y 42 reglas JSON.
- `data/interfaz/preguntas.json`: 36 preguntas, ayudas y polaridad visible.
- `data/interfaz/rutas.json`: grafo declarativo de siete categorías y tres transiciones por nodo.
- `src/diagnostico_pc/gestor_preguntas.py`: sesión, historial, retroceso y cambio explícito; no infiere diagnósticos.
- `src/diagnostico_pc/modelo_a.py`: motor de inferencia directa del Avance 1.
- `docs/PREGUNTAS.md`, `docs/REDISENO_RUTAS_AVANCE_1.md` y `docs/BASE_CONOCIMIENTOS.md`: catálogos y decisiones técnicas.
- `docs/AVANCE_1.md` y `CHECKLIST.md`: estado y resultados observados.

**Verificación de cierre:** `python validar_conocimiento.py` confirmó 36 hechos, 36 preguntas, 42 reglas, 18 diagnósticos y siete rutas. Pasaron 35 pruebas habituales y 10 de auditoría; ambos ejemplos JSON terminaron correctamente. La auditoría encontró testigos interactivos para 42/42 reglas y 18/18 diagnósticos, exploró exhaustivamente las seis rutas específicas y una muestra acotada de la ruta general. El tag anotado `avance-1` identifica la versión de cierre. Los modelos B y C, heurísticas avanzadas, 80 casos, interfaz gráfica y PDF siguen fuera del Avance 1.
