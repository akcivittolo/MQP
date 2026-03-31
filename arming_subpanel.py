from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel
)
from pymavlink import mavutil
from PyQt6.QtCore import Qt

class ArmingSubpanel(QWidget):
    def __init__(self, the_boat):
        super().__init__()

        self.the_boat = the_boat

        # Connect arming signal to UI updater
        self.the_boat.arm_status_signal.connect(self.update_arming_UI)

        # Create a layout
        layout = QVBoxLayout(self)

        # Connection status and connect button
        self.connection_status = QLabel("Disarmed", alignment = Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("background-color: green;")
        self.arm_button = QPushButton("Arm")
        self.arm_button.setCheckable(True)
        self.arm_button.setChecked(False) 

        # Add content to layout
        layout.addWidget(self.connection_status)
        layout.addWidget(self.arm_button)

        # Button connections
        self.arm_button.clicked.connect(self.handle_arm_button)

    def handle_arm_button(self):
        if self.arm_button.isChecked() == True:
            self.the_boat.arm_command()
        else:
            self.the_boat.disarm_command()

    def update_arming_UI(self, arm_status):
        if arm_status == True:
            self.arm_button.setText("Disarm")
            self.connection_status.setText("Armed")
            self.connection_status.setStyleSheet("background-color: red;")
        else:
            self.arm_button.setText("Arm")
            self.connection_status.setText("Disarmed")
            self.connection_status.setStyleSheet("background-color: green;")

    