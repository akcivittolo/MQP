from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QComboBox,
    QTableWidget, 
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QGridLayout,
    QSizePolicy
)

from statuslight import StatusLight

from PyQt6.QtCore import Qt

class MissionPlanningSubpanel(QGroupBox):
    def __init__(self, mission_data, the_boat, telem_data):
        super().__init__("Mission Planning")

        self.mission_data = mission_data
        self.the_boat = the_boat

        # Connect signal to connection status
        the_boat.connection_status_signal.connect(self.update_connection_status)
        self.connection_status_flag = False

        # Create a main layout
        main_layout = QGridLayout(self)
      
        # Buttons
        self.select_waypoints_button = QPushButton("Start Selection")
        self.set_waypoints_button = QPushButton("Send Mission Data")
        self.reset_waypoints_button = QPushButton("Reset")
        self.set_mission_type_button = QPushButton("Set Mission Type")

        self.set_waypoints_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # Mission type label dropdown
        self.mission_type_label = QLabel("Mission Type")
        self.mission_type_dropdown = QComboBox()
        self.mission_type_dropdown.addItems(self.mission_data.mission_types)

        # Set mission checks
        self.connection_status_label = QLabel("Connection Status: ")
        self.connection_status_light = StatusLight("red")
        self.selection_status_label = QLabel("Selection Status: ")
        self.selection_status_light = StatusLight("red")

        # Add buttons and combobox to button layout
        main_layout.addWidget(self.mission_type_label, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(self.mission_type_dropdown, 0, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)  # spans 2 columns

        # Select waypoints button (spans all 3 columns)
        main_layout.addWidget(self.select_waypoints_button, 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignTop)

        # Create a container for the labels + lights
        status_container = QWidget()
        status_layout = QGridLayout(status_container)

        status_container.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        status_layout.setContentsMargins(0, 0, 0, 0)  # remove extra spacing
        status_layout.addWidget(self.connection_status_label, 0, 0)
        status_layout.addWidget(self.connection_status_light, 0, 1)
        status_layout.addWidget(self.selection_status_label, 1, 0)
        status_layout.addWidget(self.selection_status_light, 1, 1)

        # Add the container to the grid
        main_layout.addWidget(status_container, 2, 0, 2, 2, alignment=Qt.AlignmentFlag.AlignTop)  # row=2, col=0, rowspan=2, colspan=2

        # Add the Set button next to the container
        main_layout.addWidget(self.set_waypoints_button, 2, 2, 2, 1)  # spans the same 2 rows vertically

        # Reset button spans all columns
        main_layout.addWidget(self.reset_waypoints_button, 4, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignTop)
    
        # Button connections
        self.select_waypoints_button.clicked.connect(self.select_waypoints_handler)
        self.set_waypoints_button.clicked.connect(self.set_waypoints)
        self.reset_waypoints_button.clicked.connect(self.reset_waypoints)

        # Combobox connections
        self.mission_type_dropdown.currentTextChanged.connect(self.set_mission_type_handler)

    def update_connection_status(self, connection_status):
        if connection_status == True:
           self.connection_status_light.setColor("green")
           self.connection_status_flag = True
        else:
            self.connection_status_light.setColor("red")
            self.connection_status_flag = False

    def set_mission_type_handler(self, text):
        self.mission_data.change_mission_type(text)

        self.reset_waypoints()

    def select_waypoints_handler(self):
        self.mission_data.current_mission_type = self.mission_type_dropdown.currentText()

        print(len(self.mission_data.waypoints_list))
        if self.mission_data.mission_planning_status == False:
            self.mission_data.mission_planning_status = True
            self.selection_status_light.setColor("red")
            self.reset_waypoints()
            self.select_waypoints_button.setText("Finish Selection")
        elif self.mission_data.mission_planning_status == True and self.mission_data.enough_waypoints_flag == True:
            if self.mission_data.current_mission_type == self.mission_data.mission_types[1]:
                print("Calculating lawnmower cords")
                self.mission_data.get_lawnmower_waypoints()
            self.mission_data.mission_planning_status = False
            self.selection_status_light.setColor("green")
            self.select_waypoints_button.setText("Start Selection")


    def reset_waypoints(self):
        self.mission_data.clear_waypoints()
        self.selection_status_light.setColor("red")
    
    def set_waypoints(self):
        print(self.mission_data.enough_waypoints_flag)
        print(self.connection_status_flag)
        print(self.mission_data.mission_planning_status)
        if self.mission_data.enough_waypoints_flag == True and self.connection_status_flag == True and self.mission_data.mission_planning_status == False:
            self.mission_data.set_waypoints()
            print("Transmitting the data to the Pixhawk")
            pass
        else:
            print("Not enough waypoints to send missioREEEEEEEEEEn")

   

