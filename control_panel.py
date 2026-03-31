from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame
)

from PyQt6.QtCore import Qt

from mode_select_subpanel import ModeSelectSubpanel
from connection_subpanel import ConnectionSubpanel
from arming_subpanel import ArmingSubpanel
from rc_overide_subpanel import RCOverideSubpanel
from mission_planning_subpanel import MissionPlanningSubpanel

class ControlPanel(QFrame):
    def __init__(self, the_boat, telem_data, mission_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data
        self.mission_data = mission_data

        # self.mode_select_subpanel = ModeSelectSubpanel(self.the_boat, self.telem_data)
        # self.arming_subpanel = ArmingSubpanel(self.the_boat)
        # self.connection_subpanel = ConnectionSubpanel(self.the_boat)
        self.mission_planning_subpanel = MissionPlanningSubpanel(self.mission_data, self.the_boat, self.telem_data)
        self.rc_overide_subpanel = RCOverideSubpanel(self.the_boat)



        # Adjust frame borders
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create a title widget
        # self.title = QLabel("Control")
        # self.title.setObjectName("title")

        # Create a frame widget
        # content_frame = QFrame()
        # content_frame.setObjectName("panel")

        # Create a layout within the frame
        # content_layout = QVBoxLayout(content_frame)

        control_content_layout = QVBoxLayout()
        control_content_layout.setContentsMargins(0, 0, 0, 0)

        control_content_widget = QWidget()
        control_content_widget.setLayout(control_content_layout)

        # Add content to layout
        # control_content_layout.addWidget(self.mode_select_subpanel)
        # control_content_layout.addWidget(self.arming_subpanel)
        # control_content_layout.addWidget(self.connection_subpanel)
        control_content_layout.addWidget(self.mission_planning_subpanel)
        control_content_layout.addWidget(self.rc_overide_subpanel)
        control_content_layout.addStretch()
        
        # Add the title and frame widgets to main widget
        # main_layout.addWidget(self.title)
        main_layout.addWidget(control_content_widget)
        
        
