from pymavlink import mavutil

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
    
    # Simulation Connection
    # the_connection = mavutil.mavlink_connection("tcp:172.21.103.161:5760")

    # USB Connection
    # the_connection = mavutil.mavlink_connection("COM8", baud=57600)

    the_connection = mavutil.mavlink_connection("udp:127.0.0.1:14550")

    the_connection.wait_heartbeat(timeout = 5)
    
    if the_connection is None:
        print("Connection failed")
        return None
    else:
        print("Connection successful")
        return the_connection
    
# Close the mavlink connection
def close_connection(the_connection):
    if the_connection is None:
        print("No Connection")
    else:
        the_connection.close()
        print("Connection closed")

# Get the current arm status of the boat
def get_arm_status(the_connection):

    if the_connection != None:
        msg = the_connection.recv_match(type='HEARTBEAT', blocking=True)
    else:
        msg = None

    if msg == None:
        return None
    
    print(msg.base_mode)
    print(mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)

    if (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
        print("The boat is armed")
        return 1
    else:
        print("The boat is unarmed")
        return 0

# Send an arm command
def arm_command(the_connection):

    if the_connection ==None:
        print("There is no connection available")
        return None
    
    the_connection.mav.command_long_send(
        the_connection.target_system,
        the_connection.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, # Message confirmation
        1, # 0 disarm, 1 arm
        1, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
        0,0,0,0,0
    )
           

# Send a disarm command
def disarm_command(the_connection):

    if the_connection ==None:
        print("There is no connection available")
        return None
    
    the_connection.mav.command_long_send(
        the_connection.target_system,
        the_connection.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, # Message confirmation
        0, # 0 disarm, 1 arm
        0, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
        0,0,0,0,0
    )

rover_custom_modes = [
        "Manual",
        "Acro",
        "NA",
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
        "Guided"
]
# Get the current mode of the boat
def get_current_mode(the_connection):
    if the_connection == None:
        print("There is no connection available. Cannot get current mode")
        return None
    
    msg = the_connection.recv_match(type='HEARTBEAT', blocking=True)

    if msg == None:
        pass
    else:
    
        current_mode = rover_custom_modes[msg.custom_mode]

        return current_mode

# Change the mode to circle mode
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

# Set mission
def set_mission(the_connection, waypoints_list):
    if the_connection == None:
        return None
    
    # First remove any prior existing mission
    the_connection.mav.mission_clear_all_send(the_connection.target_system, the_connection.target_component)

    # Send over how many waypoints there are
    total_waypoints = len(waypoints_list)
    the_connection.mav.mission_count_send(the_connection.target_system, the_connection.target_component, total_waypoints)

    #Send over the waypoints
    for seq_value, waypoint in enumerate(waypoints_list):
        print(f"Adding {waypoint}")
        send_waypoint(the_connection, waypoint, seq_value)

def send_waypoint(the_connection, waypoint, seq_value):
    lat = waypoint[0]
    lon = waypoint[1]
    alt = 0  # in meters
    seq = seq_value
    frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
    command = mavutil.mavlink.MAV_CMD_NAV_WAYPOINT

    if seq == 0:
        current = 1
    else:
        current = 0
    autocontinue = 1
    param1 = 0  # hold time
    param2 = 10  # acceptance radius
    param3 = 0  # pass radius
    param4 = 0  # yaw`

    the_connection.mav.mission_item_send(
        the_connection.target_system,
        the_connection.target_component,
        seq,
        frame,
        command,
        current,
        autocontinue,
        param1,
        param2,
        param3,
        param4,
        lat,
        lon,
        alt
    )

    print(f"Waypoint {waypoint} added to mission")







