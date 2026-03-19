from pymavlink import mavutil
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class Connection(QObject):
    # Connection status signal
    connection_status_signal = pyqtSignal(bool)
    arm_status_signal = pyqtSignal(bool)

    rover_custom_modes = [
    "Manual",
    "Acro",
    None,
    "Steering",
    "Hold",
    "Loiter",
    "Follow",
    "Simple",
    "Dock",
    "Circle",
    "Auto",
    "RTL",
    "SmartRTL",
    None,
    None,
    "Guided",
    "Initializing"
    ]
    
    def __init__(self):
        super().__init__()
        self.master_connection = None

        # Timer for continous RC overide
        self.timer = QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.set_RC_channel_out)

        # RC inputs
        self.pitch = 1500
        self.roll = 1500
        self.throttle = 1500
        self.yaw = 1500

    def start_connection(self, address = "udp:127.0.0.1:14550"):
        if self.master_connection == None:
            print(f"Connecting to {address}...")
            self.master_connection = mavutil.mavlink_connection(address, baud=57600)

            # Prevent crash if connection fails
            hb_check = self.master_connection.wait_heartbeat(timeout = 10)

            if hb_check != None:
                print("Connected")
                self.connection_status_signal.emit(True)
                return True
            else:
                print("Connection failed")
                self.master_connection.close()
                self.master_connection = None
                self.connection_status_signal.emit(False)

                self.arm_status_signal.emit(False)
                return False
        else:
            print("Connection already exists")

    def close_connection(self):
        if self.master_connection != None:
            print("Disarming...")
            self.disarm_command()
            
            print("Disconnecting...")
            self.master_connection.close()
            self.master_connection = None
            self.connection_status_signal.emit(False)

            print("Disconnected")
        else:
            print("No Connection")
    
    def arm_command(self):

        if self.master_connection == None:
            print("There is no connection available")
            return None
        
        self.master_connection.mav.command_long_send(
            self.master_connection.target_system,
            self.master_connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, # Message confirmation
            1, # 0 disarm, 1 arm
            1, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
            0,0,0,0,0
        )

        self.acknowledge_command()
        self.get_arm_status()

    def disarm_command(self):

        if self.master_connection == None:
            print("There is no connection available")
            return None
        
        self.master_connection.mav.command_long_send(
            self.master_connection.target_system,
            self.master_connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, # Message confirmation
            0, # 0 disarm, 1 arm
            0, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
            0,0,0,0,0
        )

        self.acknowledge_command()
        self.get_arm_status()

    def get_arm_status(self):
        msg = self.master_connection.recv_match(type="HEARTBEAT", blocking=True)

        if (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
            self.arm_status_signal.emit(True)
        else:
            self.arm_status_signal.emit(False)

    def acknowledge_command(self):
        msg = self.master_connection.recv_match(type='COMMAND_ACK', blocking=True)

        if (msg.result != 0):

            print(f"Command failed with code {msg.result}")
            return msg.result
        else:
            print("Command accepted")
        
        return 0
    
    def change_mode(self, chosen_mode):
        modeid = self.rover_custom_modes.index(chosen_mode)
        self.master_connection.set_mode(modeid)
        self.acknowledge_command()

    def set_waypoints(self, waypoints_list):
        pass
        for seq, (lat, lon) in enumerate(waypoints_list):
            self.master_connection.mav.mission_item_int_send(
            self.master_connection.target_system,
            self.master_connection.target_component,
            seq,  # sequence number
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            2,  # current (0 = not current, 2 = first item to execute?)
            1,  # autocontinue
            0, 0, 0, 0,  # params 1-4 (hold time, acceptance radius, etc.)
            int(lat * 1e7),
            int(lon * 1e7),
            0
        )
            
    def set_RC_channel_out(self): 
        # Send RC override
        self.master_connection.mav.rc_channels_override_send(
            self.master_connection.target_system,
            self.master_connection.target_component,
            self.roll,  # CH1 Roll neutral
            self.pitch,  # CH2 Pitch neutral
            self.throttle,  # CH3 Throttle neutral
            self.yaw,  # CH4 Yaw neutral
            0, 0, 0, 0  # CH5-8 not overridden
        )





