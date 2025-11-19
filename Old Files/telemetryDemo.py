from pymavlink import mavutil

# Use the WSL IP
WSL_IP = "172.21.103.161"

# Start a connection listening on a UDP port
the_connection = mavutil.mavlink_connection(f'tcp:{WSL_IP}:5760')

# Wait for the first heartbeat
#   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

# Once connected, use 'the_connection' to get and send messages

while True:
    msg = the_connection.recv_match(blocking=True)
    
    print(msg)