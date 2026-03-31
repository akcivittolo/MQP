from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton
)

from PyQt6.QtCore import Qt

class ModeSelectSubpanel(QWidget):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        layout = QVBoxLayout(self)

        # Title, Label, Dropdown
        self.title = QLabel("Current Mode")

        self.current_mode_label = QLabel("No data available")
        self.current_mode_label.setStyleSheet("background-color: red;")

        self.dropdown = QComboBox()
        self.dropdown.addItems(self.the_boat.rover_custom_modes)

        # Button
        self.set_mode_button = QPushButton("Set Mode")
        self.set_mode_button.clicked.connect(self.change_mode_handler)

        # Add content to layout
        layout.addWidget(self.title)
        layout.addWidget(self.current_mode_label)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.set_mode_button)

    def change_mode_handler(self):
        mode_chosen = self.dropdown.currentText()
        self.the_boat.change_mode(mode_chosen)

    def handle_connection(self, connection_status):
        if connection_status == True:
            self.current_mode_label.setStyleSheet("background-color: green;")
        else:
            self.current_mode_label.setText("No data available")
            self.current_mode_label.setStyleSheet("background-color: red;")

    def update_UI(self):
        raw_mode_data = self.telem_data.telemetry_data["HEARTBEAT"]["custom_mode"]
        
        if raw_mode_data != None:
            chosen_mode = self.the_boat.rover_custom_modes[raw_mode_data]
            self.current_mode_label.setText(chosen_mode)
        

