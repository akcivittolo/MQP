import sys
import io
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
    QFrame,
    QListWidget,
    QComboBox
)
from PyQt6.QtGui import QIcon, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, QTimer

from pathlib import Path

from pymavlink import mavutil

# Map stuff
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium
from folium import plugins

from dataDesired import (prepare_message_dictionary, 
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

master_connection = None
telemetry_data_row_list = []

priorLat = 42.293377
priorLon = -71.816133

arm_status = False

def startConnection():
    global master_connection

    if master_connection != None:
        print("Connection already exists")
        return master_connection
    else:  
        mav_connection = mavutil.mavlink_connection("tcp:172.21.103.161:5760")
        mav_connection.wait_heartbeat()

    if mav_connection is None:
        print("Connection failed")
        return None
    else:
        print("Connection successful")
        return mav_connection

def start_connection_handler():
    global master_connection
    master_connection = startConnection()
    set_messages(master_connection)
    return master_connection

def closeConnection(mav_connection):
    if mav_connection is None:
        print("No Connection")
    else:
        mav_connection.close()
        print("Connection closed")

def close_connection_handler():
    global master_connection
    closeConnection(master_connection)
    master_connection = None

class telemetry_data_row():
    def __init__(self, name, value, alert):
        self.name = name
        self.value = value
        self.alert = alert

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
    
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

        self.initializeTelemetryData()

        # Customize mapPanel
        mapPanelTitle = QLabel("Map", alignment = Qt.AlignmentFlag.AlignCenter)
        mapPanelTitle.setMinimumHeight(20)
        mapPanelTitle.setMaximumHeight(20)
        mapPanel.addWidget(mapPanelTitle)
        mapPanelTitle.setStyleSheet("background-color: grey;")

        indianLakeCords = [42.293377, -71.816133]
        self.map = folium.Map(location = indianLakeCords, tiles="Esri.WorldImagery", zoom_start = 17)
        self.map.save('map.html')
        self.map_view = QWebEngineView()
        self.map_view.setHtml(self.map.get_root().render())

        mapPanel.addWidget(self.map_view)
        

        # Customize missionPanel
        missionPanelTitle = QLabel("Mission Info", alignment = Qt.AlignmentFlag.AlignCenter)
        missionPanelTitle.setStyleSheet("background-color: grey;")
        missionPanelTitle.setMinimumHeight(20)
        missionPanelTitle.setMaximumHeight(20)

        self.arm_status = QLabel("DISARMED", alignment = Qt.AlignmentFlag.AlignCenter)
        self.arm_status.setStyleSheet("background-color: green;")

        arm_button = QPushButton("ARM")
        disarm_button = QPushButton("DISARM")

        choose_mode_label = QLabel("Select Mode:", alignment = Qt.AlignmentFlag.AlignLeft)
        circle_mode_button = QPushButton("Circle")

        mode_choice_layout = QHBoxLayout()
        mode_choice_layout.addWidget(choose_mode_label)
        mode_choice_layout.addWidget(circle_mode_button)


        self.connection_status = QLabel("No Connection", alignment = Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("background-color: red;")

        connect_button = QPushButton("Connect")
        disconnect_button = QPushButton("Disconnect")

        missionPanel.addWidget(missionPanelTitle)
        missionPanel.addLayout(mode_choice_layout)
        missionPanel.addWidget(self.arm_status)
        missionPanel.addWidget(arm_button)
        missionPanel.addWidget(disarm_button)
        missionPanel.addWidget(self.connection_status)
        missionPanel.addWidget(connect_button)
        missionPanel.addWidget(disconnect_button)

        circle_mode_button.clicked.connect(self.setCircleMode)

        arm_button.clicked.connect(self.arm_command)
        arm_button.clicked.connect(self.arm_status_label_handler)
        disarm_button.clicked.connect(self.disarm_command)
        disarm_button.clicked.connect(self.arm_status_label_handler)

        connect_button.clicked.connect(start_connection_handler)
        connect_button.clicked.connect(self.connection_status_label_handler)
        disconnect_button.clicked.connect(close_connection_handler)
        disconnect_button.clicked.connect(self.connection_status_label_handler)
        disconnect_button.clicked.connect(self.resetTelemetryData)

        # Create a timer for updating telemetry
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTelemetryData)
        self.timer.start(200)

        # Create a slower timer for updating map
        self.slowTimer = QTimer()
        self.slowTimer.timeout.connect(self.updateMapMarker)
        self.slowTimer.start(1000)

    def setCircleMode(self):
        global master_connection

        if master_connection is None:
            print("No connection available")
            return

        # Make sure the boat is armed
        if not arm_status:
            print("Boat must be armed first!")
            return

         # Ensure GUIDED mode
        guided_mode = master_connection.mode_mapping()['GUIDED']
        master_connection.set_mode(guided_mode)

        lat = 100
        lon = 100
        alt = 0

        # Send the command
        master_connection.mav.set_position_target_global_int_send(
            10,  # time_boot_ms (ignored)
            master_connection.target_system,
            master_connection.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            int(0b110111111000),  # type_mask: only position
            int(lat * 1e7),       # latitude in degE7
            int(lon * 1e7),       # longitude in degE7
            alt,                  # altitude
            0, 0, 0,              # velocity (ignored)
            0, 0, 0,              # acceleration (ignored)
            0, 0                  # yaw, yaw_rate
        )

        print(f"Heading to point ({lat},{lon},{alt})")

    def updateMapMarker(self):
        global priorLat
        global priorLon
        global arm_status

        if master_connection != None and arm_status == True:
            try:
                msg = master_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
                latitude = (msg.lat) / (1e7) # Degrees
                longitude = (msg.lon) / (1e7) # Degrees
                heading = (msg.hdg) * 100 # Degrees

                if latitude != priorLat or longitude != priorLon:
                
                    self.map = folium.Map(location = [latitude, longitude], tiles="Esri.WorldImagery", zoom_start = 16) 

                    folium.Marker(
                        [latitude, longitude],
                        popup = 'Present Location',
                        icon = folium.Icon(color='red', icon='info-sign')
                    ).add_to(self.map)

                                   
                    self.map_view.setHtml(self.map.get_root().render())

                    priorLat = latitude
                    priorLon = longitude
            except:
                pass

    def initializeTelemetryData(self):
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

        print (telemetry_data_row_list)
    
    def updateTelemetryData(self):

        current_msg = get_desired_messages(master_connection)
        
        # Create lists for the current message's fields and values
        if current_msg != None:
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

        else:
            pass
    
    def resetTelemetryData(self):
        global arm_status

        # Iterate through all the widgets in our telemetry panel
        for panel_index in range(self.telemetryPanel_data.count()):
            data_row = self.telemetryPanel_data.itemAt(panel_index)
            
            # Check to see if the widget is a data row
            if isinstance(data_row, QHBoxLayout):
                data_row.itemAt(1).widget().setText(str(0))
                data_row.itemAt(2).widget().setText("Empty")
                data_row.itemAt(2).widget().setStyleSheet("background-color: red;")

        arm_status = False
        self.arm_status_label_handler()



    def connection_status_label_handler(self):
        global master_connection
        if master_connection != None:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("background-color: green;")
        else:
            self.connection_status.setText("No Connection")
            self.connection_status.setStyleSheet("background-color: red;")

    def arm_status_label_handler(self):
        global arm_status

        print("We are in the label handler")
        print(arm_status)

        if arm_status == True:
            self.arm_status.setText("ARMED")
            self.arm_status.setStyleSheet("background-color: red;")
        
        if arm_status == False:
            self.arm_status.setText("DISARMED")
            self.arm_status.setStyleSheet("background-color: green;")

    def arm_command(self):
        global master_connection
        global arm_status

        if master_connection!=None:
            master_connection.mav.command_long_send(
                master_connection.target_system,
                master_connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, # Message confirmation
                1, # 0 disarm, 1 arm
                0, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
                0,0,0,0,0
            )

            msg = master_connection.recv_match(type='COMMAND_ACK', blocking=True)
            if msg.result == 0:
                print("Boat armed")
                arm_status = True
            else:
                print("Arm failed")
                arm_status = False
        else:
            print("No connection available")
            return None
    
    def disarm_command(self):
        global master_connection
        global arm_status

        if master_connection!=None:
            master_connection.mav.command_long_send(
                master_connection.target_system,
                master_connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, # Message confirmation
                0, # 0 disarm, 1 arm
                0, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
                0,0,0,0,0
            )

            msg = master_connection.recv_match(type='COMMAND_ACK', blocking=True)
            if msg.result == 0:
                print("Boat disarmed")
                arm_status = False
            else:
                print("Disarm failed")
                arm_status = False
        else:
            print("No connection available")
            return None


        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())