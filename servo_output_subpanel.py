from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout
)

from PyQt6.QtCore import Qt

from statuslight import StatusLight

class ServoOutputSubpanel(QGroupBox):
    def __init__(self, the_boat, telem_data):
        super().__init__("Servo Data")

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        main_layout = QVBoxLayout(self)

        # Grid layout for all the rows
        grid_layout = QGridLayout()

        # Servo one title and label
        self.servo_one_output_title = QLabel("Servo 1 Output (PWM)")
        self.servo_one_output_label = QLabel("Unavailable")
        self.servo_one_status_light = StatusLight("yellow")
        grid_layout.addWidget(self.servo_one_output_title, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.servo_one_output_label, 0, 1)
        grid_layout.addWidget(self.servo_one_status_light, 0, 2)

        # Servo three title and label
        self.servo_three_output_title = QLabel("Servo 3 Output (PWM)")
        self.servo_three_output_label = QLabel("Unavailable")
        self.servo_three_status_light = StatusLight("yellow")
        grid_layout.addWidget(self.servo_three_output_title, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.servo_three_output_label, 1, 1)
        grid_layout.addWidget(self.servo_three_status_light, 1, 2)

        # Add the grid layout to the main vertical layout
        main_layout.addLayout(grid_layout)
            
    def handle_connection(self, connection_status):
        if connection_status == True:
            self.servo_one_status_light.setColor("green")
            self.servo_three_status_light.setColor("green")
        else:
            self.servo_one_output_label.setText("Unavailable")
            self.servo_three_output_label.setText("Unavailable")
            self.servo_one_status_light.setColor("yellow")
            self.servo_three_status_light.setColor("yellow")
    
    def update_UI(self):
        servo_one_new_value = self.telem_data.telemetry_data["SERVO_OUTPUT_RAW"]["servo1_raw"]
        self.servo_one_output_label.setText(str(servo_one_new_value))

        servo_three_new_value = self.telem_data.telemetry_data["SERVO_OUTPUT_RAW"]["servo3_raw"]
        self.servo_three_output_label.setText(str(servo_three_new_value))


