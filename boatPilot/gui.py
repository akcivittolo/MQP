import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel
)

from telemetry_panel import TelemetryPanel
from map_panel import MapPanel
from control_panel import ControlPanel

from connection_logic import Connection
from telemetry_logic import TelemetryData

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instantiate necessary classes
        self.the_boat = Connection()
        self.telem_data = TelemetryData(self.the_boat)

        # Title and icon
        self.setWindowTitle("Boat Pilot")
        self.setWindowIcon(QIcon("boatIcon.png"))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Instantiate panels
        self.telemetry_panel = TelemetryPanel(self.telem_data)
        self.map_panel = MapPanel(self.telem_data)
        self.control_panel = ControlPanel(self.the_boat, self.telem_data)

        # Create the layout
        overall_H_layout = QHBoxLayout()

        # Add panels to layout
        overall_H_layout.addWidget(self.telemetry_panel)
        overall_H_layout.addWidget(self.map_panel)
        overall_H_layout.addWidget(self.control_panel)

        # Add layout to central widget
        central_widget.setLayout(overall_H_layout)
        

app = QApplication(sys.argv)

# CSS Styling
app.setStyleSheet("""
    QFrame#panel {
        background-color: gray; 
        border: 6px solid black;     
        border-radius: 0px;         
    }
    
    QLabel#title {
        background-color: gray;
        border: 6px solid black;
        border-radius: 0px;
        qproperty-alignment: 'AlignCenter';
        color: black;
        font-size: 20px;
        font-weight: bold;
        max-height: 50px;
    }
                

""")

window = MainWindow()
window.show()
app.exec()