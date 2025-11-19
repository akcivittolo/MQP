from pymavlink import mavutil

def startConnection(device):  
    mav_connection = mavutil.mavlink_connection(f'{device}')
    mav_connection.wait_heartbeat()

    if mav_connection is None:
        print("Connection failed")
        return None
    else:
        print("Connection successful")
        return mav_connection
        
def closeConnection(mav_connection):
    if mav_connection is None:
        print("No Connection")
    else:
        mav_connection.close()
        print("Connection closed")