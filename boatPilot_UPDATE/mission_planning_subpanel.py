from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton
)

class MissionPlanningSubpanel(QWidget):
    def __init__(self, mission_data):
        super().__init__()

        self.mission_data = mission_data

        # Connect telem data available signal to UI updater
        self.mission_data.mission_data_update.connect(self.update_UI)

        # Create a main layout
        main_layout = QVBoxLayout(self)

        # Create a button layout
        button_layout_widget = QWidget()
        button_layout = QHBoxLayout(button_layout_widget)

        # Title and message 
        self.title = QLabel("Mission Planning")

        # Log View
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)

        # Buttons
        self.select_waypoints_button = QPushButton("Start Selection")
        self.set_waypoints_button = QPushButton("Set")
        self.reset_waypoints_button = QPushButton("Reset")

        # Add buttons to button layout
        button_layout.addWidget(self.select_waypoints_button)
        button_layout.addWidget(self.set_waypoints_button)
        button_layout.addWidget(self.reset_waypoints_button)

        # Add content to layout
        main_layout.addWidget(button_layout_widget)
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.log_view)
    
        # Button connections
        self.select_waypoints_button.clicked.connect(self.select_waypoints_handler)
        self.set_waypoints_button.clicked.connect(self.set_waypoints)
        self.reset_waypoints_button.clicked.connect(self.reset_waypoints)


    def select_waypoints_handler(self):
        if self.mission_data.mission_planning_status == False:
            self.mission_data.mission_planning_status = True
            self.select_waypoints_button.setText("Finish Selection")
        elif self.mission_data.mission_planning_status == True:
            self.mission_data.mission_planning_status = False
            self.select_waypoints_button.setText("Start Selection")


    def reset_waypoints(self):
        self.mission_data.clear_waypoints()

        self.log_view.clear()
    
    def set_waypoints(self):
        self.mission_data.set_waypoints()



    def update_UI(self):
        number_of_waypoints = len(self.mission_data.waypoints_list)
        print(f"The number of waypoints is: {number_of_waypoints}")
        waypoint_to_display = self.mission_data.waypoints_list[number_of_waypoints - 1]

        lat = waypoint_to_display[0]
        lon = waypoint_to_display[1]

        text_to_print = f"Waypoint #{number_of_waypoints}: {lat}, {lon}"
        self.log_view.appendPlainText(text_to_print)

