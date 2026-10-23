"""Composición paginada del reporte técnico mediante Qt, sin inferir datos."""

from pathlib import Path

from PySide6.QtCore import QMarginsF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPageLayout, QPageSize, QPainter, QPdfWriter


VIOLETA = QColor("#6355FF")
TINTA = QColor("#211D41")
TENUE = QColor("#625E79")
LAVANDA = QColor("#F5F3FF")
BORDE = QColor("#E4DFFF")
ESTADOS = {
    "verdadero": (QColor("#E8F6F0"), QColor("#147653")),
    "falso": (QColor("#FFF1E5"), QColor("#995218")),
    "desconocido": (QColor("#F1F1F3"), QColor("#575963")),
}
MASCOTA = Path(__file__).with_name("assets") / "mascota" / "mascota-analizando1.png"
ALINEAR = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


def datos_reporte(
    resultado: dict, observaciones: dict[str, str], hechos: dict | None = None,
    registradas: set[str] | None = None,
) -> dict:
    """Prepara la instantánea sin convertir desconocidos ni alterar el orden de C."""
    hechos = hechos or {}
    hipotesis = ([resultado["principal"]] if resultado["principal"] else []) + list(resultado["alternativas"])
    return {
        "observaciones": [
            {"id": clave, "nombre": hechos.get(clave, {}).get("nombre", clave), "estado": estado}
            for clave, estado in sorted(observaciones.items()) if registradas is None or clave in registradas
        ],
        "hipotesis": hipotesis,
        "criterios": resultado["criterios"],
        "derivados": [
            {**hecho, "nombre": hechos.get(hecho["hechoId"], {}).get("nombre", hecho["hechoId"])}
            for hecho in resultado["hechosDerivados"]
        ],
        "trazas": resultado["trazas"],
        "sin_conclusion": resultado["explicacionSinConclusion"],
        "prioridad": resultado["explicacionPrioridad"],
        "aviso": resultado["aviso"],
    }


def prioridad_publica(explicacion: str) -> str:
    """Retira solo el apéndice comparativo del texto académico de C."""
    for inicio in (" B y C conservan el mismo orden", " El orden difiere del de B"):
        if inicio in explicacion:
            return explicacion.split(inicio, 1)[0]
    return explicacion


