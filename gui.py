from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QTimer
from listen import startConnection, closeConnection, getTelemetry, the_connection
import sys

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("My GCS")
window.resize(400, 600)
layout = QVBoxLayout()
window.setLayout(layout)

# Status label
status_label = QLabel("Status: Disconnected")
layout.addWidget(status_label)

# Telemetry label
telemetry_label = QLabel("Telemetry: ---")
layout.addWidget(telemetry_label)

# Function to update telemetry continuously
def update_telemetry():
    if the_connection is not None:
        data = getTelemetry()
        if data:
            telemetry_label.setText(str(data))
            print("Hello")
    else:
        telemetry_label.setText("Telemetry: ---")  # clear if disconnected

# Handler for Connect button
def handle_connect():
    status = startConnection()
    if status == 1:
        status_label.setText("Status: Connected")
    else:
        status_label.setText("Status: Already connected or failed")

# Handler for Disconnect button
def handle_disconnect():
    status = closeConnection()
    if status == 1:
        status_label.setText("Status: Disconnected")
        telemetry_label.setText("Telemetry: ---")  # clear display
    else:
        status_label.setText("Status: No active connection")

# Connect / Disconnect buttons
connect_button = QPushButton("Connect")
connect_button.clicked.connect(handle_connect)
layout.addWidget(connect_button)

disconnect_button = QPushButton("Disconnect")
disconnect_button.clicked.connect(handle_disconnect)
layout.addWidget(disconnect_button)



window.show()
app.exec()
