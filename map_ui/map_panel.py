from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame
)

from map_ui.map_subpanel import MapSubpanel
# from mission_planning_subpanel import MissionPlanningSubpanel
from map_ui.waypoint_display_subpanel import WaypointDisplaySubpanel
       
class MapPanel(QFrame):
    def __init__(self, telem_data, mission_data):
        super().__init__()

        self.telem_data = telem_data
        self.mission_data = mission_data

        self.map_subpanel = MapSubpanel(self.telem_data, self.mission_data)
        # self.mission_planning_subpanel = MissionPlanningSubpanel(self.mission_data)
        self.waypoint_display_subpanel = WaypointDisplaySubpanel(self.mission_data)

        # Adjust frame borders
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create a title widget
        # self.title = QLabel("Map")
        # self.title.setObjectName("title")

        # Create a frame widget
        # content_frame = QFrame()
        # content_frame.setObjectName("panel")

        map_content_layout = QVBoxLayout()
        map_content_layout.setContentsMargins(0, 0, 0, 0)
        map_content_layout.setSpacing(0)

        map_content_widget = QWidget()
        map_content_widget.setLayout(map_content_layout)

        # Create a layout within the frame
        # content_layout = QVBoxLayout(content_frame)

        # Add content to layout
        map_content_layout.addWidget(self.map_subpanel)
        # map_content_layout.addWidget(self.mission_planning_subpanel)
        map_content_layout.addWidget(self.waypoint_display_subpanel)

        # Add the title and frame widgets to main widget
        # main_layout.addWidget(self.title)
        main_layout.addWidget(map_content_widget)
        