from pymavlink import mavutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class MissionData(QObject):
    # Mission Data Signals
    mission_data_update = pyqtSignal()
    reset_mission_data = pyqtSignal()

    def __init__(self, the_boat):
        super().__init__()

        self.the_boat = the_boat

        self.waypoints_list = []
        self.mission_planning_status = False

    def add_waypoints(self, lat, lon):
        if self.mission_planning_status == True:
            self.waypoints_list.append((lat, lon))
            print(f"Our current list of waypoints is: {self.waypoints_list}")

            self.mission_data_update.emit()
        else:
            pass

    def clear_waypoints(self):
        self.waypoints_list = []

        self.reset_mission_data.emit()

    def set_waypoints(self):
        self.the_boat.set_waypoints(self.waypoints_list)