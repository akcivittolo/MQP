from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame
)

from battery_subpanel import BatterySubpanel
from supervisor_subpanel import SupervisorSubpanel
from servo_output_subpanel import ServoOutputSubpanel

class TelemetryPanel(QWidget):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        self.battery_subpanel = BatterySubpanel(self.the_boat, self.telem_data)
        self.supervisor_subpanel = SupervisorSubpanel(self.the_boat, self.telem_data)
        self.servo_output_subpanel = ServoOutputSubpanel(self.the_boat, self.telem_data)

        # Create main layout
        main_layout = QVBoxLayout(self)

        # Create a title widget
        self.title = QLabel("Telemetry")
        self.title.setObjectName("title")

        # Create a frame widget
        content_frame = QFrame()
        content_frame.setObjectName("panel")

        # Create a layout within the frame
        content_layout = QVBoxLayout(content_frame)

        # Add content to layout
        content_layout.addWidget(self.battery_subpanel)
        content_layout.addWidget(self.servo_output_subpanel)
        content_layout.addWidget(self.supervisor_subpanel)

        # Add the title and frame widgets to main widget
        main_layout.addWidget(self.title)
        main_layout.addWidget(content_frame)
       

        