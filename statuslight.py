from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QToolBar,
    QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QAction, QPainter, QColor

class StatusLight(QWidget):
    def __init__(self, color="gray", diameter=16, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._diameter = diameter
        self.setFixedSize(diameter, diameter)

    def setColor(self, color):
        """Update the circle color dynamically."""
        self._color = QColor(color)
        self.update()  # triggers a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self._diameter, self._diameter)