class Pagina:
    """Mantiene toda la tinta dentro del área de contenido reservada."""

    def __init__(self, escritor: QPdfWriter):
        self.escritor = escritor
        self.pintor = QPainter(escritor)
        self.pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        recto = escritor.pageLayout().fullRectPoints()
        self.ancho_pagina = float(recto.width())
        self.alto_pagina = float(recto.height())
        self.x = 46.0
        self.w = self.ancho_pagina - 92.0
        self.inicio = 43.0
        self.limite = self.alto_pagina - 77.0
        self.y = self.inicio
        self.numero = 1
        self.seccion_actual = ""
        self.fondo()

    def fondo(self):
        self.pintor.fillRect(QRectF(0, 0, self.ancho_pagina, self.alto_pagina), QColor("#FFFFFF"))

    def fuente(self, puntos=9, negrita=False):
        fuente = QFont("Arial")
        fuente.setPointSizeF(puntos)
        fuente.setBold(negrita)
        self.pintor.setFont(fuente)
        return QFontMetricsF(fuente)

    def pie(self):
        base = self.alto_pagina - 48
        self.pintor.fillRect(QRectF(self.x, base - 10, self.w, 1), BORDE)
        self.fuente(8)
        self.pintor.setPen(TENUE)
        self.pintor.drawText(QRectF(self.x, base, self.w * 0.7, 18), ALINEAR,
                             "Reporte técnico de diagnóstico")
        self.pintor.drawText(QRectF(self.x, base, self.w, 18),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             f"Página {self.numero}")
        self.pintor.setPen(VIOLETA)
        self.pintor.drawText(QRectF(self.x, base + 18, self.w, 15), ALINEAR,
                             "Del síntoma a la solución.")

    def asegurar(self, altura, *, continuar=True):
        if self.y + altura <= self.limite:
            return
        self.pie()
        if not self.escritor.newPage():
            raise OSError("No se pudo crear una nueva página del PDF.")
        self.numero += 1
        self.y = self.inicio
        self.fondo()
        if continuar and self.seccion_actual:
            self.pintor.fillRect(QRectF(self.x, self.y, self.w, 27), LAVANDA)
            self.pintor.fillRect(QRectF(self.x, self.y, 3, 27), VIOLETA)
            self.fuente(9, True)
            self.pintor.setPen(TINTA)
            self.pintor.drawText(QRectF(self.x + 11, self.y, self.w - 22, 27), ALINEAR,
                                 self.seccion_actual + " (continuación)")
            self.y += 36

    @staticmethod
    def lineas(texto, metrica, ancho):
        resultado = []
        for parrafo in str(texto).splitlines() or [""]:
            actual = ""
            for palabra in parrafo.split():
                candidato = f"{actual} {palabra}".strip()
                if metrica.horizontalAdvance(candidato) <= ancho:
                    actual = candidato
                    continue
                if actual:
                    resultado.append(actual)
                    actual = ""
                while palabra and metrica.horizontalAdvance(palabra) > ancho:
                    corte = 1
                    while corte < len(palabra) and metrica.horizontalAdvance(palabra[:corte + 1]) <= ancho:
                        corte += 1
                    resultado.append(palabra[:corte])
                    palabra = palabra[corte:]
                actual = palabra
            resultado.append(actual)
        return resultado

    def texto(self, texto, *, puntos=9, color=TENUE, negrita=False, sangria=0, despues=5):
        metrica = self.fuente(puntos, negrita)
        alto = metrica.lineSpacing() + 2
        for linea in self.lineas(texto, metrica, self.w - sangria):
            self.asegurar(alto)
            self.fuente(puntos, negrita)
            self.pintor.setPen(color)
            self.pintor.drawText(QRectF(self.x + sangria, self.y, self.w - sangria, alto), ALINEAR, linea)
            self.y += alto
        self.y += despues

    def seccion(self, titulo):
        self.asegurar(55, continuar=False)
        self.y += 10
        self.pintor.fillRect(QRectF(self.x, self.y, self.w, 29), LAVANDA)
        self.pintor.fillRect(QRectF(self.x, self.y, 3, 29), VIOLETA)
        self.fuente(11, True)
        self.pintor.setPen(TINTA)
        self.pintor.drawText(QRectF(self.x + 11, self.y, self.w - 22, 29), ALINEAR, titulo)
        self.y += 36
        self.seccion_actual = titulo

    def subtitulo(self, titulo):
        self.asegurar(35)
        self.texto(titulo, puntos=10, color=TINTA, negrita=True, despues=3)

    def estado(self, nombre, clave, valor):
        metrica = self.fuente(9, True)
        lineas = self.lineas(nombre, metrica, self.w - 150)
        alto_linea = metrica.lineSpacing() + 2
        altura = max(43, len(lineas) * alto_linea + 19)
        self.asegurar(altura + 6)
        fondo, tinta = ESTADOS.get(valor, ESTADOS["desconocido"])
        self.pintor.fillRect(QRectF(self.x, self.y, self.w, altura), QColor("#FAF9FF"))
        self.pintor.fillRect(QRectF(self.x + self.w - 115, self.y + 9, 105, 23), fondo)
        self.fuente(8, True)
        self.pintor.setPen(tinta)
        self.pintor.drawText(QRectF(self.x + self.w - 115, self.y + 9, 105, 23),
                             Qt.AlignmentFlag.AlignCenter, valor.capitalize())
        self.fuente(9, True)
        self.pintor.setPen(TINTA)
        for indice, linea in enumerate(lineas):
            self.pintor.drawText(QRectF(self.x + 11, self.y + 5 + indice * alto_linea,
                                        self.w - 150, alto_linea), ALINEAR, linea)
        self.fuente(7.5)
        self.pintor.setPen(TENUE)
        self.pintor.drawText(QRectF(self.x + 11, self.y + altura - 15, self.w - 150, 12), ALINEAR, clave)
        self.y += altura + 6

    def comprobacion(self, numero, recomendacion, evidencia):
        metrica = self.fuente(9, True)
        alto = metrica.lineSpacing() + 2
        lineas = self.lineas(f"{numero}. {recomendacion}", metrica, self.w - 20)
        evidencia_lineas = self.lineas("Reglas de soporte de la hipótesis: " + evidencia,
                                       self.fuente(8), self.w - 20) if evidencia else []
        altura = 12 + len(lineas) * alto + len(evidencia_lineas) * (self.fuente(8).lineSpacing() + 2) + 30
        if altura > self.limite - self.inicio:
            self.texto(f"{numero}. {recomendacion}", color=TINTA, negrita=True)
            if evidencia:
                self.texto("Reglas de soporte de la hipótesis: " + evidencia, puntos=8)
            self.texto("[ ] Pendiente     [ ] Realizada     [ ] No aplicable", puntos=8)
            self.texto("Observaciones del técnico: ______________________________", puntos=8)
            return
        self.asegurar(altura + 7)
        inicio = self.y
        self.pintor.fillRect(QRectF(self.x, inicio, self.w, altura), LAVANDA)
        self.y += 9
        self.texto(f"{numero}. {recomendacion}", color=TINTA, negrita=True, sangria=10, despues=2)
        if evidencia:
            self.texto("Reglas de soporte de la hipótesis: " + evidencia,
                       puntos=8, sangria=10, despues=2)
        self.fuente(8)
        self.pintor.setPen(TINTA)
        self.pintor.drawText(QRectF(self.x + 10, self.y, self.w - 20, 15), ALINEAR,
                             "[ ] Pendiente     [ ] Realizada     [ ] No aplicable")
        self.y += 15
        self.pintor.setPen(BORDE)
        self.fuente(7.5)
        self.pintor.setPen(TENUE)
        self.pintor.drawText(QRectF(self.x + 10, self.y, 125, 15), ALINEAR,
                             "Observaciones del técnico:")
        self.pintor.setPen(BORDE)
        self.pintor.drawLine(int(self.x + 137), int(self.y + 11), int(self.x + self.w - 12), int(self.y + 11))
        self.y = inicio + altura + 7

    def terminar(self):
        self.pie()
        self.pintor.end()


