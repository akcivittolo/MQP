import sys
import ctypes
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QHBoxLayout, QVBoxLayout, QGridLayout,
    QScrollArea,
    QSizePolicy,
    QWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QTextEdit
)
from PyQt6.QtGui import QIcon, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSlot, QObject

from PyQt6.QtQuickWidgets import QQuickWidget # For the map

from pathlib import Path

from pymavlink import mavutil

import base64

# Map stuff
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
import folium
from folium import plugins


from mavlink_layer import (start_connection,
                           close_connection,
                           arm_command,
                           disarm_command,
                           get_arm_status,
                           get_current_mode,
                           rover_custom_modes,
                           change_mode,
                           set_mission
                          )

from message_modification_layer import (prepare_message_dictionary, 
                         set_messages,
                         get_desired_messages,
                         get_msg_fields,
                         get_msg_values
) 

# You have to have this for the taskbar icon (Thank you Stack Overflow)
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Enter the following code into WSL to start the simulation:
# sim_vehicle.py -L indianLake -v Rover -f motorboat-skid -A "--serial0=tcp:0.0.0.0:5760" --no-mavproxy

# Defined in locations.txt as indianLake=42.298823,-71.811522,0,0

telemetry_data_row_list = []

class telemetry_data_row():
    def __init__(self, name, value, alert):
        self.name = name
        self.value = value
        self.alert = alert

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Define a variable to store the mavlink connection
        self.the_connection = None
    
        # Set window title, icon, and size
        self.setWindowTitle("WPilot")
        self.setWindowIcon(QIcon('ChatGPTBoat.png'))

        # Set the Windows taskbar icon
        path_to_icon = 'ChatGPTBoatTaskbar.png'
        pixmap = QPixmap()
        pixmap.loadFromData( Path(path_to_icon).read_bytes())
        appIcon = QIcon(pixmap)
        self.setWindowIcon(appIcon)

        # Create overall layout
        overall_layout = QHBoxLayout()
        self.setLayout(overall_layout)

        # Create a central widget to apply layout
        widget = QWidget()
        widget.setLayout(overall_layout)
        self.setCentralWidget(widget)

        # Create layouts for each panel
        self.telemetryPanel = QVBoxLayout()
        mapPanel = QVBoxLayout()
        missionPanel = QVBoxLayout()

        # Add the panel layouts to overall layout
        overall_layout.addLayout(self.telemetryPanel)
        overall_layout.addLayout(mapPanel)
        overall_layout.addLayout(missionPanel)

        # Customize telemetryPanel
        telemetryPanelTitle = QLabel("Telemetry", alignment = Qt.AlignmentFlag.AlignCenter)
        telemetryPanelTitle.setMinimumHeight(20)
        telemetryPanelTitle.setMaximumHeight(20)
        telemetryPanelTitle.setMaximumWidth(500)
        telemetryPanelTitle.setStyleSheet("background-color: grey;")
        self.telemetryPanel.addWidget(telemetryPanelTitle)
        
        telemetry_data_content = QWidget()
        telemetry_data_content.setMaximumWidth(500)
        telemetry_data_content.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.telemetryPanel_data = QVBoxLayout(telemetry_data_content)

        scroll = QScrollArea()
        scroll.setWidget(telemetry_data_content)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(500)

        self.telemetryPanel.addWidget(scroll)

        self.initialize_telemetry_data()

        # Customize mapPanel
        mapPanelTitle = QLabel("Map", alignment = Qt.AlignmentFlag.AlignCenter)
        mapPanelTitle.setMinimumHeight(20)
        mapPanelTitle.setMaximumHeight(20)
        mapPanel.addWidget(mapPanelTitle)
        mapPanelTitle.setStyleSheet("background-color: grey;")

        indianLakeCords = [42.293377, -71.816133]
        self.location_history = []
        self.map = folium.Map(location = indianLakeCords, tiles="Esri.WorldImagery", zoom_start = 17)

        # Show a popup with coordinates when clicked
        self.map.add_child(folium.LatLngPopup())

        map_id = self.map.get_name()

        self.map.get_root().html.add_child(folium.Element(f"""
            <script>
                setTimeout(function() {{
                    window.map = {map_id};
                }}, 0);
            </script>
            """))
        
        # Because folium runs as an html thing we have to pass the image in a weird way
        arrow_path = Path("arrowicon.png")
        arrow_data = base64.b64encode(arrow_path.read_bytes()).decode()
        
        self.map.get_root().html.add_child(folium.Element(f"""
            <script>
                window.arrowIcon = L.icon({{
                    iconUrl: "data:image/png;base64,{arrow_data}",
                    iconSize: [40, 40],
                    iconAnchor: [20, 20]  // center the rotation point
                }});
            </script>
            """))
        
        self.map.save('map.html')
        self.map_view = QWebEngineView()

        self.map_view.setHtml(self.map.get_root().render())


        mapPanel.addWidget(self.map_view)



        # Add a waypoints section
        missionPlanningTitle = QLabel("Waypoints", alignment = Qt.AlignmentFlag.AlignCenter)
        missionPlanningTitle.setMinimumHeight(20)
        missionPlanningTitle.setMaximumHeight(20)
        mapPanel.addWidget(missionPlanningTitle)
        missionPlanningTitle.setStyleSheet("background-color: grey;")

        add_waypoint_layout = QHBoxLayout()
        waypoint_control_buttons = QHBoxLayout()
        waypoint_info_layout = QHBoxLayout()

        waypoints_selected_layout = QVBoxLayout()
        waypoints_selected_label = QLabel("Current waypoints:", alignment = Qt.AlignmentFlag.AlignCenter)

        boat_is_heading_towards_layout = QVBoxLayout()
        boat_is_heading_towards_label = QLabel("Boat is heading towards:", alignment = Qt.AlignmentFlag.AlignCenter)
        self.boat_destination_label = QLabel("None", alignment = Qt.AlignmentFlag.AlignCenter)

        boat_is_heading_towards_layout.addWidget(boat_is_heading_towards_label)
        boat_is_heading_towards_layout.addWidget(self.boat_destination_label)

        new_waypoint_label = QLabel("New Waypoint:", alignment = Qt.AlignmentFlag.AlignLeft)
        self.latitude_box = QLineEdit()
        self.latitude_box.setPlaceholderText("Latitude")
        self.longitude_box = QLineEdit()
        self.longitude_box.setPlaceholderText("Longitude")

        self.waypoints_list = []
        self.add_waypoint_button = QPushButton("Add Waypoint")
        self.reset_waypoints_button = QPushButton("Reset Waypoints")
        self.set_mission_button = QPushButton("Set Mission")
        
        waypoint_control_buttons.addWidget(self.add_waypoint_button)
        waypoint_control_buttons.addWidget(self.reset_waypoints_button)

        # Create a read-only text box
        self.waypoints_text = QTextEdit()
        self.waypoints_text.setReadOnly(True)
        
        add_waypoint_layout.addWidget(new_waypoint_label)
        add_waypoint_layout.addWidget(self.latitude_box)
        add_waypoint_layout.addWidget(self.longitude_box)
        
        mapPanel.addLayout(add_waypoint_layout)
        mapPanel.addLayout(waypoint_control_buttons)

        mapPanel.addLayout(waypoint_info_layout)
        waypoint_info_layout.addLayout(waypoints_selected_layout)
        waypoint_info_layout.addLayout(boat_is_heading_towards_layout)
        waypoints_selected_layout.addWidget(waypoints_selected_label)
        waypoints_selected_layout.addWidget(self.waypoints_text)
        mapPanel.addWidget(self.set_mission_button)

        self.waypoints_text.setText("\n".join([f"{lat}, {lon}" for lat, lon in self.waypoints_list]))

        self.add_waypoint_button.clicked.connect(self.add_waypoint)
        self.set_mission_button.clicked.connect(self.set_mission_handler)


        # Customize missionPanel
        missionPanelTitle = QLabel("Mission Info", alignment = Qt.AlignmentFlag.AlignCenter)
        missionPanelTitle.setStyleSheet("background-color: grey;")
        missionPanelTitle.setMinimumHeight(20)
        missionPanelTitle.setMaximumHeight(20)

        self.arm_status_label = QLabel("DISARMED", alignment = Qt.AlignmentFlag.AlignCenter)
        self.arm_status_label.setStyleSheet("background-color: green;")

        arm_button = QPushButton("ARM")
        disarm_button = QPushButton("DISARM")

        choose_mode_label = QLabel("Select Mode:", alignment = Qt.AlignmentFlag.AlignLeft)
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(rover_custom_modes)

        mode_choice_layout = QHBoxLayout()
        mode_choice_layout.addWidget(choose_mode_label)
        mode_choice_layout.addWidget(self.mode_dropdown)

        set_mode_button = QPushButton("Set Selected Mode")

        this_is_the_current_mode_label = QLabel("Current Mode:", alignment = Qt.AlignmentFlag.AlignLeft)
        self.current_mode_label = QLabel("None", alignment = Qt.AlignmentFlag.AlignCenter)
        
        current_mode_layout = QHBoxLayout()
        current_mode_layout.addWidget(this_is_the_current_mode_label)
        current_mode_layout.addWidget(self.current_mode_label)

        self.connection_status = QLabel("No Connection", alignment = Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("background-color: red;")

        connect_button = QPushButton("Connect")
        disconnect_button = QPushButton("Disconnect")

        missionPanel.addWidget(missionPanelTitle)
        missionPanel.addLayout(current_mode_layout)
        missionPanel.addLayout(mode_choice_layout)
        missionPanel.addWidget(set_mode_button)
        missionPanel.addWidget(self.arm_status_label)
        missionPanel.addWidget(arm_button)
        missionPanel.addWidget(disarm_button)
        missionPanel.addWidget(self.connection_status)
        missionPanel.addWidget(connect_button)
        missionPanel.addWidget(disconnect_button)

        set_mode_button.clicked.connect(self.change_mode_handler)

        arm_button.clicked.connect(self.arm_boat_handler)
        disarm_button.clicked.connect(self.disarm_boat_handler)

        connect_button.clicked.connect(self.start_connection_handler)
        disconnect_button.clicked.connect(self.close_connection_handler)


        # Create a timer for updating telemetry
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry_data)
        self.timer.start(20)

    def set_mission_handler(self):
        if self.the_connection == None:
            return None
        
        set_mission(self.the_connection, self.waypoints_list)

    def add_waypoint(self):
        waypoint_lat = float(self.latitude_box.text())
        waypoint_lon = float(self.longitude_box.text())

        self.waypoints_list.append((waypoint_lat, waypoint_lon))

        self.waypoints_text.setText("\n".join([f"Waypoint {i}: {lat}, {lon}" 
                                       for i, (lat, lon) in enumerate(self.waypoints_list)]))


        print("we're adding a waypoint")
        js = f"""
            L.marker([{waypoint_lat}, {waypoint_lon}], {{
            }}).addTo(window.map);

        """

        self.map_view.page().runJavaScript(js)


    def start_connection_handler(self):
        self.the_connection = start_connection(self.the_connection)
        self.connection_status_label_handler()
        set_messages(self.the_connection)
    
    def close_connection_handler(self):
        self.disarm_boat_handler()

        close_connection(self.the_connection)
        self.the_connection = None
        self.connection_status_label_handler()
        self.reset_telemetry_data()
        
    def connection_status_label_handler(self):
        if self.the_connection != None:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("background-color: green;")
        else:
            self.connection_status.setText("No Connection")
            self.connection_status.setStyleSheet("background-color: red;")

    def updateMapMarker(self, msg):

        latitude = (msg.lat) / (1e7) # Degrees
        longitude = (msg.lon) / (1e7) # Degrees
        heading = (msg.hdg) / 100.0 # Degrees

        self.location_history.append([latitude,longitude])

        # Javascript version

        js = f"""

        if (!window.marker) {{
            // Create the marker and store it in a variable
            window.marker = L.marker([{latitude}, {longitude}], {{
                icon: window.arrowIcon
            }}).addTo(window.map);

            window.map.setView([{latitude}, {longitude}], 17); 
        }}
        else {{
            window.map.removeLayer(window.marker)
            // Create the marker and store it in a variable
            window.marker = L.marker([{latitude}, {longitude}], {{
                icon: window.arrowIcon
            }}).addTo(window.map);
        }}

        // Rotate the marker by the desired heading
        var el = marker.getElement();  // Get the DOM element of the marker
        if (el) {{
            el.style.transform += ' rotate({heading}deg)';
            el.style.transformOrigin = 'center center';
        }}

        // Draw/update polyline for path
        if (!window.pathLine) {{
            window.pathLine = L.polyline({self.location_history}, {{color: 'blue', weight: 3}}).addTo(window.map);
        }} 
        else {{
            window.pathLine.setLatLngs({self.location_history});
        }}
        """

        self.map_view.page().runJavaScript(js)



        
    def initialize_telemetry_data(self):
        ordered_messages = prepare_message_dictionary()

        targeted_fields = []
        
        for messages in ordered_messages:
            for key, value in messages.items():
                if key == 'fields':
                    targeted_fields.extend(value) # Use extend to not have lists within lists. It's just one big list with .extend

        for field in targeted_fields:
            telem_row_layout = QHBoxLayout()
            self.telemetryPanel_data.addLayout(telem_row_layout)

            telemetry_data_row_temp = telemetry_data_row(field, str(0), "Empty")
            telemetry_data_row_list.append(telemetry_data_row_temp)
            
            field_name = QLabel(telemetry_data_row_temp.name, alignment = Qt.AlignmentFlag.AlignLeft)
            field_value = QLabel(telemetry_data_row_temp.value, alignment = Qt.AlignmentFlag.AlignLeft)
            field_alert = QLabel(telemetry_data_row_temp.alert, alignment = Qt.AlignmentFlag.AlignCenter)

            field_alert.setStyleSheet("background-color: red;")

            telem_row_layout.addWidget(field_name)
            telem_row_layout.addWidget(field_value)
            telem_row_layout.addWidget(field_alert)
    
    def update_telemetry_data(self):

        current_msg = get_desired_messages(self.the_connection)
        
        # Create lists for the current message's fields and values
        if current_msg == None:
            return None

        # Update our current mode label
        if current_msg.get_type() == 'HEARTBEAT':
            self.current_mode_label.setText(rover_custom_modes[current_msg.custom_mode])

        # Update our map data
        if current_msg.get_type() == 'GLOBAL_POSITION_INT':
            self.updateMapMarker(current_msg)

        # Update destination label
        if current_msg.get_type() == 'MISSION_CURRENT':
            self.update_destination_label(current_msg)


        current_fields = get_msg_fields(current_msg)
        current_values = get_msg_values(current_msg)

        # Iterate through all the widgets in our telemetry panel
        for panel_index in range(self.telemetryPanel_data.count()):
            data_row = self.telemetryPanel_data.itemAt(panel_index)
            
            # Check to see if the widget is a data row
            if isinstance(data_row, QHBoxLayout):

                # If the field name in the data row has a match in our list of fields, update the respective value
                for field, value in zip(current_fields, current_values):
                    data_row_field = data_row.itemAt(0).widget().text()

                    if data_row_field == field:
                        data_row.itemAt(1).widget().setText(str(value))
                        data_row.itemAt(2).widget().setText("Updated")
                        data_row.itemAt(2).widget().setStyleSheet("background-color: green;")

    def update_destination_label(self, msg):
        current_waypoint_index = msg.seq

        if (msg.mission_mode == 0):
            return

        if current_waypoint_index < len(self.waypoints_list):
            current_waypoint = self.waypoints_list[current_waypoint_index]
            label_text = f"Waypoint {current_waypoint_index + 1}: {current_waypoint}"
        else:
            label_text = "Mission Complete"

        self.boat_destination_label.setText(label_text)

    
    def reset_telemetry_data(self):

        # Iterate through all the widgets in our telemetry panel
        for panel_index in range(self.telemetryPanel_data.count()):
            data_row = self.telemetryPanel_data.itemAt(panel_index)
            
            # Check to see if the widget is a data row
            if isinstance(data_row, QHBoxLayout):
                data_row.itemAt(1).widget().setText(str(0))
                data_row.itemAt(2).widget().setText("Empty")
                data_row.itemAt(2).widget().setStyleSheet("background-color: red;")

    def arm_boat_handler(self):
        if self.the_connection == None:
            print("No connection. Unable to arm")
            return None

        arm_command(self.the_connection)

        arm_flag = 0

        while arm_flag != 1:
            arm_flag = get_arm_status(self.the_connection)
            print(arm_flag)
            self.arm_status_label_handler(arm_flag)
        
    def disarm_boat_handler(self):
        if self.the_connection == None:
            print("No connection. Unable to disarm")
            return None
        
        disarm_command(self.the_connection)

        arm_flag = 1

        while arm_flag != 0:
            arm_flag = get_arm_status(self.the_connection)
            print(arm_flag)
            self.arm_status_label_handler(arm_flag)

    def arm_status_label_handler(self, arm_status_flag):

        if arm_status_flag == 1:
            self.arm_status_label.setText("ARMED")
            self.arm_status_label.setStyleSheet("background-color: red;")
            return 1
        
        if arm_status_flag == 0:
            self.arm_status_label.setText("DISARMED")
            self.arm_status_label.setStyleSheet("background-color: green;")
            return 0   

    def change_mode_handler(self):
        if self.the_connection == None:
            return None
        
        dropdown_chosen_mode = self.mode_dropdown.currentText()
        if change_mode(self.the_connection, dropdown_chosen_mode) == 1:
            print("Mode change failed")
            return None

        # Update our current mode label
        while dropdown_chosen_mode != self.current_mode_label.text():
            current_mode = get_current_mode(self.the_connection)
            self.current_mode_label.setText(current_mode)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())