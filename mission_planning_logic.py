from pymavlink import mavutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import coverage_path_planner as cpp

class MissionData(QObject):
    # Mission Data Signals
    mission_data_update = pyqtSignal()
    reset_mission_data = pyqtSignal()

    def __init__(self, the_boat):
        super().__init__()

        self.the_boat = the_boat

        self.waypoints_list = []
        self.mission_planning_status = False
        self.mission_types = ["Point to Point","Lawnmower"]
        self.current_mission_type = self.mission_types[0]

        self.cpp_list = []
        self.lawnmower_list = []

        self.enough_waypoints_flag = False

    def change_mission_type(self, chosen_type):
        # Change mission type
        self.current_mission_type = str(chosen_type)
        print(f"Current mission type is changed and is now {self.current_mission_type}")

        # Reset other information
        self.clear_waypoints()

    def add_waypoints(self, lat, lon):
        if self.mission_planning_status == True:
            self.waypoints_list.append((lat, lon))

            self.mission_data_update.emit()

            if len(self.waypoints_list) >= 3:
                self.enough_waypoints_flag = True
            else:
                self.enough_waypoints_flag = False
        else:
            print("Mission planning status is down")
            pass

    def clear_waypoints(self):
        self.waypoints_list = []

        self.cpp_list = []

        self.reset_mission_data.emit()

        self.enough_waypoints_flag = False

    def set_waypoints(self):
        self.the_boat.set_waypoints(self.waypoints_list)

    def get_lawnmower_waypoints(self):
        self.cpp_list = []
        # Convert our list of waypoints into something that coverage path planner will accept
        for waypoint in self.waypoints_list:
            lat = waypoint[0]
            lon = waypoint[1]

            cpp_waypoint = cpp.Point(lat, lon)

            self.cpp_list.append(cpp_waypoint)
            

        # Create perimeter polygon and create environment 
        peri = cpp.Polygon(self.cpp_list)
        env = cpp.Environment(peri)

        # Configure settings
        settings = cpp.PathSettings()
        settings.pattern = "lines"  # possible patterns: lines, squares, rings
        settings.offset = 0.0005     # distance between coverage lines
        settings.angle = 0.5        # coverage angle (RAD)
        settings.distanceToBorder = 0.4   # distance to border
        settings.mowArea = True       # cover area
        settings.mowBorder = False    # calculate border laps (borderLaps must be > 0)
        settings.mowBorderCcw = True  # border laps counter clockwise?
        settings.borderLaps = 2      # how many border laps (every new lap gets offset of settings.offset)
        settings.mowExclusionsBoder = True  # calculate exclusions laps (exclusionsBorderLaps must be > 0)
        settings.mowExclusionsBorderCcw = True  # exclusions laps counter clockwise?
        settings.exclusionsBorderLaps = 2       # how many exclusions laps (every new lap gets offset of settings.offset)

        # Compute path
        service = cpp.PathService()
        result = service.computeFullTask(env, settings, self.cpp_list[0])
        result_list = result.path.getPoints()
        print(result_list)
        print(type(result_list))

        self.lawnmower_list = result_list

        self.show_lawnmower_list()

    def show_lawnmower_list(self):
        self.change_mission_type(self.mission_types[0])

        for waypoint in self.lawnmower_list:
            self.add_waypoints(waypoint.x, waypoint.y)
            print(f"Adding waypoint {waypoint.x},{waypoint.y}")
