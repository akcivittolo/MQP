from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QSpinBox,
    QSlider,
    QSizePolicy
)

from PyQt6.QtCore import Qt

class RCOverideSubpanel(QGroupBox):
    def __init__(self, the_boat):
        super().__init__("RC Overide")

        self.the_boat = the_boat

        # Labels for RC options
        self.roll_label = QLabel("Roll")
        self.pitch_label = QLabel("Pitch")
        self.throttle_label = QLabel("Throttle")
        self.yaw_label = QLabel("Yaw")

        # Text inputs for RC options
        self.roll_input = QSpinBox()
        self.roll_input.setRange(1000, 2000)
        self.roll_input.setValue(1500)

        self.pitch_input = QSpinBox()
        self.pitch_input.setRange(1000, 2000)
        self.pitch_input.setValue(1500)

        self.throttle_input = QSpinBox()
        self.throttle_input.setRange(1000, 2000)
        self.throttle_input.setValue(1500)

        self.yaw_input = QSpinBox()
        self.yaw_input.setRange(1000, 2000)
        self.yaw_input.setValue(1500)

        # Set incriments
        self.roll_input.setSingleStep(25)
        self.pitch_input.setSingleStep(25)
        self.throttle_input.setSingleStep(25)
        self.yaw_input.setSingleStep(25)
        
        # Button to set RC options
        self.set_RC_values_button = QPushButton("Start")
        self.set_RC_values_button.setCheckable(True)
        self.set_RC_values_button.setChecked(False) 

        # Button to reset RC values
        self.reset_button = QPushButton("Reset")

        # Connect button to handler function
        self.set_RC_values_button.clicked.connect(self.RC_signaloveride)
        self.reset_button.clicked.connect(self.reset_values)

        # Create layout
        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        grid_layout.addWidget(self.throttle_label, 0, 0)
        grid_layout.addWidget(self.roll_input, 0, 1)

        grid_layout.addWidget(self.pitch_label, 1, 0)
        grid_layout.addWidget(self.pitch_input, 1, 1)

        grid_layout.addWidget(self.roll_label, 2, 0)
        grid_layout.addWidget(self.throttle_input, 2, 1)

        grid_layout.addWidget(self.yaw_label, 3, 0)
        grid_layout.addWidget(self.yaw_input, 3, 1)

        grid_layout.addWidget(self.set_RC_values_button, 4, 0)
        grid_layout.addWidget(self.reset_button, 4, 1)

    def reset_values(self):
        self.roll_input.setValue(1500)
        self.pitch_input.setValue(1500)
        self.throttle_input.setValue(1500)
        self.yaw_input.setValue(1500)

        self.the_boat.roll = int(self.roll_input.value())
        self.the_boat.pitch = int(self.pitch_input.value())
        self.the_boat.throttle = int(self.throttle_input.value())
        self.the_boat.yaw = int(self.yaw_input.value())

        self.the_boat.timer.stop()
        self.set_RC_values_button.setChecked(False)
        self.set_RC_values_button.setText("Start")



    def RC_signaloveride(self):
        self.the_boat.roll = int(self.roll_input.value())
        self.the_boat.pitch = int(self.pitch_input.value())
        self.the_boat.throttle = int(self.throttle_input.value())
        self.the_boat.yaw = int(self.yaw_input.value())

        if self.set_RC_values_button.isChecked() == True:
            self.the_boat.timer.start()
            self.set_RC_values_button.setText("Stop")
        else:
            self.the_boat.timer.stop()
            self.set_RC_values_button.setText("Start")


