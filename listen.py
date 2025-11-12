from pymavlink import mavutil

# Enter the following code into WSL to start the simulation:
# sim_vehicle.py -v Rover -f motorboat-skid -A "--serial0=tcp:0.0.0.0:5760" --no-mavproxy

# Use the WSL IP
WSL_IP = "172.21.103.161"

# Global variable to store the connection
the_connection = None

# Start a connection listening on a UDP port
def startConnection():
    global the_connection # By stating "global" before the_connection we're referring to the global version
    if the_connection is None:
        the_connection = mavutil.mavlink_connection(f'tcp:{WSL_IP}:5760')
        the_connection.wait_heartbeat()
        print("Connected!")
        return 1
    else:
        print("Already connected")
        return 0

def closeConnection():
    global the_connection
    if the_connection is not None:
        the_connection.close()
        the_connection = None
        print("Disconnected")
        return 1
    else:
        print("No active connection")
        return 0

# Define a dictionary of telemetry messages to track
messages_to_track = {
    "GLOBAL_POSITION_INT": ["lat", "lon", "alt"],
    "ATTITUDE": ["roll", "pitch", "yaw"],
    "SYS_STATUS": ["voltage_battery", "current_battery", "battery_remaining"],
}

# Create a structure to store values for each message included in our dictionary
telemetry = {msg: {field: None for field in fields}
             for msg, fields in messages_to_track.items()}

def getTelemetry():
    global the_connection
    msg = the_connection.recv_match(blocking=False)  # <-- non-blocking
    if msg is None:
        return telemetry  # return the last known telemetry

    msg_type = msg.get_type()
    if msg_type in messages_to_track:
        for field in messages_to_track[msg_type]:
            telemetry[msg_type][field] = getattr(msg, field, None)

    return telemetry