def dibujar_reporte(ruta: Path, datos: dict) -> None:
    escritor = QPdfWriter(str(ruta))
    escritor.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    escritor.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)
    escritor.setResolution(72)
    escritor.setTitle("Reporte técnico de diagnóstico")
    pagina = Pagina(escritor)
    try:
        imagen = QImage(str(MASCOTA))
        pagina.asegurar(108)
        if not imagen.isNull():
            escala = min(87 / imagen.width(), 87 / imagen.height())
            ancho, alto = imagen.width() * escala, imagen.height() * escala
            pagina.pintor.drawImage(QRectF(pagina.x + pagina.w - ancho, pagina.y, ancho, alto), imagen)
        pagina.pintor.fillRect(QRectF(pagina.x, pagina.y, 4, 83), VIOLETA)
        pagina.fuente(20, True)
        pagina.pintor.setPen(TINTA)
        pagina.pintor.drawText(QRectF(pagina.x + 15, pagina.y + 2, pagina.w - 125, 62),
                               Qt.TextFlag.TextWordWrap, "Reporte técnico de diagnóstico")
        pagina.y += 96
        pagina.texto("Hipótesis orientativas para revisión técnica; no confirman por sí solas una falla.", despues=7)

        pagina.seccion("Observaciones de la consulta")
        for dato in datos["observaciones"]:
            pagina.estado(dato["nombre"], dato["id"], dato["estado"])
        if not datos["observaciones"]:
            pagina.texto("No se registraron observaciones.")

        pagina.seccion("Resultado de la consulta")
        if not datos["hipotesis"]:
            pagina.subtitulo("Sin hipótesis concluyente")
            pagina.texto(datos["sin_conclusion"] or "No hay evidencia suficiente para una hipótesis.")
        for indice, hipotesis in enumerate(datos["hipotesis"]):
            pagina.subtitulo(("Hipótesis principal: " if indice == 0 else f"Hipótesis alternativa {indice}: ")
                             + hipotesis["nombre"])
            pagina.texto(hipotesis["descripcion"])
            if indice < len(datos["criterios"]):
                criterio = datos["criterios"][indice]
                pagina.texto(f"Criterios ordinales: {criterio['calidadTexto']}; "
                             f"{criterio['especificidad']} observaciones originales distintas; "
                             f"{criterio['prioridadTexto']}.", puntos=8)
            if hipotesis["recomendaciones"]:
                pagina.texto("Recomendaciones", color=VIOLETA, negrita=True, despues=2)
                for recomendacion in hipotesis["recomendaciones"]:
                    pagina.texto("• " + recomendacion, sangria=10, despues=2)
            if hipotesis["reglas"]:
                pagina.texto("Reglas y evidencias de soporte", color=VIOLETA, negrita=True, despues=2)
                for regla in hipotesis["reglas"]:
                    pagina.asegurar(49)
                    pagina.texto(f"{regla['id']}: {regla['explicacion']}", puntos=8, sangria=10, despues=1)
                    condiciones = "; ".join(f"{c['nombre']} ({c['estado']})" for c in regla["condiciones"])
                    if condiciones:
                        pagina.texto("Evidencia: " + condiciones, puntos=8, sangria=10, despues=3)
        if datos["prioridad"]:
            pagina.texto(prioridad_publica(datos["prioridad"]), puntos=8)

        pagina.seccion("Hechos derivados")
        for hecho in datos["derivados"]:
            pagina.estado(hecho["nombre"], hecho["hechoId"], hecho["estado"])
            pagina.texto("Reglas: " + ", ".join(hecho["reglas"]), puntos=8, sangria=10, despues=2)
        if not datos["derivados"]:
            pagina.texto("No se derivaron hechos adicionales.")

        pagina.seccion("Trazas de razonamiento")
        for traza in datos["trazas"]:
            pagina.subtitulo(f"Nivel {traza['nivel']} · Regla {traza['reglaId']}")
            pagina.texto(traza["explicacion"], puntos=8, despues=2)
            for condicion in traza["condiciones"]:
                pagina.texto(f"Condición: {condicion['nombre']} [{condicion['hechoId']}] — {condicion['estado']}",
                             puntos=8, sangria=10, despues=1)
            tipo = "Hipótesis" if traza["conclusionTipo"] == "diagnostico" else "Hecho derivado"
            estado = f" — {traza['conclusionEstado']}" if traza["conclusionEstado"] else ""
            pagina.texto(f"Conclusión ({tipo}): {traza['conclusionId']}{estado}",
                         puntos=8, sangria=10, despues=6)
        if not datos["trazas"]:
            pagina.texto("No hay reglas activadas para esta consulta.")

        pagina.seccion("Guía de verificación técnica")
        pagina.texto("Cada comprobación procede de una recomendación del resultado. "
                     "Registre lo observado y confirme la causa mediante revisión técnica.", puntos=8)
        numero = 0
        for hipotesis in datos["hipotesis"]:
            if hipotesis["recomendaciones"]:
                pagina.subtitulo(hipotesis["nombre"])
            evidencia = ", ".join(regla["id"] for regla in hipotesis["reglas"])
            for recomendacion in hipotesis["recomendaciones"]:
                numero += 1
                pagina.comprobacion(numero, recomendacion, evidencia)
        if not numero:
            pagina.texto("El resultado no ofrece comprobaciones específicas adicionales.")
        if datos["hipotesis"]:
            pagina.texto(datos["aviso"], puntos=8, color=TINTA, negrita=True)
    finally:
        pagina.terminar()
    del pagina
    del escritor
    if not ruta.is_file() or ruta.stat().st_size == 0:
        raise OSError("No se pudo generar el archivo PDF.")
