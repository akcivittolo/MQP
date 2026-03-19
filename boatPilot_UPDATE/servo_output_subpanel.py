from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)

from PyQt6.QtCore import Qt

class ServoOutputSubpanel(QWidget):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        layout = QVBoxLayout(self)

        # Servo one title and label
        self.servo_one_output_title = QLabel("Servo 1 Output (PWM)")
        self.servo_one_output_label = QLabel("Placeholder")
        self.servo_one_output_label.setText("No data available")
        self.servo_one_output_label.setStyleSheet("background-color: red;")

        # Servo three title and label
        self.servo_three_output_title = QLabel("Servo 3 Output (PWM)")
        self.servo_three_output_label = QLabel("Placeholder")
        self.servo_three_output_label.setText("No data available")
        self.servo_three_output_label.setStyleSheet("background-color: red;")

        # Add content to layout
        layout.addWidget(self.servo_one_output_title)
        layout.addWidget(self.servo_one_output_label)
        layout.addWidget(self.servo_three_output_title)
        layout.addWidget(self.servo_three_output_label)
            
    def handle_connection(self, connection_status):
        if connection_status == True:
            self.servo_one_output_label.setStyleSheet("background-color: green;")
            self.servo_three_output_label.setStyleSheet("background-color: green;")
        else:
            self.servo_one_output_label.setText("No data available")
            self.servo_one_output_label.setStyleSheet("background-color: red;")
            self.servo_three_output_label.setText("No data available")
            self.servo_three_output_label.setStyleSheet("background-color: red;")
    
    def update_UI(self):
        servo_one_new_value = self.telem_data.telemetry_data["SERVO_OUTPUT_RAW"]["servo1_raw"]
        self.servo_one_output_label.setText(str(servo_one_new_value))

        servo_three_new_value = self.telem_data.telemetry_data["SERVO_OUTPUT_RAW"]["servo3_raw"]
        self.servo_three_output_label.setText(str(servo_three_new_value))


