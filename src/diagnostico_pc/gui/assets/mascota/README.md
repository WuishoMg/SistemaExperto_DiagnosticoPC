# Recursos opcionales de la mascota

La bienvenida busca primero `mascota-saludando.png` (con transparencia) y después `mascota-saludando.jpg`. Las otras poses actuales son `mascota-default1.png` para categorías, `mascota-escribiendo1.png` para preguntas, `mascota-analizando1.png` para análisis y `mascota-idea1.png` para la idea y los resultados. Si falta un archivo, la imagen se oculta y la consulta sigue funcionando.

Para otras poses, se admiten los nombres `seleccion`, `preguntas`, `analisis` y `resultados` con extensión PNG, WebP, SVG, GIF o JPG. PNG y SVG se muestran como imágenes estáticas; GIF y WebP se entregan a `AnimatedImage` cuando Qt pueda reproducirlos. Estos recursos son opcionales y no intervienen en el diagnóstico.
