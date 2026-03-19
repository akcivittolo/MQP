from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit 
)

from PyQt6.QtCore import Qt

class RCOverideSubpanel(QWidget):
    def __init__(self, the_boat):
        super().__init__()

        self.the_boat = the_boat

        # Create a layout
        layout = QVBoxLayout(self)

        # Title
        self.title = QLabel("RC Overide", alignment = Qt.AlignmentFlag.AlignCenter)

        # Labels for RC options
        self.roll_label = QLabel("Roll")
        self.pitch_label = QLabel("Pitch")
        self.throttle_label = QLabel("Throttle")
        self.yaw_label = QLabel("Yaw")

        # Text inputs for RC options
        self.roll_input = QLineEdit()
        self.roll_input.setText("1500")
        self.pitch_input = QLineEdit()
        self.pitch_input.setText("1500")
        self.throttle_input = QLineEdit()
        self.throttle_input.setText("1500")
        self.yaw_input = QLineEdit()
        self.yaw_input.setText("1500")
        
        # Button to set RC options
        self.set_RC_values_button = QPushButton("Start")
        self.set_RC_values_button.setCheckable(True)
        self.set_RC_values_button.setChecked(False) 

        # Connect button to handler function
        self.set_RC_values_button.clicked.connect(self.RC_signaloveride)

        # Add widgets to layout
        layout.addWidget(self.title)

        layout.addWidget(self.throttle_label)
        layout.addWidget(self.roll_input)

        layout.addWidget(self.pitch_label)
        layout.addWidget(self.pitch_input)

        layout.addWidget(self.roll_label)
        layout.addWidget(self.throttle_input)

        layout.addWidget(self.yaw_label)
        layout.addWidget(self.yaw_input)

        layout.addWidget(self.set_RC_values_button)

    def RC_signaloveride(self):
        self.the_boat.roll = int(self.roll_input.text())
        self.the_boat.pitch = int(self.pitch_input.text())
        self.the_boat.throttle = int(self.throttle_input.text())
        self.the_boat.yaw = int(self.yaw_input.text())

        if self.set_RC_values_button.isChecked() == True:
            self.the_boat.timer.start()
            self.set_RC_values_button.setText("Stop")
        else:
            self.the_boat.timer.stop()
            self.set_RC_values_button.setText("Start")


