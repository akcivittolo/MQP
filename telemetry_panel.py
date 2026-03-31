from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QGroupBox
)

from gps_data_subpanel import GPSSubpanel
from battery_subpanel import BatterySubpanel
from supervisor_subpanel import SupervisorSubpanel
from servo_output_subpanel import ServoOutputSubpanel


class TelemetryPanel(QFrame):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        self.gps_data_subpanel = GPSSubpanel(self.the_boat, self.telem_data)
        self.battery_subpanel = BatterySubpanel(self.the_boat, self.telem_data)
        self.supervisor_subpanel = SupervisorSubpanel(self.the_boat, self.telem_data)
        self.servo_output_subpanel = ServoOutputSubpanel(self.the_boat, self.telem_data)

        # Adjust frame borders
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # # Create a title widget
        # self.title = QLabel("Telemetry")
        # self.title.setObjectName("title")

        # Create a frame widget
        # content_frame = QFrame()
        # content_frame.setObjectName("panel")

        # Create a layout within the frame
        # content_layout = QVBoxLayout(content_frame)
        telem_content_layout = QVBoxLayout()
        telem_content_layout.setContentsMargins(0, 0, 0, 0)

        telem_content_widget = QWidget()
        telem_content_widget.setLayout(telem_content_layout)

        # Add content to layout
        telem_content_layout.addWidget(self.gps_data_subpanel)
        telem_content_layout.addWidget(self.battery_subpanel)
        telem_content_layout.addWidget(self.servo_output_subpanel)
        telem_content_layout.addWidget(self.supervisor_subpanel)

        # Add the title and frame widgets to main widget
        # main_layout.addWidget(self.title)
        main_layout.addWidget(telem_content_widget)
       

        