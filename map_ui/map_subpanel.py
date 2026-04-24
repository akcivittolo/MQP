from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout
)
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
import folium
import os
import base64
import json

class MapSubpanel(QWidget):
    def __init__(self, telem_data, mission_data):
        super().__init__()
            
        self.telem_data = telem_data
        self.mission_data = mission_data

        # Connect telem data update signal to map update functions
        self.telem_data.telem_data_update.connect(self.update_map_marker)
        
        # Connect mission data update signal to waypoint marker functions
        self.mission_data.mission_data_update.connect(self.add_marker_to_map)
        self.mission_data.reset_mission_data.connect(self.reset_waypoint_markers)

        # Create a layout
        layout = QVBoxLayout(self)

        # Create the map
        indianLakeCords = [42.293377, -71.816133]
        self.map = folium.Map(
            location = indianLakeCords,
            tiles = "Cartodb Positron",
            zoom_start = 17
        )

        # Add necessary js to the HTML file
        self.add_dependencies()

        # Connect javascript for live updates
        with open("map_ui/map_update.js") as f:
            js_code = f.read()  
        self.map.get_root().html.add_child(folium.Element(f"<script>{js_code}</script>"))

        # Create the map as an HTML file
        self.map.save("map_ui/map.html")
        self.map_view = QWebEngineView()
        self.map_view.setHtml(self.map.get_root().render())

        # Create the marker after the HTML finishes loading
        self.map_view.loadFinished.connect(self.init_marker_handler)

        # Setup the channel that allows data to pass from the HTML map to the main program
        self.channel = QWebChannel()
        self.map_handler = MapHandler(self.mission_data)
        self.channel.registerObject("pyHandler", self.map_handler)
        self.map_view.page().setWebChannel(self.channel)

        # Add map widget to layout
        layout.addWidget(self.map_view)

    def add_marker_to_map(self):
        mission_type = str(self.mission_data.current_mission_type)
        number_of_waypoints = len(self.mission_data.waypoints_list)
        waypoint_to_display = self.mission_data.waypoints_list[number_of_waypoints - 1]

        lat = waypoint_to_display[0]
        lon = waypoint_to_display[1]

        self.map_view.page().runJavaScript(f"addWaypoint({json.dumps(mission_type)}, {lat}, {lon}, {number_of_waypoints});")

    def reset_waypoint_markers(self):
        self.map_view.page().runJavaScript("clearWaypoints();")

    def add_dependencies(self):

        # Allows the marker image to get accessed
        with open("assets/marker.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        self.map.get_root().html.add_child(
            folium.Element(f"""
            <script>
                var markerIconPath = "data:image/png;base64,{encoded}";
            </script>
            """)
        )

        # Allows the marker to be rotated
        self.map.get_root().html.add_child(
            folium.Element("""
                <script src="https://rawcdn.githack.com/bbecquet/Leaflet.RotatedMarker/master/leaflet.rotatedMarker.js"></script>
            """)
        ) 

        # Allows for coords to get passed
        self.map.get_root().html.add_child(
            folium.Element("""
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            """)
        )

    def init_marker_handler(self):
        # Get the map id
        get_initial_map_id = f"getMap()"
        self.map_view.page().runJavaScript(get_initial_map_id)

        init_marker_command = f"initBoatMarker(42.293377, -71.816133)" 
        self.map_view.page().runJavaScript(init_marker_command)

        print("We added the marker")
        

    def update_map_marker(self):
        # Get new values
        raw_lat = self.telem_data.telemetry_data["GLOBAL_POSITION_INT"]["lat"]
        raw_lon = self.telem_data.telemetry_data["GLOBAL_POSITION_INT"]["lon"]
        raw_hdg = self.telem_data.telemetry_data["GLOBAL_POSITION_INT"]["hdg"]

        if raw_lat != None and raw_lon != None and raw_hdg != None:
            # Convert to correct units
            new_lat = raw_lat / 1e7
            new_lon = raw_lon / 1e7
            new_hdg = raw_hdg / 100.0

            # Apply javascript to the HTML map
            update_marker_command = f"updateBoatMarker({new_lat},{new_lon},{new_hdg})"
            self.map_view.page().runJavaScript(update_marker_command)

        else:
            pass

class MapHandler(QObject):
    def __init__(self, mission_data):
        super().__init__()
        self.mission_data = mission_data
        self.last_clicked = None  # optional: store the last click

    @pyqtSlot(float, float)
    def mapClicked(self, lat, lon):
        self.last_clicked = (lat, lon)

        self.mission_data.add_waypoints(lat, lon)

        print(f"Map clicked at: {lat}, {lon}")


