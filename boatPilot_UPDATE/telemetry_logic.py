from pymavlink import mavutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class TelemetryData(QObject):
    # Telemetry Data Signals
    telem_data_update = pyqtSignal()

    def __init__(self, the_boat):
        super().__init__()
        self.telemetry_data = {
            "BATTERY_STATUS": {
                "battery_remaining": None
            },
            "ATTITUDE": {
                "roll": None,
                "pitch": None,
                "yaw": None
            },
            "GLOBAL_POSITION_INT": {
                "lat": None,
                "lon": None,
                "alt": None,
                "hdg": None
            },
            "GPS_RAW_INT": {
                "vel": None
            },
            "HEARTBEAT": {
                "custom_mode": None
            },
            "STATUSTEXT": {
                "severity": None,
                "text": None
            },
            "SERVO_OUTPUT_RAW": {
                "servo1_raw": None,
                "servo3_raw": None
            }
        }

        # Used for telemetry data updates
        self.message_types = list(self.telemetry_data.keys())
        self.message_type_index = 0

        self.the_boat = the_boat

        self.timer = QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update_telemetry_data)
        self.timer.timeout.connect(self.the_boat.get_arm_status)

        # Connect connection status signal
        self.the_boat.connection_status_signal.connect(self.request_messages)

    def request_messages(self, connection_status):
        if connection_status == True:
            for message_type in self.telemetry_data:
                # Peforme getattr() for a numerical value
                msg_name= "MAVLINK_MSG_ID_" + message_type
                msg_id = getattr(mavutil.mavlink, msg_name)

                self.the_boat.master_connection.mav.command_long_send(
                    self.the_boat.master_connection.target_system,
                    self.the_boat.master_connection.target_component,
                    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                    0,
                    msg_id,
                    100000,
                    0,0,0,0,0
                )

                print(f"Added {msg_name} to comms")

            # Begin updating telemetry data
            self.timer.start()
            
        else:
            # Stop updating telemetry data
            print("Timer stopped. No longer updating telemetry data")
            self.timer.stop()

    # def update_telemetry_data(self):
    #     # message_type_wanted = self.message_types[self.message_type_index]
    #     msg = self.the_boat.master_connection.recv_match(blocking=True)
        
    #     if msg != None:
    #         received_message_type = msg.get_type()
    #         print(f"New message received: {received_message_type}")

    #         if received_message_type in self.telemetry_data:
    #             for field in self.telemetry_data[received_message_type]:
    #                 new_value = getattr(msg, field)
    #                 self.telemetry_data[received_message_type][field] = new_value

    #         self.telem_data_update.emit()

    def update_telemetry_data(self): 
        message_type_wanted = self.message_types[self.message_type_index]
        status_msg = self.the_boat.master_connection.recv_match(type = "STATUSTEXT", blocking=False) 

        if status_msg is not None:
            self.telemetry_data["STATUSTEXT"]["severity"] = status_msg.severity
            self.telemetry_data["STATUSTEXT"]["text"] = status_msg.text

            print(f"STATUSTEXT RECEIVED: {status_msg.text}")  # debug

            self.telem_data_update.emit()

        msg = self.the_boat.master_connection.messages.get(message_type_wanted)


        if msg != None: 
        
            for field in self.telemetry_data[message_type_wanted]: 
                new_value = getattr(msg, field) 
                self.telemetry_data[message_type_wanted][field] = new_value 
            
            self.telem_data_update.emit()

        else:
            pass

        self.message_type_index += 1 
        
        if self.message_type_index == len(self.message_types): 
            self.message_type_index = 0
    

            



    





        


