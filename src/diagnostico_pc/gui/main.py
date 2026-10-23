"""Arranque de Qt Quick."""

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .bridge import PuenteDiagnostico
from diagnostico_pc.preguntas import ErrorPreguntas
from diagnostico_pc.rutas import ErrorRutas
from diagnostico_pc.validacion import ErrorConocimiento


def main() -> int:
    app = QGuiApplication(sys.argv)
    fuente_windows = Path("C:/Windows/Fonts/segoeui.ttf")
    if fuente_windows.is_file() and QFontDatabase.addApplicationFont(str(fuente_windows)) >= 0:
        app.setFont(QFont("Segoe UI"))
    motor_qml = QQmlApplicationEngine()
    try:
        puente = PuenteDiagnostico()
    except (ErrorConocimiento, ErrorPreguntas, ErrorRutas, ValueError, OSError) as error:
        print(f"No se pudo iniciar la interfaz gráfica: {error}", file=sys.stderr)
        return 2
    motor_qml.rootContext().setContextProperty("diagnostico", puente)
    motor_qml.load(QUrl.fromLocalFile(str(Path(__file__).with_name("qml") / "Main.qml")))
    if not motor_qml.rootObjects():
        return 2
    return app.exec()
