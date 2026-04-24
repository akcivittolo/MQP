import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSplitter,
    QToolBar,
)

from toolbar_statusbar_ui.toolbar_panel import ToolbarPanel
from toolbar_statusbar_ui.statusbar_panel import StatusbarPanel
from telemetry_ui.telemetry_panel import TelemetryPanel
from map_ui.map_panel import MapPanel
from control_ui.control_panel import ControlPanel

from core_logic.connection_logic import ConnectionData
from core_logic.telemetry_logic import TelemetryData
from core_logic.mission_planning_logic import MissionData

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instantiate necessary classes
        self.connection_data = ConnectionData()
        self.telem_data = TelemetryData(self.connection_data)
        self.mission_data = MissionData(self.connection_data)

        # Toolbar
        self.toolbar_panel = ToolbarPanel(self.connection_data, self.telem_data)
        self.addToolBar(self.toolbar_panel)

        # Statusbar
        self.statusbar_panel = StatusbarPanel(self.connection_data, self.telem_data)
        self.setStatusBar(self.statusbar_panel)

        # Title and icon
        self.setWindowTitle("Boat Pilot")
        self.setWindowIcon(QIcon("assets/boatIcon.png"))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Instantiate panels
        self.telemetry_panel = TelemetryPanel(self.connection_data, self.telem_data)
        self.map_panel = MapPanel(self.telem_data, self.mission_data)
        self.control_panel = ControlPanel(self.connection_data, self.telem_data, self.mission_data)

        # Create the layout
        overall_H_layout = QHBoxLayout()

        # Create a splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Add panels to spliter
        splitter.addWidget(self.telemetry_panel)
        splitter.addWidget(self.map_panel)
        splitter.addWidget(self.control_panel)

        # Add splitter to layout
        overall_H_layout.addWidget(splitter)

        # Add layout to central widget
        central_widget.setLayout(overall_H_layout)

        # # Add toolbar
        # toolbar = QToolBar("Main")
        # self.addToolBar(toolbar)

        # connect_action = QAction(QIcon.fromTheme("network-connect"), "Connect", self)
        # toolbar.addAction(connect_action)
        

# app = QApplication(sys.argv)


# window = MainWindow()
# window.show()
# app.exec()