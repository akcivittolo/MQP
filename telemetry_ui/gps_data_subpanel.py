from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QHBoxLayout,
    QGridLayout
)

from PyQt6.QtCore import Qt

from toolbar_statusbar_ui.statuslight import StatusLight

class GPSSubpanel(QGroupBox):
    def __init__(self, the_boat, telem_data):
        super().__init__("GPS Data")

        self.the_boat = the_boat
        self.telem_data = telem_data

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        main_layout = QVBoxLayout(self)

        # Optional: if you want a title for the panel
        # title = QLabel("GPS Data")
        # title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # main_layout.addWidget(title)

        # Grid layout for all the rows
        grid_layout = QGridLayout()

        # Row 0: Coordinates
        self.lat_title = QLabel("Latitude: ")
        self.lat_info = QLabel("Unavailable")
        self.lat_status_light = StatusLight("yellow")
        grid_layout.addWidget(self.lat_title, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.lat_info, 0, 1)
        grid_layout.addWidget(self.lat_status_light, 0, 2)

        # Row 1: Coordinates
        self.lon_title = QLabel("Longitude: ")
        self.lon_info = QLabel("Unavailable")
        self.lon_status_light = StatusLight("yellow")
        grid_layout.addWidget(self.lon_title, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.lon_info, 1, 1)
        grid_layout.addWidget(self.lon_status_light, 1, 2)

        # Row 2: Satellites
        self.satellites_title = QLabel("Satellites Visible: ")
        self.satellites_info = QLabel("Unavailable")
        self.sat_status_light = StatusLight("yellow")
        grid_layout.addWidget(self.satellites_title, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.satellites_info, 2, 1)
        grid_layout.addWidget(self.sat_status_light, 2, 2)

        # Row 3: HDOP
        self.hdop_title = QLabel("HDOP: ")
        self.hdop_info = QLabel("Unavailable")
        self.hdop_status_light = StatusLight("yellow")
        grid_layout.addWidget(self.hdop_title, 3, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.hdop_info, 3, 1)
        grid_layout.addWidget(self.hdop_status_light, 3, 2)

        # Row 4: VDOP
        self.vdop_title = QLabel("VDOP: ")
        self.vdop_info = QLabel("Unavailable")
        self.vdop_status_light = StatusLight("yellow")
        grid_layout.addWidget(self.vdop_title, 4, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.vdop_info, 4, 1)
        grid_layout.addWidget(self.vdop_status_light, 4, 2)

        # Add the grid layout to the main vertical layout
        main_layout.addLayout(grid_layout)
        
            
    def handle_connection(self, connection_status):
        if connection_status == True:
           self.lat_status_light.setColor("green")
           self.lon_status_light.setColor("green")
           self.sat_status_light.setColor("green")
           self.hdop_status_light.setColor("green")
           self.vdop_status_light.setColor("green")
        else:
            self.satellites_info.setText("Unavailable")
            self.lat_info.setText("Unavailable")
            self.lon_info.setText("Unavailable")
            self.hdop_info.setText("Unavailable")
            self.vdop_info.setText("Unavailable")

            self.lat_status_light.setColor("yellow")
            self.lon_status_light.setColor("yellow")
            self.sat_status_light.setColor("yellow")
            self.hdop_status_light.setColor("yellow")
            self.vdop_status_light.setColor("yellow")
          
    
    def update_UI(self):
        lat = self.telem_data.telemetry_data["GLOBAL_POSITION_INT"]["lat"]
        lon = self.telem_data.telemetry_data["GLOBAL_POSITION_INT"]["lon"]
        sat_num = self.telem_data.telemetry_data["GPS_RAW_INT"]["satellites_visible"]
        hdop = self.telem_data.telemetry_data["GPS_RAW_INT"]["eph"]
        vdop = self.telem_data.telemetry_data["GPS_RAW_INT"]["epv"]

        if lat != None and lon != None:
            lat = lat / 1e7
            lon = lon / 1e7

        if hdop != None and vdop != None:
            hdop = hdop / 100
            vdop = vdop / 100
        
        self.lat_info.setText(str(lat))
        self.lon_info.setText(str(lon))
        self.satellites_info.setText(str(sat_num))

        self.hdop_info.setText(str(hdop))
        self.vdop_info.setText(str(vdop))


