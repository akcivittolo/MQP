from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel
)

from PyQt6.QtCore import Qt

class ConnectionSubpanel(QWidget):
    def __init__(self, the_boat):
        super().__init__()

        self.the_boat = the_boat

        # Connect connection signal to UI updater
        self.the_boat.connection_status_signal.connect(self.update_connection_UI)

        # Create a layout
        layout = QVBoxLayout(self)

        # Connection status and connect button
        self.connection_status = QLabel("No Connection", alignment = Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("background-color: red;")
        self.connect_button = QPushButton("Connect")
        self.connect_button.setCheckable(True)
        self.connect_button.setChecked(False) 

        # Add content to layout
        layout.addWidget(self.connection_status)
        layout.addWidget(self.connect_button)

        # Button connections
        self.connect_button.clicked.connect(self.handle_connect_button)

    def handle_connect_button(self):
        if self.connect_button.isChecked() == True:
            self.the_boat.start_connection()
        else:
            self.the_boat.close_connection()

    def update_connection_UI(self, connection_status):
        if connection_status == True:
            self.connect_button.setText("Disconnect")
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("background-color: green;")
        else:
            self.connect_button.setText("Connect")
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("background-color: red;")



