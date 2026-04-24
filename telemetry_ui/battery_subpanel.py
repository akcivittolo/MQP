from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout
)

from PyQt6.QtCore import Qt

from toolbar_statusbar_ui.statuslight import StatusLight

class BatterySubpanel(QGroupBox):
    def __init__(self, the_boat, telem_data):
        super().__init__("Battery Data")

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        main_layout = QVBoxLayout(self)

        # Grid layout for all the rows
        grid_layout = QGridLayout()

        # Title and battery remaining
        self.title = QLabel("Battery Remaining: ")
        self.battery_remaining = QLabel("Unavailable")
        self.battery_status_light = StatusLight("yellow")

        # Add content to layout
        grid_layout.addWidget(self.title, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.battery_remaining, 0, 1)
        grid_layout.addWidget(self.battery_status_light, 0, 2)

        # Add the grid layout to the main vertical layout
        main_layout.addLayout(grid_layout)
            
    def handle_connection(self, connection_status):
        if connection_status == True:
            self.battery_status_light.setColor("green")
        else:
            self.battery_status_light.setColor("yellow")
            self.battery_remaining.setText("Unavailable")
    
    def update_UI(self):
        battery_data = self.telem_data.telemetry_data["BATTERY_STATUS"]["battery_remaining"]
        battery_voltages = self.telem_data.telemetry_data["BATTERY_STATUS"]["voltages"]
        self.battery_remaining.setText(str(battery_data) + "%")


