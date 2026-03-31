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
    QToolButton,
    QMenu,
    QComboBox
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QAction

from mode_select_subpanel import ModeSelectSubpanel
from connection_subpanel import ConnectionSubpanel
from arming_subpanel import ArmingSubpanel
from rc_overide_subpanel import RCOverideSubpanel

class ToolbarPanel(QToolBar):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect connection signal to UI updater
        self.the_boat.connection_status_signal.connect(self.update_connection_UI)
        # Connect arming signal to UI updater
        self.the_boat.arm_status_signal.connect(self.update_arming_UI)

        # Add a vertical line separator function
        def make_separator():
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            sep.setFixedHeight(15)
            return sep

        self.setMovable(False)

        self.connect_action = QAction(QIcon.fromTheme("network-connect"), "Connect", self)
        self.addAction(self.connect_action)

        self.connection_targets = QComboBox()
        self.connection_targets.addItems(self.the_boat.connection_targets)

        self.addWidget(self.connection_targets)


        self.addWidget(make_separator())

        self.arm_action = QAction(QIcon.fromTheme("network-connect"), "Arm", self)
        self.addAction(self.arm_action)

        self.addWidget(make_separator())

        self.mode_action = QAction(QIcon.fromTheme("network-connect"), "Set Mode", self)
        self.addAction(self.mode_action)

        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(self.the_boat.rover_custom_modes)
        self.mode_dropdown.setEditable(True)

        self.addWidget(self.mode_dropdown)

        # Connect buttons to functions
        self.connect_action.triggered.connect(self.connection_button_handler)
        self.arm_action.triggered.connect(self.arm_button_handler)
        self.mode_action.triggered.connect(self.mode_button_handler)

    def mode_button_handler(self):
        mode_chosen = self.mode_dropdown.currentText()
        self.the_boat.change_mode(mode_chosen)

    def arm_button_handler(self):
        if self.arm_action.text() == "Arm":
            self.the_boat.arm_command()
        elif self.arm_action.text() == "Disarm":
            self.the_boat.disarm_command()
    
    def update_arming_UI(self, arm_status):
        if arm_status == True:
            self.arm_action.setText("Disarm")
        else:
            self.arm_action.setText("Arm")

    def connection_button_handler(self):
        target = self.connection_targets.currentText()
        if self.connect_action.text() == "Connect":
            self.the_boat.start_connection(target)
        elif self.connect_action.text() == "Disconnect":
            self.the_boat.close_connection()

    def update_connection_UI(self, connection_status):
        if connection_status == True:
            self.connect_action.setText("Disconnect")
        else:
            self.connect_action.setText("Connect")

           
