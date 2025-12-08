from pymavlink import mavutil

# Create a mavlink connection and return it
def start_connection(current_connection):

    if current_connection != None:
        print("Connection already exists")
        return current_connection
 
    the_connection = mavutil.mavlink_connection("tcp:172.21.103.161:5760")
    the_connection.wait_heartbeat()
    
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

# Send an arm command
def arm_command(the_connection):

        if the_connection ==None:
            print("There is no connection available")
            return None
        
        the_connection.mav.command_long_send(
            master_connection.target_system,
            master_connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, # Message confirmation
            1, # 0 disarm, 1 arm
            0, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
            0,0,0,0,0
        )

        msg = master_connection.recv_match(type='COMMAND_ACK', blocking=True)
        if msg.result == 0:
            print("Boat armed")
            arm_status = True
        else:
            print("Arm failed")
            arm_status = False

# Send a disarm command
def disarm_command(self):
        global master_connection
        global arm_status

        if master_connection!=None:
            master_connection.mav.command_long_send(
                master_connection.target_system,
                master_connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, # Message confirmation
                0, # 0 disarm, 1 arm
                0, # 0 allow safety checks to prevent arm/disarm, 1 force the arm/disarm
                0,0,0,0,0
            )

            msg = master_connection.recv_match(type='COMMAND_ACK', blocking=True)
            if msg.result == 0:
                print("Boat disarmed")
                arm_status = False
            else:
                print("Disarm failed")
                arm_status = False
        else:
            print("No connection available")
            return None
        
def setCircleMode(self):
        global master_connection

        if master_connection is None:
            print("No connection available")
            return

        # Make sure the boat is armed
        if not arm_status:
            print("Boat must be armed first!")
            return

         # Ensure GUIDED mode
        guided_mode = master_connection.mode_mapping()['GUIDED']
        master_connection.set_mode(guided_mode)

        lat = 100
        lon = 100
        alt = 0

        # Send the command
        master_connection.mav.set_position_target_global_int_send(
            10,  # time_boot_ms (ignored)
            master_connection.target_system,
            master_connection.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            int(0b110111111000),  # type_mask: only position
            int(lat * 1e7),       # latitude in degE7
            int(lon * 1e7),       # longitude in degE7
            alt,                  # altitude
            0, 0, 0,              # velocity (ignored)
            0, 0, 0,              # acceleration (ignored)
            0, 0                  # yaw, yaw_rate
        )

        print(f"Heading to point ({lat},{lon},{alt})")