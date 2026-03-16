from pymavlink import mavutil
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class Connection(QObject):
    # Connection status signal
    connection_status_signal = pyqtSignal(bool)
    arm_status_signal = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.master_connection = None

    def start_connection(self, address = "udp:127.0.0.1:14550"):
        if self.master_connection == None:
            print("Connecting...")
            self.master_connection = mavutil.mavlink_connection(address)

            # Prevent crash if connection fails
            hb_check = self.master_connection.wait_heartbeat(timeout = 5)

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

        print(msg.command)
        print(msg.result)

        if (msg.result != 0):

            print(f"Command failed with code {msg.result}")
            return msg.result
        
        return 0





