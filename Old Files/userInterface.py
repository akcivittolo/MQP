from pymavlink import mavutil

from connectionFunctions import *

# Device ID to connect to
DEVICE = "tcp:172.21.103.161:5760"

# Establish connection to the device
mav_connection = startConnection(DEVICE)

# Define a list of message types we want to have
message_types_desired = ['GLOBAL_POSITION_INT',
                         'HEARTBEAT',
                         'GPS_RAW_INT',
                         'LOCAL_POSITION_NED', 
                         'ATTITUDE'
                         'MISSION_ITEM',
                         'MISSION_CURRENT']
while True:
    
    # Wait for a specific message type
    for message_type in message_types_desired:
        msg = mav_connection.recv_match(type = message_type, blocking=True)
        print(msg)