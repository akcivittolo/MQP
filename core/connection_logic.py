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

    connection_targets = [
        "udp:127.0.0.1:14550",
        "/dev/ttyUSB0",
        "com14",
        "com8"
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

    def clear_mission_data(self):
        # Assuming master_connection is your mavlink connection object
        # Send the clear mission command
        self.master_connection.mav.mission_clear_all_send(
            self.master_connection.target_system,
            self.master_connection.target_component
        )
        
        # Wait for acknowledgement from the flight controller
        msg = self.master_connection.recv_match(type='MISSION_ACK', blocking=True)
        print("Mission cleared:", msg)
    

    def set_waypoints(self, waypoints_list):

        temp_list = waypoints_list

        temp_list.insert(0,(0,0)) # Add a dummy

        self.clear_mission_data()

        num_waypoints = len(temp_list)
        print(num_waypoints)
        # First - Send the number of waypoints in the mission
        self.master_connection.mav.mission_count_send(self.master_connection.target_system, 
                                                      self.master_connection.target_component, 
                                                      num_waypoints)
        
        # Second - Wait for Pixhawk to request each item
        seq = 0
        while seq < num_waypoints:
            msg = self.master_connection.recv_match(type=['MISSION_REQUEST'], blocking=True)
            if not msg:
                continue
            if msg.seq != seq:
                print(f"Unexpected sequence {msg.seq}, expected {seq}")
                continue

            lat, lon = temp_list[seq]

            self.master_connection.mav.mission_item_int_send(
                self.master_connection.target_system,
                self.master_connection.target_component,
                seq,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                0,  # current (0 = not current waypoint, 1 = first item to execute)
                1,  # autocontinue
                0, 3, 0, 0,  # params 1-4 # 2 is 2 meters of radius
                int(lat * 1e7),
                int(lon * 1e7),
                0  # We dont care about altitude
            )

            seq += 1
        print(seq)
        print("MISSION SENT AND RECEIVED")
      
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

    def get_available_logs(self):
        # Request logs
        self.master_connection.mav.log_request_list_send(
            target_system = self.master_connection.target_system,
            target_component = self.master_connection.target_component,
            start = 0,
            end = 0xFFFF
        )

        logs = []

        while True:
            msg = self.master_connection.recv_match(type='LOG_ENTRY', blocking=True, timeout=5)
            if msg is None:
                break

            logs.append(msg)
            print(f"Log {msg.id}: size={msg.size} bytes")

        print(f"Found {len(logs)} logs")




