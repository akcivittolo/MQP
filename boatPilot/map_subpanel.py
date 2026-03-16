from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel
)

from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium

class MapSubpanel(QWidget):
    def __init__(self, telem_data):
        super().__init__()
            
        self.telem_data = telem_data

        # Create a layout
        layout = QVBoxLayout(self)

        # Create the map
        indianLakeCords = [42.293377, -71.816133]
        self.map = folium.Map(
            location = indianLakeCords,
            tiles = "Esri.WorldImagery",
            zoom_start = 17
        )
        self.map.save("map.html")
        self.map_view = QWebEngineView()
        self.map_view.setHtml(self.map.get_root().render())

        # Add map widget to layout
        layout.addWidget(self.map_view)
