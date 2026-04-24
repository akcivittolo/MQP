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

# from mode_select_subpanel import ModeSelectSubpanel
# from connection_subpanel import ConnectionSubpanel
# from arming_subpanel import ArmingSubpanel
from control_ui.rc_overide_subpanel import RCOverideSubpanel

from toolbar_statusbar_ui.statuslight import StatusLight

class StatusbarPanel(QStatusBar):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect connection signal to UI updater
        self.the_boat.connection_status_signal.connect(self.update_connection_UI)
        # Connect arming signal to UI updater
        self.the_boat.arm_status_signal.connect(self.update_arming_UI)
        # Connect telem signal to UI updater
        telem_data.telem_data_update.connect(self.update_mode_UI)

        # Create labels for each status
        self.connection_label = QLabel("Disconnected")
        self.arm_label = QLabel("Disarmed")
        self.mode_label = QLabel("Current Mode:")
        self.current_mode_label = QLabel("Unavailable")

        # Add a vertical line separator function
        def make_separator():
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            sep.setFixedHeight(15)
            return sep
        
        self.connection_status_light = StatusLight("red")
        self.arm_status_light = StatusLight("green")

        # Add labels and separators to status bar
        self.addWidget(self.connection_label)
        self.addWidget(self.connection_status_light)
        self.addWidget(make_separator())
        self.addWidget(self.arm_label)
        self.addWidget(self.arm_status_light)
        self.addWidget(make_separator())
        self.addWidget(self.mode_label)
        self.addWidget(self.current_mode_label)
    
    def update_arming_UI(self, arm_status):
        if arm_status == True:
            self.arm_label.setText("Armed")
            self.arm_status_light.setColor("red")
        else:
            self.arm_label.setText("Disarmed")
            self.arm_status_light.setColor("green")
    
    def update_connection_UI(self, connection_status):
        if connection_status == True:
            self.connection_label.setText("Connected")
            self.connection_status_light.setColor("green")
        else:
            self.connection_label.setText("Disconnected")
            self.connection_status_light.setColor("red")

        self.current_mode_label.setText("Unavailable")

    def update_mode_UI(self):
        raw_mode_data = self.telem_data.telemetry_data["HEARTBEAT"]["custom_mode"]
        
        if raw_mode_data != None:
            chosen_mode = self.the_boat.rover_custom_modes[raw_mode_data]
            self.current_mode_label.setText(chosen_mode)

# class StatusLight(QWidget):
#     def __init__(self, color="gray", diameter=16, parent=None):
#         super().__init__(parent)
#         self._color = QColor(color)
#         self._diameter = diameter
#         self.setFixedSize(diameter, diameter)

#     def setColor(self, color):
#         """Update the circle color dynamically."""
#         self._color = QColor(color)
#         self.update()  # triggers a repaint

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.setBrush(self._color)
#         painter.setPen(Qt.PenStyle.NoPen)
#         painter.drawEllipse(0, 0, self._diameter, self._diameter)

