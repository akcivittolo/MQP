from pymavlink import mavutil
import math

rover_custom_modes = [
    "Manual",
    "Acro",
    "Learning",
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
    "Guided",
    "Initializing"
]

# Acknowledgement command to see if a command is successful or not
def acknowledge_command(the_connection):
    msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)

    print(msg.command)
    print(msg.result)

    if (msg.result != 0):

        print(f"Command failed with code {msg.result}")
        return msg.result
    
    return 0

# Create a mavlink connection and return it
def start_connection(current_connection):

    if current_connection != None:
        print("Connection already exists")
        return current_connection
    
    # # Simulation Connection
    # the_connection = mavutil.mavlink_connection("tcp:172.21.103.161:5760")

    # # USB Connection
    # the_connection = mavutil.mavlink_connection("COM8", baud=57600)

    # PI, UART Connection
    the_connection = mavutil.mavlink_connection("/dev/ttyAMA0", baud=57600)

    the_connection.wait_heartbeat()
    
    if the_connection is None:
        print("Connection failed")
        return None
    else:
        print("Connection successful")
        return the_connection
    
# Change Mode
def change_mode(the_connection, chosen_mode):
    available_modes = the_connection.mode_mapping()
    if the_connection == None:
        print("There is no connection available. Cannot get current mode")
        return None
    
    modeid = rover_custom_modes.index(chosen_mode)
    the_connection.set_mode(modeid)

    if acknowledge_command(the_connection) != 0:
        print(f"The mode change failed to {chosen_mode}")
        return 1

    print(f'We have changed the mode to {chosen_mode}')
    
the_connection = None
the_connection = start_connection(the_connection)

while True:
    msg = the_connection.recv_match(type='ATTITUDE', blocking=True)
    if msg:
        roll_deg = math.degrees(msg.roll)
        pitch_deg = math.degrees(msg.pitch)

        print(f"Roll: {roll_deg:.2f}  Pitch: {pitch_deg:.2f}")

        if pitch_deg > 30:
            change_mode(the_connection, "Manual")
        else:
            change_mode(the_connection,"Hold")
    
        
