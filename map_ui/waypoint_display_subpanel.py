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
    QHeaderView
)

from PyQt6.QtCore import Qt

class WaypointDisplaySubpanel(QWidget):
    def __init__(self, mission_data):
        super().__init__()

        self.mission_data = mission_data

        # Connect telem data available signal to UI updater
        self.mission_data.mission_data_update.connect(self.update_UI)
        self.mission_data.reset_mission_data.connect(self.reset_waypoints)

        # Create a main layout
        main_layout = QVBoxLayout(self)

        # # Create a button layout
        # button_layout_widget = QWidget()
        # button_layout = QHBoxLayout(button_layout_widget)

        # # Title and message 
        # self.title = QLabel("Mission Planning")

        # # Log View
        # self.log_view = QPlainTextEdit()
        # self.log_view.setReadOnly(True)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Waypoint #","Latitude","Longitude","Status"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Make the columns stretch
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.table)

    def reset_waypoints(self):
        self.table.setRowCount(0)
    

    def update_UI(self):
        number_of_waypoints = len(self.mission_data.waypoints_list)
        waypoint_to_display = self.mission_data.waypoints_list[number_of_waypoints - 1]
        lat = waypoint_to_display[0]
        lon = waypoint_to_display[1]

        self.table.setRowCount(number_of_waypoints)

        self.table.setItem(number_of_waypoints - 1, 0, QTableWidgetItem(str(number_of_waypoints)))
        self.table.setItem(number_of_waypoints - 1, 1, QTableWidgetItem(str(lat)))
        self.table.setItem(number_of_waypoints - 1, 2, QTableWidgetItem(str(lon)))
        self.table.setItem(number_of_waypoints - 1, 3, QTableWidgetItem("Placeholder"))

        self.table.scrollToItem(self.table.item(number_of_waypoints - 1, 0))



