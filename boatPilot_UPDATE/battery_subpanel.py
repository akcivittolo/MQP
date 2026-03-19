from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel
)

from PyQt6.QtCore import Qt

class BatterySubpanel(QWidget):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        layout = QVBoxLayout(self)

        # Title and battery remaining
        self.title = QLabel("Battery Remaining")
        self.battery_remaining = QLabel("Placeholder")
        self.battery_remaining.setText("No data available")
        self.battery_remaining.setStyleSheet("background-color: red;")

        # Add content to layout
        layout.addWidget(self.title)
        layout.addWidget(self.battery_remaining)
            
    def handle_connection(self, connection_status):
        if connection_status == True:
            self.battery_remaining.setStyleSheet("background-color: green;")
        else:
            self.battery_remaining.setText("Disconnected")
            self.battery_remaining.setText("No data available")
            self.battery_remaining.setStyleSheet("background-color: red;")
    
    def update_UI(self):
        battery_data = self.telem_data.telemetry_data["BATTERY_STATUS"]["battery_remaining"]
        self.battery_remaining.setText(str(battery_data) + "%")


