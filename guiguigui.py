import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium

# Import your telemetry from your existing file
from dataDesired import ordered_messages, master_connection

class TelemetryMapGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASV Telemetry & Map GUI")
        self.setGeometry(100, 100, 1400, 700)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Telemetry Table ---
        self.table = QTableWidget()
        self.max_fields = max(len(msg['fields']) for msg in ordered_messages)
        self.table.setRowCount(len(ordered_messages))
        self.table.setColumnCount(1 + self.max_fields)  # Message name + fields

        # Header: use the message with the most fields
        for msg in ordered_messages:
            if len(msg['fields']) == self.max_fields:
                header_labels = ["Message"] + msg['fields']
                break
        self.table.setHorizontalHeaderLabels(header_labels)

        # Fill message names
        for i, msg in enumerate(ordered_messages):
            self.table.setItem(i, 0, QTableWidgetItem(msg['name']))

        # --- Map Widget ---
        self.map_view = QWebEngineView()
        self.default_lat, self.default_lon = 42.3601, -71.0589  # fallback location
        self.last_lat, self.last_lon = None, None

        # Initial map
        self.map = folium.Map(location=[self.default_lat, self.default_lon], zoom_start=17)
        folium.Marker([self.default_lat, self.default_lon], tooltip="ASV").add_to(self.map)
        self.map_view.setHtml(self.map._repr_html_())

        # Add widgets to layout
        main_layout.addWidget(self.table, 2)
        main_layout.addWidget(self.map_view, 3)

        # Timer for updating telemetry & map
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(500)  # update 2x/sec

    def update_telemetry(self):
        # Read all new MAVLink messages (non-blocking)
        while True:
            msg = master_connection.recv_match(blocking=False)
            if not msg:
                break
            msg_type = msg.get_type()
            for msg_dict in ordered_messages:
                if msg_dict['name'] == msg_type:
                    msg_dict['field_values'] = {f: getattr(msg, f, None) for f in msg_dict['fields']}
                    break

        # Update telemetry table
        for row, msg_dict in enumerate(ordered_messages):
            for col, field_name in enumerate(msg_dict['fields']):
                value = msg_dict.get('field_values', {}).get(field_name, "")
                self.table.setItem(row, col + 1, QTableWidgetItem(str(value)))

        # Update map if we have GPS telemetry
        gps_msg = next((m for m in ordered_messages if m['name'] == "GLOBAL_POSITION_INT"), None)
        if gps_msg and 'lat' in gps_msg.get('field_values', {}) and 'lon' in gps_msg.get('field_values', {}):
            lat = gps_msg['field_values']['lat'] / 1e7
            lon = gps_msg['field_values']['lon'] / 1e7
            if lat != self.last_lat or lon != self.last_lon:
                self.last_lat, self.last_lon = lat, lon
                # Re-create map in memory
                self.map = folium.Map(location=[lat, lon], zoom_start=17)
                folium.Marker([lat, lon], tooltip="ASV").add_to(self.map)
                self.map_view.setHtml(self.map._repr_html_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelemetryMapGUI()
    window.show()
    sys.exit(app.exec())
