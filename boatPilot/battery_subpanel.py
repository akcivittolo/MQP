from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame
)

from PyQt6.QtCore import Qt

class BatterySubpanel(QWidget):
    def __init__(self, telem_data):
        super().__init__()

        self.telem_data = telem_data

        # Create a layout
        layout = QVBoxLayout(self)

        # Title and battery remaining
        self.title = QLabel("Battery Remaining")
        self.battery_remaining = QLabel("Placeholder")

        # Add content to layout
        layout.addWidget(self.title)
        layout.addWidget(self.battery_remaining)

