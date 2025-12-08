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

from mavlink_layer import (start_connection,
                           close_connection,
                           arm_command,
                           disarm_command,
                           get_arm_status
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

master_connection = None
telemetry_data_row_list = []

priorLat = 42.293377
priorLon = -71.816133

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

        self.arm_status_label = QLabel("DISARMED", alignment = Qt.AlignmentFlag.AlignCenter)
        self.arm_status_label.setStyleSheet("background-color: green;")

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
        missionPanel.addWidget(self.arm_status_label)
        missionPanel.addWidget(arm_button)
        missionPanel.addWidget(disarm_button)
        missionPanel.addWidget(self.connection_status)
        missionPanel.addWidget(connect_button)
        missionPanel.addWidget(disconnect_button)

        # circle_mode_button.clicked.connect(self.setCircleMode)

        arm_button.clicked.connect(self.arm_boat_handler)
        disarm_button.clicked.connect(self.disarm_boat_handler)

        connect_button.clicked.connect(self.start_connection_handler)
        disconnect_button.clicked.connect(self.close_connection_handler)

        # Create a timer for updating telemetry
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry_data)
        self.timer.start(200)

        # Create a slower timer for updating map
        self.slowTimer = QTimer()
        self.slowTimer.timeout.connect(self.updateMapMarker)
        self.slowTimer.start(1000)

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

        print (telemetry_data_row_list)
    
    def update_telemetry_data(self):

        current_msg = get_desired_messages(self.the_connection)
        
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

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())